"""
FoodRescue Platform - Authentication Module
JWT-based authentication with 2FA (OTP via email)
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy import Column, Integer, String, DateTime, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import enum
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================
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
# JWT CONFIGURATION
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-surplus-sync-2024")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))

# ============================================================================
# PASSWORD HASHING
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@foodrescue.com")

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    DISPATCHER = "DISPATCHER"
    NGO = "NGO"
    VOLUNTEER = "VOLUNTEER"
    DONOR = "DONOR"


# ============================================================================
# DATABASE MODEL
# ============================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    
    # OTP fields for 2FA
    otp_code = Column(String(6), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    is_verified = Column(Integer, default=0)  # 0 = not verified, 1 = verified
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    password: str = Field(..., min_length=6)
    role: UserRole

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+919876543210",
                "password": "password123",
                "role": "VOLUNTEER"
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class OTPResend(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: UserRole
    is_verified: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
    email: Optional[str] = None


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
# HELPER FUNCTIONS
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_otp_email(email: str, otp: str, name: str = "User"):
    """Send OTP via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = "FoodRescue - Your Verification Code"
        
        body = f"""
        Hello {name},
        
        Your verification code is: {otp}
        
        This code will expire in 10 minutes.
        
        If you didn't request this code, please ignore this email.
        
        Best regards,
        FoodRescue Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Log to console for development
        print(f"📧 [DEV LOG] OTP for {email}: {otp}")
        
        # Send actual email if credentials are provided
        if SMTP_USER and SMTP_PASSWORD and SMTP_USER != "your-email@gmail.com":
            print(f"📧 Sending email to {email} via {SMTP_HOST}...")
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, email, msg.as_string())
            server.quit()
            print("✅ Email sent successfully")
        else:
            print("⚠️ SMTP credentials not set. Email not sent. Check console log above for OTP.")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=MessageResponse)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user. Sends OTP to email for verification.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate OTP
    otp = generate_otp()
    otp_expires = datetime.utcnow() + timedelta(minutes=10)
    
    # Create user
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        otp_code=otp,
        otp_expires_at=otp_expires,
        is_verified=0
    )
    
    db.add(db_user)
    db.commit()
    
    # Send OTP email in background
    background_tasks.add_task(send_otp_email, user_data.email, otp, user_data.name)
    
    return MessageResponse(
        message="Registration successful. Please check your email for OTP.",
        email=user_data.email
    )


@router.post("/verify-otp", response_model=Token)
async def verify_otp(
    otp_data: OTPVerify,
    db: Session = Depends(get_db)
):
    """
    Verify OTP after registration to complete account activation.
    """
    user = db.query(User).filter(User.email == otp_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.otp_code != otp_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    # Mark user as verified and clear OTP
    user.is_verified = 1
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    db.refresh(user)
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=MessageResponse)
async def login(
    login_data: UserLogin,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Login step 1: Verify credentials and send OTP.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if user.is_verified == 0:
        raise HTTPException(status_code=400, detail="Account not verified. Please verify OTP first.")
    
    # Generate new OTP for login
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    # Send OTP email
    background_tasks.add_task(send_otp_email, user.email, otp, user.name)
    
    return MessageResponse(
        message="OTP sent to your email.",
        email=user.email
    )


@router.post("/login/verify", response_model=Token)
async def login_verify(
    otp_data: OTPVerify,
    db: Session = Depends(get_db)
):
    """
    Login step 2: Verify OTP and return access token.
    """
    user = db.query(User).filter(User.email == otp_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.otp_code != otp_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    # Clear OTP
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    db.refresh(user)
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/resend-otp", response_model=MessageResponse)
async def resend_otp(
    resend_data: OTPResend,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Resend OTP to user's email.
    """
    user = db.query(User).filter(User.email == resend_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate new OTP
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    # Send OTP email
    background_tasks.add_task(send_otp_email, user.email, otp, user.name)
    
    return MessageResponse(
        message="OTP resent to your email.",
        email=user.email
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get current user from token.
    Pass token as query parameter: /api/auth/me?token=your_token
    """
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
