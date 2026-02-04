"""
M7 Logistics - Pydantic Schemas
Request/Response validation models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============ Volunteer Schemas ============

class VolunteerBase(BaseModel):
    full_name: str
    phone_number: str
    vehicle_type: Optional[str] = None
    vehicle_plate: Optional[str] = None
    capacity_kg: int = 10


class VolunteerCreate(VolunteerBase):
    firebase_uid: str


class VolunteerResponse(VolunteerBase):
    id: UUID
    firebase_uid: str
    status: str
    rating: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class VolunteerStatusUpdate(BaseModel):
    status: str  # ONLINE, OFFLINE, BUSY


class LocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    speed: float = 0
    heading: float = 0


# ============ Task Schemas ============

class TaskCreate(BaseModel):
    donor_id: UUID
    ngo_id: UUID
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float
    food_type: Optional[str] = None
    expiry_time: datetime
    requires_cooling: bool = False


class TaskResponse(BaseModel):
    id: UUID
    donor_id: UUID
    ngo_id: UUID
    volunteer_id: Optional[UUID]
    distance_km: Optional[float]
    food_type: Optional[str]
    expiry_time: datetime
    requires_cooling: bool
    status: str
    pickup_token: str
    delivery_token: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskAcceptance(BaseModel):
    volunteer_id: UUID


class QRVerification(BaseModel):
    qr_token: str


class TaskException(BaseModel):
    issue_type: str  # FLAT_TIRE, ACCIDENT, FOOD_SPOILED, VEHICLE_ISSUE
    description: Optional[str] = None


# ============ Tracking Schemas ============

class TrackingUpdate(BaseModel):
    volunteer_id: UUID
    task_id: UUID
    lat: float
    lng: float
    speed: float = 0
    heading: float = 0


class DonorTrackingView(BaseModel):
    task_id: UUID
    volunteer_name: str
    vehicle_type: str
    current_location: Optional[dict] = None
    eta_minutes: Optional[int] = None
    status: str


# ============ State Machine Schemas ============

class StateTransitionRequest(BaseModel):
    target_state: str
    context: Optional[dict] = None


class StateTransitionResponse(BaseModel):
    new_state: str
    task_state: Optional[str]
    side_effects: dict
    timestamp: str


# ============ WebSocket Schemas ============

class WebSocketMessage(BaseModel):
    event: str
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============ Exception Schemas ============

class ExceptionCreate(BaseModel):
    task_id: UUID
    issue_type: str
    description: Optional[str] = None


class ExceptionResponse(BaseModel):
    id: UUID
    task_id: UUID
    issue_type: str
    description: Optional[str]
    resolved: bool
    reported_at: datetime
    
    class Config:
        from_attributes = True


# ============ Performance Schemas ============

class PerformanceStatCreate(BaseModel):
    volunteer_id: UUID
    task_id: UUID
    on_time: bool
    completion_time_minutes: int
    distance_traveled_km: float
    rating: int = Field(..., ge=1, le=5)


class PerformanceStatResponse(BaseModel):
    id: UUID
    volunteer_id: UUID
    task_id: UUID
    on_time: bool
    completion_time_minutes: int
    distance_traveled_km: float
    rating: int
    created_at: datetime
    
    class Config:
        from_attributes = True
