"""
Shared pytest fixtures for Food Rescue Platform backend tests.

Uses the Supabase PostgreSQL database (from .env DATABASE_URL).
Each test runs inside a transaction that is rolled back afterwards,
so the production data is never modified.
"""
import sys
import os

# Add backend root to sys.path so that `from database import ...` works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load .env from the backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from database import Base, get_db
from models import User, NGO, Donation, NGOBranch
from models import UserRoleEnum, ApprovalStatusEnum, DonationStatusEnum, FoodTypeEnum
from auth import get_password_hash, create_access_token
from main import app

# ---------------------------------------------------------------------------
# Database engine – Supabase PostgreSQL
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db_session():
    """
    Yield a DB session wrapped in a transaction.
    The transaction is rolled back after every test so
    no test data persists in the Supabase database.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI TestClient that uses the test DB session.
    """
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---- Data helpers ----

@pytest.fixture
def sample_ngo(db_session):
    """Create and return a sample approved NGO."""
    ngo = NGO(
        name="Test NGO",
        email="testngo@example.com",
        phone="1234567890",
        address="123 Test Street",
        storage_capacity=500.0,
        approval_status=ApprovalStatusEnum.APPROVED,
    )
    db_session.add(ngo)
    db_session.flush()
    return ngo


@pytest.fixture
def sample_user(db_session, sample_ngo):
    """Create and return a sample NGO user linked to sample_ngo."""
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRoleEnum.NGO,
        ngo_id=sample_ngo.id,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def donor_user(db_session):
    """Create and return a DONOR user (not an NGO)."""
    user = User(
        email="donor@example.com",
        hashed_password=get_password_hash("donorpass"),
        role=UserRoleEnum.DONOR,
        ngo_id=None,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def sample_donation(db_session):
    """Create and return a sample AVAILABLE donation."""
    donation = Donation(
        donor_name="John Doe",
        donor_phone="9876543210",
        food_type=FoodTypeEnum.VEG,
        quantity=10.0,
        address="456 Donor Avenue",
        latitude=28.6139,
        longitude=77.2090,
        expiry_time=datetime.utcnow() + timedelta(hours=5),
        status=DonationStatusEnum.AVAILABLE,
    )
    db_session.add(donation)
    db_session.flush()
    return donation


@pytest.fixture
def expired_donation(db_session):
    """Create and return an EXPIRED donation."""
    donation = Donation(
        donor_name="Expired Donor",
        donor_phone="0000000000",
        food_type=FoodTypeEnum.MIXED,
        quantity=5.0,
        address="789 Old Road",
        expiry_time=datetime.utcnow() - timedelta(hours=1),
        status=DonationStatusEnum.AVAILABLE,
    )
    db_session.add(donation)
    db_session.flush()
    return donation


@pytest.fixture
def auth_headers(sample_user):
    """Return Authorization headers with a valid JWT for sample_user."""
    token = create_access_token(
        data={
            "sub": sample_user.email,
            "user_id": sample_user.id,
            "role": sample_user.role.value,
        }
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def donor_auth_headers(donor_user):
    """Return Authorization headers with a valid JWT for donor_user."""
    token = create_access_token(
        data={
            "sub": donor_user.email,
            "user_id": donor_user.id,
            "role": donor_user.role.value,
        }
    )
    return {"Authorization": f"Bearer {token}"}
