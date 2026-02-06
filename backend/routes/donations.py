from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Donation, NGO, NGOBranch, DonationStatusEnum
from schemas import DonationCreate, DonationResponse, StatusUpdate, DonationVerify, ClaimRequest
from auth import get_current_ngo_user, get_current_user
from models import User

router = APIRouter(prefix="/api/donations", tags=["donations"])

# ============= Get Available Donations =============

@router.get("/available", response_model=List[DonationResponse])
async def get_available_donations(
    db: Session = Depends(get_db)
):
    """
    Get all available donations for NGOs to claim.
    This endpoint is public - no authentication required.
    
    Returns:
        List of available donations
    """
    # Query available donations that haven't expired
    donations = db.query(Donation).filter(
        Donation.status == DonationStatusEnum.AVAILABLE,
        Donation.expiry_time > datetime.utcnow()
    ).order_by(Donation.created_at.desc()).all()
    
    return donations

# ============= Claim Donation =============

@router.patch("/{donation_id}/status", response_model=DonationResponse)
async def claim_donation(
    donation_id: int,
    claim_request: ClaimRequest,
    current_user: User = Depends(get_current_ngo_user),
    db: Session = Depends(get_db)
):
    """
    Claim a donation by updating its status to ASSIGNED.
    Only approved NGOs can claim donations.
    
    Args:
        donation_id: ID of the donation to claim
        claim_request: New status and optional branch_id for delivery
        
    Returns:
        Updated donation object
        
    Raises:
        HTTPException: If donation not found, already claimed, or capacity exceeded
    """
    # Get the donation
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donation not found"
        )
    
    # Check if donation is available
    if donation.status != DonationStatusEnum.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Donation is not available. Current status: {donation.status.value}"
        )
    
    # Check if donation has expired
    if donation.expiry_time <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donation has expired"
        )
    
    # Get NGO details
    ngo = db.query(NGO).filter(NGO.id == current_user.ngo_id).first()
    
    # If branch_id is provided, validate it belongs to the NGO
    branch = None
    if claim_request.branch_id:
        branch = db.query(NGOBranch).filter(
            NGOBranch.id == claim_request.branch_id,
            NGOBranch.ngo_id == current_user.ngo_id,
            NGOBranch.is_active == 1
        ).first()
        
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid branch selected or branch is inactive"
            )
        
        # Check branch storage capacity
        # Calculate current load for this branch
        active_branch_claims = db.query(Donation).filter(
            Donation.branch_id == branch.id,
            Donation.status.in_([DonationStatusEnum.ASSIGNED, DonationStatusEnum.COMPLETED])
        ).all()
        
        branch_current_load = sum(d.quantity for d in active_branch_claims)

        if (branch_current_load + donation.quantity) > branch.storage_capacity:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Branch storage capacity exceeded! Branch Load: {branch_current_load}kg + New: {donation.quantity}kg > Capacity: {branch.storage_capacity}kg"
            )
    else:
        # Check NGO total storage capacity if no branch selected
        # Calculate current total storage occupied by pending donations + collected food
        # This is a simplified check. A more complex one would sum up active donations.
        
        # Get all active claims for this NGO (ASSIGNED or PICKED_UP)
        active_claims = db.query(Donation).filter(
            Donation.ngo_id == current_user.ngo_id,
            Donation.status.in_([DonationStatusEnum.ASSIGNED, DonationStatusEnum.COMPLETED]) 
            # Note: COMPLETED usually means in storage. DELIVERED implies distributed/gone.
            # Assuming COMPLETED means "In NGO Storage"
        ).all()
        
        current_load = sum(d.quantity for d in active_claims)
        
        if (current_load + donation.quantity) > ngo.storage_capacity:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Storage capacity exceeded! Current Load: {current_load}kg + New: {donation.quantity}kg > Capacity: {ngo.storage_capacity}kg"
            )
    
    # Update donation status
    donation.status = claim_request.new_status
    donation.ngo_id = current_user.ngo_id
    donation.branch_id = claim_request.branch_id
    donation.claimed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(donation)
    
    return donation

# ============= Get My Claimed Donations =============

