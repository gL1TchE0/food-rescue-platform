from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from models import FoodTypeEnum, DonationStatusEnum, UserRoleEnum, ApprovalStatusEnum

# ============= Authentication Schemas =============

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token payload data"""
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    role: UserRoleEnum
    ngo_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# ============= NGO Schemas =============

class NGOCreate(BaseModel):
    """Schema for creating an NGO"""
    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    address: Optional[str] = None
    storage_capacity: float = Field(default=100.0, gt=0)

class NGOBranchResponse(BaseModel):
    """Schema for NGO branch response"""
    id: int
    name: str
    address: str
    phone: Optional[str] = None
    storage_capacity: float = 50.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: int
    
    class Config:
        from_attributes = True

class NGOResponse(BaseModel):
    """Schema for NGO response"""
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    storage_capacity: float
    approval_status: ApprovalStatusEnum
    created_at: datetime
    
    class Config:
        from_attributes = True

class NGODetailResponse(BaseModel):
    """Schema for detailed NGO response with branches"""
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    storage_capacity: float
    approval_status: ApprovalStatusEnum
    created_at: datetime
    branches: list[NGOBranchResponse] = []
    total_stored: float = 0.0  # Total kg currently stored
    
    class Config:
        from_attributes = True

# ============= Donation Schemas =============

class ClaimRequest(BaseModel):
    """Schema for claiming a donation with branch selection"""
    new_status: DonationStatusEnum
    branch_id: Optional[int] = None  # Delivery branch

class DonationCreate(BaseModel):
    """Schema for creating a donation"""
    donor_name: str = Field(..., min_length=2, max_length=200)
    donor_phone: Optional[str] = None
    food_type: FoodTypeEnum = FoodTypeEnum.MIXED
    quantity: float = Field(..., gt=0, description="Quantity in kg")
    address: str = Field(..., min_length=5)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    expiry_time: datetime

class DonationResponse(BaseModel):
    """Schema for donation response"""
    id: int
    donor_name: str
    donor_phone: Optional[str] = None
    food_type: FoodTypeEnum
    quantity: float
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    expiry_time: datetime
    status: DonationStatusEnum
    ngo_id: Optional[int] = None
    branch_id: Optional[int] = None
    branch_name: Optional[str] = None  # Delivery branch name
    branch_address: Optional[str] = None  # Delivery branch address
    created_at: datetime
    claimed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    """Schema for updating donation status"""
    new_status: DonationStatusEnum

class DonationVerify(BaseModel):
    """Schema for donation verification response"""
    id: int
    donor_name: str
    food_type: FoodTypeEnum
    quantity: float
    address: str
    status: DonationStatusEnum
    ngo_name: Optional[str] = None
    verified: bool = True
    
    class Config:
        from_attributes = True
