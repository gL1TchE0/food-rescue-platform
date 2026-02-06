from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

# Food type enumeration
class FoodTypeEnum(str, enum.Enum):
    VEG = "VEG"
    NON_VEG = "NON_VEG"
    VEGAN = "VEGAN"
    MIXED = "MIXED"
    SNACK = "SNACK"

# Donation status enumeration
class DonationStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# User role enumeration
class UserRoleEnum(str, enum.Enum):
    NGO = "NGO"
    DONOR = "DONOR"
    VOLUNTEER = "VOLUNTEER"
    DISPATCHER = "DISPATCHER"

# NGO approval status
class ApprovalStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class NGO(Base):
    """NGO model for organizations claiming donations"""
    __tablename__ = "ngos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String)
    address = Column(String)  # Main/HQ address
    storage_capacity = Column(Float, default=100.0)  # Total storage capacity in kg
    approval_status = Column(SQLEnum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="ngo")
    donations = relationship("Donation", back_populates="ngo")
    branches = relationship("NGOBranch", back_populates="ngo", cascade="all, delete-orphan")


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRoleEnum), default=UserRoleEnum.NGO)
    ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ngo = relationship("NGO", back_populates="users")


class NGOBranch(Base):
    """Branch locations for an NGO"""
    __tablename__ = "ngo_branches"

    id = Column(Integer, primary_key=True, index=True)
    ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=False)
    name = Column(String, nullable=False)  # Branch name (e.g., "North Delhi Branch")
    address = Column(String, nullable=False)
    phone = Column(String)
    storage_capacity = Column(Float, default=50.0)  # Storage capacity in kg for this branch
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ngo = relationship("NGO", back_populates="branches")


class Donation(Base):
    """Donation model for food donations"""
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_name = Column(String, nullable=False)
    donor_phone = Column(String)
    food_type = Column(SQLEnum(FoodTypeEnum), default=FoodTypeEnum.MIXED)
    quantity = Column(Float, nullable=False)  # in kg
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    expiry_time = Column(DateTime, nullable=False)
    status = Column(SQLEnum(DonationStatusEnum), default=DonationStatusEnum.AVAILABLE)
    ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("ngo_branches.id"), nullable=True)  # Delivery branch
    created_at = Column(DateTime, default=datetime.utcnow)
    claimed_at = Column(DateTime, nullable=True)
    
    # Relationships
    ngo = relationship("NGO", back_populates="donations")