@router.get("/my-claims")
async def get_my_claimed_donations(
    current_user: User = Depends(get_current_ngo_user),
    db: Session = Depends(get_db)
):
    """
    Get all donations claimed by the current NGO.
    Returns donations with status ASSIGNED, PICKED_UP, or DELIVERED.
    """
    donations = db.query(Donation).filter(
        Donation.ngo_id == current_user.ngo_id
    ).order_by(Donation.claimed_at.desc()).all()
    
    # Add branch info to each donation
    result = []
    for donation in donations:
        donation_dict = {
            "id": donation.id,
            "donor_name": donation.donor_name,
            "donor_phone": donation.donor_phone,
            "food_type": donation.food_type.value,
            "quantity": donation.quantity,
            "address": donation.address,
            "latitude": donation.latitude,
            "longitude": donation.longitude,
            "expiry_time": donation.expiry_time.isoformat(),
            "status": donation.status.value,
            "ngo_id": donation.ngo_id,
            "branch_id": donation.branch_id,
            "branch_name": None,
            "branch_address": None,
            "created_at": donation.created_at.isoformat(),
            "claimed_at": donation.claimed_at.isoformat() if donation.claimed_at else None,
        }
        
        # Get branch info if available
        if donation.branch_id:
            branch = db.query(NGOBranch).filter(NGOBranch.id == donation.branch_id).first()
            if branch:
                donation_dict["branch_name"] = branch.name
                donation_dict["branch_address"] = branch.address
        
        result.append(donation_dict)
    
    return result

# ============= Create Donation (for donors) =============

@router.post("", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
async def create_donation(
    donation: DonationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new food donation.
    This endpoint can be used by donors to submit donations.
    
    Args:
        donation: Donation details
        
    Returns:
        Created donation object
    """
    # Create new donation
    db_donation = Donation(
        donor_name=donation.donor_name,
        donor_phone=donation.donor_phone,
        food_type=donation.food_type,
        quantity=donation.quantity,
        address=donation.address,
        latitude=donation.latitude,
        longitude=donation.longitude,
        expiry_time=donation.expiry_time,
        status=DonationStatusEnum.AVAILABLE
    )
    
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)
    
    return db_donation

# ============= Verify Donation (QR Code Verification) =============

@router.get("/{donation_id}/verify", response_model=DonationVerify)
async def verify_donation(
    donation_id: int,
    db: Session = Depends(get_db)
):
    """
    Verify a donation using QR code.
    This endpoint is used by volunteers to verify donations.
    
    Args:
        donation_id: ID of the donation to verify
        
    Returns:
        Donation verification details
        
    Raises:
        HTTPException: If donation not found
    """
    # Get the donation
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donation not found"
        )
    
    # Get NGO name if assigned
    ngo_name = None
    if donation.ngo_id:
        ngo = db.query(NGO).filter(NGO.id == donation.ngo_id).first()
        if ngo:
            ngo_name = ngo.name
    
    return DonationVerify(
        id=donation.id,
        donor_name=donation.donor_name,
        food_type=donation.food_type,
        quantity=donation.quantity,
        address=donation.address,
        status=donation.status,
        ngo_name=ngo_name,
        verified=True
    )

# ============= Get All Donations (for admin/debugging) =============

@router.get("", response_model=List[DonationResponse])
async def get_all_donations(
    db: Session = Depends(get_db)
):
    """
    Get all donations (for testing/admin purposes).
    
    Returns:
        List of all donations
    """
    donations = db.query(Donation).order_by(Donation.created_at.desc()).all()
    return donations

# ============= Verify Donation Pickup =============

@router.put("/{donation_id}/verify", response_model=DonationResponse)
async def verify_donation_pickup(
    donation_id: int,
    current_user: User = Depends(get_current_ngo_user),
    db: Session = Depends(get_db)
):
    """
    Verify that the donation has been picked up.
    Changes status from ASSIGNED to COMPLETED.
    """
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
        
    if donation.ngo_id != current_user.ngo_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this donation"
        )
        
    if donation.status != DonationStatusEnum.ASSIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donation must be ASSIGNED to be verified"
        )
        
    donation.status = DonationStatusEnum.COMPLETED
    db.commit()
    db.refresh(donation)
    
    return donation

