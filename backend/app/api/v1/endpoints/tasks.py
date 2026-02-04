"""
M7 Logistics - Task Management Endpoints
Task lifecycle, assignment, and verification
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from typing import List
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.db.redis import get_redis, RedisManager
from app.models.models import Task, Volunteer, Donor, NGO, TaskException as TaskExceptionModel
from app.schemas.schemas import (
    TaskCreate, TaskResponse, TaskAcceptance, QRVerification,
    TaskException, ExceptionResponse
)
from app.services.state_machine import state_machine, VolunteerState, TaskState, TransitionError
from app.core.socket_manager import socket_manager
from geoalchemy2.functions import ST_Distance, ST_SetSRID, ST_MakePoint
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/task", tags=["Tasks"])


@router.post("/create", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new task
    Automatically finds nearest available volunteer
    """
    # Create task with PostGIS geometry
    # Remove timezone info to match database TIMESTAMP WITHOUT TIME ZONE
    expiry_time_naive = task_data.expiry_time.replace(tzinfo=None) if task_data.expiry_time.tzinfo else task_data.expiry_time
    
    task = Task(
        donor_id=task_data.donor_id,
        ngo_id=task_data.ngo_id,
        pickup_location=f"SRID=4326;POINT({task_data.pickup_lng} {task_data.pickup_lat})",
        drop_location=f"SRID=4326;POINT({task_data.drop_lng} {task_data.drop_lat})",
        food_type=task_data.food_type,
        expiry_time=expiry_time_naive,
        requires_cooling=task_data.requires_cooling,
        status=TaskState.PENDING
    )
    
    # Calculate distance
    distance_query = text("""
        SELECT ST_Distance(
            ST_SetSRID(ST_MakePoint(:pickup_lng, :pickup_lat), 4326)::geography,
            ST_SetSRID(ST_MakePoint(:drop_lng, :drop_lat), 4326)::geography
        ) / 1000 AS distance_km
    """)
    
    result = await db.execute(
        distance_query,
        {
            "pickup_lng": task_data.pickup_lng,
            "pickup_lat": task_data.pickup_lat,
            "drop_lng": task_data.drop_lng,
            "drop_lat": task_data.drop_lat
        }
    )
    distance = result.scalar()
    task.distance_km = round(distance, 2)
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Find nearest volunteer
    await _assign_nearest_volunteer(task, db)
    
    return task


@router.post("/{task_id}/accept")
async def accept_task(
    task_id: UUID,
    acceptance: TaskAcceptance,
    db: AsyncSession = Depends(get_db)
):
    """
    Volunteer accepts assigned task
    Transitions to NAVIGATING_TO_DONOR
    """
    # Get task and volunteer
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    volunteer_result = await db.execute(
        select(Volunteer).where(Volunteer.id == acceptance.volunteer_id)
    )
    volunteer = volunteer_result.scalar_one_or_none()
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    # Execute state transition
    try:
        transition = state_machine.transition(
            VolunteerState(volunteer.status),
            VolunteerState.NAVIGATING_TO_DONOR,
            {"task_id": str(task_id)}
        )
        
        # Update volunteer and task
        await db.execute(
            update(Volunteer)
            .where(Volunteer.id == acceptance.volunteer_id)
            .values(status=transition["new_state"])
        )
        await db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(status=TaskState.IN_PROGRESS)
        )
        await db.commit()
        
        # Notify donor via WebSocket
        await socket_manager.notify_donor(
            str(task_id),
            "volunteer_assigned",
            {
                "volunteer_name": volunteer.full_name,
                "vehicle_type": volunteer.vehicle_type,
                "eta_minutes": None  # Calculate based on distance
            }
        )
        
        return {
            "status": "success",
            "message": "Task accepted, navigation started"
        }
        
    except TransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{task_id}/verify-pickup")
