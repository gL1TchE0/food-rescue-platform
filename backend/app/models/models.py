"""
M7 Logistics - SQLAlchemy Models
Database ORM definitions with PostGIS support
"""
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, ForeignKey, Text, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime
import uuid
import secrets

from app.db.session import Base


class Volunteer(Base):
    """Volunteer model"""
    __tablename__ = "volunteers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    vehicle_type = Column(String(20))  # BIKE, SCOOTER, CAR, VAN
    vehicle_plate = Column(String(20))
    capacity_kg = Column(Integer, default=10)
    status = Column(String(20), default='OFFLINE', index=True)
    current_location = Column(Geometry('POINT', srid=4326))
    last_heartbeat = Column(DateTime)
    rating = Column(DECIMAL(3, 2), default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="volunteer")
    performance_stats = relationship("PerformanceStat", back_populates="volunteer")


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    donor_id = Column(UUID(as_uuid=True), nullable=False)
    ngo_id = Column(UUID(as_uuid=True), nullable=False)
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey('volunteers.id'))
    pickup_location = Column(Geometry('POINT', srid=4326), nullable=False)
    drop_location = Column(Geometry('POINT', srid=4326), nullable=False)
    distance_km = Column(DECIMAL(5, 2))
    food_type = Column(String(50))
    expiry_time = Column(DateTime, nullable=False, index=True)
    requires_cooling = Column(Boolean, default=False)
    status = Column(String(30), default='PENDING', index=True)
    pickup_proof_url = Column(String(255))
    drop_proof_url = Column(String(255))
    pickup_token = Column(String(10), unique=True, nullable=False, default=lambda: secrets.token_hex(3).upper())
    delivery_token = Column(String(10), unique=True, nullable=False, default=lambda: secrets.token_hex(3).upper())
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    volunteer = relationship("Volunteer", back_populates="tasks")
    tracking_session = relationship("TrackingSession", back_populates="task", uselist=False)
    exceptions = relationship("TaskException", back_populates="task")


class TrackingSession(Base):
    """Real-time tracking session"""
    __tablename__ = "tracking_sessions"
    
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey('volunteers.id'), primary_key=True)
    mapbox_session_id = Column(String(100))
    route_polyline = Column(Text)
    start_time = Column(DateTime, default=datetime.utcnow)
    last_update = Column(DateTime)
    
    # Relationships
    task = relationship("Task", back_populates="tracking_session")


class TaskException(Base):
    """Task exceptions/issues"""
    __tablename__ = "task_exceptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'))
    issue_type = Column(String(50))  # FLAT_TIRE, ACCIDENT, FOOD_SPOILED, VEHICLE_ISSUE
    description = Column(Text)
    resolved = Column(Boolean, default=False, index=True)
    reported_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    task = relationship("Task", back_populates="exceptions")


class Donor(Base):
    """Donor model"""
    __tablename__ = "donors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    address = Column(Text, nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    qr_token = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class NGO(Base):
    """NGO/Beneficiary model"""
    __tablename__ = "ngos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    address = Column(Text, nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    qr_token = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PerformanceStat(Base):
    """Volunteer performance tracking"""
    __tablename__ = "performance_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey('volunteers.id'))
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'))
    on_time = Column(Boolean)
    completion_time_minutes = Column(Integer)
    distance_traveled_km = Column(DECIMAL(5, 2))
    rating = Column(Integer)  # 1-5
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    volunteer = relationship("Volunteer", back_populates="performance_stats")
