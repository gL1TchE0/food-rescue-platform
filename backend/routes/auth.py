from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta, datetime

from database import get_db
from models import User, NGO, NGOBranch, Donation, UserRoleEnum, ApprovalStatusEnum, DonationStatusEnum
from schemas import UserLogin, Token, NGOCreate, UserResponse, NGOResponse, NGODetailResponse
from auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# ============= Login =============

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    Args:
        user_credentials: Email and password
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

# ============= Register NGO =============

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_ngo(
    ngo_data: NGOCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new NGO and create user account.
    NGO will be in PENDING status until approved by admin.
    
    Args:
        ngo_data: NGO registration details
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == ngo_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create NGO
    db_ngo = NGO(
        name=ngo_data.name,
        email=ngo_data.email,
        phone=ngo_data.phone,
        address=ngo_data.address,
        serving_capacity=ngo_data.serving_capacity,
        approval_status=ApprovalStatusEnum.APPROVED  # Auto-approve for demo
    )
    
    db.add(db_ngo)
    db.commit()
    db.refresh(db_ngo)
    
    # Create user account
    db_user = User(
        email=ngo_data.email,
        hashed_password=get_password_hash(ngo_data.password),
        role=UserRoleEnum.NGO,
        ngo_id=db_ngo.id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "user_id": db_user.id,
            "role": db_user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

# ============= Get Current User =============

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user details.
    
    Returns:
        Current user information
    """
    return current_user

# ============= Get Current NGO =============

@router.get("/ngo", response_model=NGOResponse)
async def get_current_ngo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's NGO details.
    
    Returns:
        NGO information
        
    Raises:
        HTTPException: If user is not an NGO or NGO not found
    """
    if current_user.role != UserRoleEnum.NGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an NGO"
        )
    
    if not current_user.ngo_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NGO profile not found"
        )
    
    ngo = db.query(NGO).filter(NGO.id == current_user.ngo_id).first()
    
    if not ngo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NGO not found"
        )
    
    return ngo


# ============= Get Current NGO Dashboard Details =============

@router.get("/ngo/dashboard", response_model=NGODetailResponse)
async def get_ngo_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's NGO details with branches and statistics.
    
    Returns:
        Detailed NGO information including branches and storage totals
        
    Raises:
        HTTPException: If user is not an NGO or NGO not found
    """
    if current_user.role != UserRoleEnum.NGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an NGO"
        )
    
    if not current_user.ngo_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NGO profile not found"
        )
    
    ngo = db.query(NGO).filter(NGO.id == current_user.ngo_id).first()
    
    if not ngo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NGO not found"
        )
    
    # Calculate total currently stored (active claims)
    total_stored = db.query(func.sum(Donation.quantity)).filter(
        Donation.ngo_id == ngo.id,
        Donation.status == DonationStatusEnum.ASSIGNED
    ).scalar() or 0.0
    
    # Get branches
    branches = db.query(NGOBranch).filter(NGOBranch.ngo_id == ngo.id).all()
    
    return NGODetailResponse(
        id=ngo.id,
        name=ngo.name,
        email=ngo.email,
        phone=ngo.phone,
        address=ngo.address,
        storage_capacity=ngo.storage_capacity,
        approval_status=ngo.approval_status,
        created_at=ngo.created_at,
        branches=[{
            "id": b.id,
            "name": b.name,
            "address": b.address,
            "phone": b.phone,
            "storage_capacity": b.storage_capacity,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "is_active": b.is_active
        } for b in branches],
        total_stored=total_stored
    )