async def verify_pickup(
    task_id: UUID,
    verification: QRVerification,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify pickup with QR code scan
    Checks against task's pickup_token
    Transitions to PICKUP_VERIFIED then IN_TRANSIT
    """
    # Get task
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify QR token matches task's pickup_token
    if task.pickup_token != verification.qr_token:
        raise HTTPException(status_code=400, detail="Invalid pickup QR code")
    
    # Get volunteer
    volunteer_result = await db.execute(
        select(Volunteer).where(Volunteer.id == task.volunteer_id)
    )
    volunteer = volunteer_result.scalar_one_or_none()
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    try:
        # Update task status directly (no state machine for task states)
        await db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(status=TaskState.PICKED_UP)
        )
        # Update volunteer to PICKUP_VERIFIED
        await db.execute(
            update(Volunteer)
            .where(Volunteer.id == task.volunteer_id)
            .values(status=VolunteerState.PICKUP_VERIFIED)
        )
        await db.commit()
        
        # Broadcast update via WebSocket (optional - can be implemented later)
        # await socket_manager.notify_donor(
        #     str(task_id),
        #     'pickup_verified',
        #     {"status": TaskState.PICKED_UP, "message": "Pickup verified, starting transit to NGO"}
        # )
        
        return {
            "status": "success",
            "message": "Pickup verified, starting transit to NGO",
            "new_task_status": TaskState.PICKED_UP
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{task_id}/verify-dropoff")
async def verify_dropoff(
    task_id: UUID,
    verification: QRVerification,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify dropoff with QR code scan
    Checks against task's delivery_token
    Completes task
    """
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify QR token matches task's delivery_token
    if task.delivery_token != verification.qr_token:
        raise HTTPException(status_code=400, detail="Invalid delivery QR code")
    
    volunteer_result = await db.execute(
        select(Volunteer).where(Volunteer.id == task.volunteer_id)
    )
    volunteer = volunteer_result.scalar_one_or_none()
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    try:
        # Update task status directly to COMPLETED
        from datetime import datetime
        await db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(
                status=TaskState.COMPLETED,
                completed_at=datetime.utcnow()
            )
        )
        # Update volunteer back to ONLINE
        await db.execute(
            update(Volunteer)
            .where(Volunteer.id == task.volunteer_id)
            .values(status=VolunteerState.ONLINE)
        )
        await db.commit()
        
        # Broadcast update (optional - can be implemented later)
        # await socket_manager.notify_donor(
        #     str(task_id),
        #     'delivery_completed',
        #     {"status": TaskState.COMPLETED, "message": "Delivery verified, task completed"}
        # )
        
        return {
            "status": "success",
            "message": "Delivery verified, task completed",
            "new_task_status": TaskState.COMPLETED
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))





@router.post("/{task_id}/exception", response_model=ExceptionResponse)
async def report_exception(
    task_id: UUID,
    exception_data: TaskException,
    db: AsyncSession = Depends(get_db)
):
    """
    Report task exception (vehicle issue, spoilage, etc.)
    Freezes workflow
    """
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    volunteer_result = await db.execute(
        select(Volunteer).where(Volunteer.id == task.volunteer_id)
    )
    volunteer = volunteer_result.scalar_one_or_none()
    
    try:
        # Transition to exception state
        transition = state_machine.transition(
            VolunteerState(volunteer.status),
            VolunteerState.EXCEPTION,
            {"issue_type": exception_data.issue_type}
        )
        
        # Create exception record
        exception = TaskExceptionModel(
            task_id=task_id,
            issue_type=exception_data.issue_type,
            description=exception_data.description
        )
        db.add(exception)
        
        # Update states
        await db.execute(
            update(Volunteer)
            .where(Volunteer.id == task.volunteer_id)
            .values(status=VolunteerState.EXCEPTION)
        )
        await db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(status=TaskState.EXCEPTION)
        )
        await db.commit()
        await db.refresh(exception)
        
        # Alert dispatcher
        await socket_manager.broadcast_exception(
            str(task_id),
            {
                "issue_type": exception_data.issue_type,
                "description": exception_data.description,
                "volunteer_id": str(task.volunteer_id),
                "task_id": str(task_id)
            }
        )
        
        return exception
        
    except TransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pending", response_model=List[TaskResponse])
async def get_pending_tasks(db: AsyncSession = Depends(get_db)):
    """Get all pending tasks (for dispatcher view)"""
    result = await db.execute(
        select(Task)
        .where(Task.status == TaskState.PENDING)
        .order_by(Task.expiry_time.asc())
    )
    tasks = result.scalars().all()
    return tasks


async def _assign_nearest_volunteer(task: Task, db: AsyncSession):
    """
    Find and assign nearest available volunteer
    Uses PostGIS spatial query
    """
    # Extract coordinates from task
    pickup_query = text("""
        SELECT 
            ST_X(pickup_location::geometry) as lng,
            ST_Y(pickup_location::geometry) as lat
        FROM tasks
        WHERE id = :task_id
    """)
    
    coords_result = await db.execute(pickup_query, {"task_id": task.id})
    coords = coords_result.fetchone()
    
    if not coords:
        return
    
    # Find nearby volunteers
    nearby_query = text("""
        SELECT * FROM find_nearby_volunteers(:lat, :lng, 10)
        LIMIT 1
    """)
    
    result = await db.execute(
        nearby_query,
        {"lat": coords.lat, "lng": coords.lng}
    )
    nearest = result.fetchone()
    
    if nearest:
        # Send task assignment via WebSocket
        await socket_manager.send_task_assignment(
            str(nearest.volunteer_id),
            {
                "task_id": str(task.id),
                "pickup_address": "...",  # Fetch from donor
                "drop_address": "...",    # Fetch from NGO
                "distance_km": task.distance_km,
                "expiry_time": task.expiry_time.isoformat()
            }
        )
        
        # Update task with assigned volunteer
        await db.execute(
            update(Task)
            .where(Task.id == task.id)
            .values(volunteer_id=nearest.volunteer_id, status=TaskState.ASSIGNED)
        )
        await db.commit()
