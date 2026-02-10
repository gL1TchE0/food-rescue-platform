"""
FoodRescue Platform - S1: Map-Based Allocation Backend
FastAPI application with PostgreSQL/PostGIS and WebSocket support
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
# from geoalchemy2 import Geography  # Removed: PostGIS not needed with lat/lng columns
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import json
import enum
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:milkmanisonthedoor@db.isfvqviuduiykpvupjcs.supabase.co:5432/postgres")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class FoodType(str, enum.Enum):
    VEG = "VEG"
    NON_VEG = "NON_VEG"
    VEGAN = "VEGAN"
    MIXED = "MIXED"


class DonationStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# ============================================================================
# DATABASE MODELS
# ============================================================================

class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_name = Column(String, nullable=False)
    donor_phone = Column(String, nullable=False)
    food_type = Column(Enum(FoodType), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    description = Column(String)
    
    # Geospatial data stored as lat/lng (no PostGIS needed)
    
    # For easy access without PostGIS queries
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    address = Column(String, nullable=False)
    status = Column(Enum(DonationStatus), default=DonationStatus.AVAILABLE)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Assignment tracking
    assigned_volunteer_id = Column(Integer, nullable=True)
    assigned_at = Column(DateTime, nullable=True)


# Create tables
Base.metadata.create_all(bind=engine)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class DonationCreate(BaseModel):
    donor_name: str = Field(..., min_length=2, max_length=100)
    donor_phone: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    food_type: FoodType
    quantity_kg: float = Field(..., gt=0, le=500)
    description: Optional[str] = Field(None, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str = Field(..., min_length=10, max_length=300)
    expires_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "donor_name": "Raj's Restaurant",
                "donor_phone": "+919876543210",
                "food_type": "VEG",
                "quantity_kg": 15.5,
                "description": "Biryani and curry - prepared 2 hours ago",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "address": "123 Marina Beach Road, Chennai, Tamil Nadu 600001",
                "expires_at": "2026-01-25T20:00:00"
            }
        }


class DonationResponse(BaseModel):
    id: int
    donor_name: str
    food_type: FoodType
    quantity_kg: float
    description: Optional[str]
    latitude: float
    longitude: float
    address: str
    status: DonationStatus
    created_at: datetime
    expires_at: datetime
    assigned_volunteer_id: Optional[int]

    class Config:
        from_attributes = True


class MapMarker(BaseModel):
    """Lightweight model for map display"""
    id: int
    latitude: float
    longitude: float
    food_type: FoodType
    quantity_kg: float
    status: DonationStatus
    donor_name: str
    expires_at: datetime
    time_until_expiry_hours: float


# ============================================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up dead connections
        for conn in disconnected:
            self.active_connections.remove(conn)


manager = ConnectionManager()


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="FoodRescue S1 API",
    description="Map-Based Allocation System with Real-Time Updates",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register auth router
from auth import router as auth_router
app.include_router(auth_router)


# ============================================================================
# DEPENDENCY
# ============================================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    return {
        "service": "FoodRescue S1 - Map-Based Allocation",
        "status": "operational",
        "endpoints": {
            "donations": "/api/donations",
            "available_donations": "/api/donations/available",
            "map_markers": "/api/map/markers",
            "websocket": "/ws"
        }
    }


@app.post("/api/donations", response_model=DonationResponse, status_code=201)
async def create_donation(donation: DonationCreate, db: Session = Depends(get_db)):
    """
    Create a new food donation listing.
    This will trigger a WebSocket broadcast to update all connected map clients.
    """
    
    db_donation = Donation(
        donor_name=donation.donor_name,
        donor_phone=donation.donor_phone,
        food_type=donation.food_type,
        quantity_kg=donation.quantity_kg,
        description=donation.description,
        latitude=donation.latitude,
        longitude=donation.longitude,
        address=donation.address,
        expires_at=donation.expires_at,
        status=DonationStatus.AVAILABLE
    )
    
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)
    
    # Broadcast to all connected WebSocket clients
    await manager.broadcast({
        "event": "NEW_DONATION",
        "data": {
            "id": db_donation.id,
            "latitude": db_donation.latitude,
            "longitude": db_donation.longitude,
            "food_type": db_donation.food_type.value,
            "quantity_kg": db_donation.quantity_kg,
            "donor_name": db_donation.donor_name,
            "status": db_donation.status.value
        }
    })
    
    return db_donation


@app.get("/api/donations", response_model=List[DonationResponse])
def get_all_donations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all donations with pagination"""
    donations = db.query(Donation).offset(skip).limit(limit).all()
    return donations

@app.delete("/api/donations/cleanup")
def cleanup_expired_donations(db: Session = Depends(get_db)):
    """Deletes all donations that have passed their expiry time"""
    now = datetime.utcnow()
    deleted_count = db.query(Donation).filter(Donation.expires_at < now).delete()
    db.commit()
    return {"message": f"Successfully deleted {deleted_count} expired donations."}

@app.get("/api/donations/available", response_model=List[DonationResponse])
def get_available_donations(db: Session = Depends(get_db)):
    """
    Get all donations with status = AVAILABLE.
    This is the primary endpoint for the dispatcher's map view.
    """
    donations = db.query(Donation).filter(
        Donation.status == DonationStatus.AVAILABLE
    ).order_by(Donation.expires_at.asc()).all()
    
    return donations


@app.get("/api/map/markers", response_model=List[MapMarker])
def get_map_markers(db: Session = Depends(get_db)):
    """
    Optimized endpoint for map markers.
    Returns only essential data for rendering markers on the map.
    """
    donations = db.query(Donation).filter(
        Donation.status == DonationStatus.AVAILABLE
    ).all()
    
    markers = []
    now = datetime.utcnow()
    
    for donation in donations:
        time_diff = (donation.expires_at - now).total_seconds() / 3600
        
        markers.append(MapMarker(
            id=donation.id,
            latitude=donation.latitude,
            longitude=donation.longitude,
            food_type=donation.food_type,
            quantity_kg=donation.quantity_kg,
            status=donation.status,
            donor_name=donation.donor_name,
            expires_at=donation.expires_at,
            time_until_expiry_hours=round(time_diff, 1)
        ))
    
    return markers


@app.get("/api/donations/{donation_id}", response_model=DonationResponse)
def get_donation_by_id(donation_id: int, db: Session = Depends(get_db)):
    """Get specific donation details"""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    return donation


@app.patch("/api/donations/{donation_id}/status")
async def update_donation_status(
    donation_id: int,
    new_status: DonationStatus,
    db: Session = Depends(get_db)
):
    """
    Update donation status (for testing and future stories).
    Broadcasts the change to all connected clients.
    """
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    donation.status = new_status
    db.commit()
    
    # Broadcast status change
    await manager.broadcast({
        "event": "STATUS_UPDATE",
        "data": {
            "id": donation.id,
            "status": new_status.value
        }
    })
    
    return {"message": "Status updated", "donation_id": donation_id, "new_status": new_status}


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket connection for real-time map updates.
    Clients connect here to receive live donation updates.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            
            # Echo back for connection verification
            await websocket.send_json({
                "event": "PONG",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Check database connectivity"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
