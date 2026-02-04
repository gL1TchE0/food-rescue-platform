"""
M7 Logistics - Volunteer Endpoints
Handle volunteer lifecycle and state management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.redis import get_redis, RedisManager
from app.models.models import Volunteer, Task
from app.schemas.schemas import (
    VolunteerCreate, VolunteerResponse, VolunteerStatusUpdate,
    LocationUpdate, TaskResponse
)
from app.services.state_machine import state_machine, VolunteerState, TransitionError
from app.core.socket_manager import socket_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/volunteer", tags=["Volunteer"])


@router.post("/register", response_model=VolunteerResponse, status_code=status.HTTP_201_CREATED)
async def register_volunteer(
    volunteer_data: VolunteerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register new volunteer"""
    try:
        volunteer = Volunteer(**volunteer_data.dict())
        db.add(volunteer)
        await db.commit()
        await db.refresh(volunteer)
        return volunteer
    except Exception as e:
        logger.error(f"Error registering volunteer: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/status")
async def update_volunteer_status(
    volunteer_id: UUID,
    status_update: VolunteerStatusUpdate,
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """
    Update volunteer status (ONLINE/OFFLINE)
    Triggers state machine transition
    """
    # Get current volunteer
    result = await db.execute(select(Volunteer).where(Volunteer.id == volunteer_id))
    volunteer = result.scalar_one_or_none()
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    current_state = VolunteerState(volunteer.status)
    target_state = VolunteerState(status_update.status)
    
    try:
        # Execute state transition
        transition_result = state_machine.transition(current_state, target_state)
        
        # Update database
        await db.execute(
            update(Volunteer)
            .where(Volunteer.id == volunteer_id)
            .values(status=transition_result["new_state"])
        )
        await db.commit()
        
        # Update Redis
        if target_state == VolunteerState.ONLINE:
            await redis.add_to_online_volunteers(str(volunteer_id))
        elif target_state == VolunteerState.OFFLINE:
            await redis.remove_from_online_volunteers(str(volunteer_id))
        
        # Notify via WebSocket
        await socket_manager.notify_state_change(
            str(volunteer_id),
            transition_result["new_state"]
        )
        
        return {
            "status": "success",
            "new_state": transition_result["new_state"],
            "message": f"Status updated to {transition_result['new_state']}"
        }
        
    except TransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/location")
async def update_location(
    volunteer_id: UUID,
    location: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """
    Update volunteer's current location
    Cached in Redis for real-time tracking and persisted in database
    """
    # Update Redis cache
    await redis.set_volunteer_location(
        str(volunteer_id),
        location.lat,
        location.lng,
        location.heading,
        location.speed
    )
    
    # Update database for spatial queries
    from sqlalchemy import text
    from datetime import datetime
    await db.execute(
        update(Volunteer)
        .where(Volunteer.id == volunteer_id)
        .values(
            current_location=text(f"ST_SetSRID(ST_MakePoint({location.lng}, {location.lat}), 4326)"),
            last_heartbeat=datetime.utcnow()
        )
    )
    await db.commit()
    
    return {"status": "success", "message": "Location updated"}


@router.get("/task/current", response_model=TaskResponse)
async def get_current_task(
    volunteer_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get volunteer's active task"""
    result = await db.execute(
        select(Task)
        .where(Task.volunteer_id == volunteer_id)
        .where(Task.status.in_(['ASSIGNED', 'IN_PROGRESS', 'PICKED_UP', 'IN_TRANSIT']))
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="No active task")
    
    return task


@router.get("/available-actions")
async def get_available_actions(
    volunteer_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get available actions for current state"""
    result = await db.execute(select(Volunteer).where(Volunteer.id == volunteer_id))
    volunteer = result.scalar_one_or_none()
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    current_state = VolunteerState(volunteer.status)
    actions = state_machine.get_available_actions(current_state)
    
    return {
        "current_state": current_state,
        "available_actions": actions
    }


@router.get("/me", response_model=VolunteerResponse)
async def get_volunteer_profile(
    firebase_uid: str,
    db: AsyncSession = Depends(get_db)
):
    """Get volunteer profile by Firebase UID"""
    result = await db.execute(
        select(Volunteer).where(Volunteer.firebase_uid == firebase_uid)
    )
    volunteer = result.scalar_one_or_none()
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    return volunteer
