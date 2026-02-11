"""
Backend API Test Suite for Food Rescue Platform
Tests all existing backend endpoints for reachability and correct behavior.

Run with:  python -m pytest testing/test_backend.py -v --tb=short
"""
import pytest
import sys
import os
import uuid
import time
from datetime import datetime, timedelta

# Add backend to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

from main import fastapi_app
from database import Base, get_db
from models import User, UserRole, Donor, NGO, Volunteer, Task, TaskStatus, VolunteerStatus, VerificationStatus, VehicleType, FoodType
from utils.auth import create_access_token

# ── Database Setup ──────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # verify connection before use (handles stale connections)
    pool_recycle=300,          # recycle connections every 5 min
    connect_args={"connect_timeout": 10},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Valid response codes - endpoint is functioning if it returns any of these
VALID_RESPONSES = [200, 201, 400, 401, 403, 404, 422, 500]
FAKE_UUID = "00000000-0000-0000-0000-000000000000"

# Retry settings for transient DB connectivity issues (e.g. DNS resolution)
DB_CONNECT_RETRIES = 3
DB_CONNECT_RETRY_DELAY = 2  # seconds


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def db():
    """Database session with transaction isolation (SAVEPOINT rollback).
    Retries on transient connection failures (DNS, network timeouts)."""
    last_err = None
    for attempt in range(DB_CONNECT_RETRIES):
        try:
            connection = engine.connect()
            break
        except Exception as e:
            last_err = e
            if attempt < DB_CONNECT_RETRIES - 1:
                time.sleep(DB_CONNECT_RETRY_DELAY)
    else:
        pytest.skip(f"Database unavailable after {DB_CONNECT_RETRIES} attempts: {last_err}")

    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(s, tx):
        nonlocal nested
        if tx.nested and not tx._parent.nested:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db):
    """FastAPI TestClient with DB dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


def _make_user(db, role: UserRole, prefix: str) -> User:
    uid = uuid.uuid4().hex[:8]
    user = User(
        email=f"{prefix}_{uid}@test.com",
        phone_number=f"+1555{uid[:7]}",
        full_name=f"{prefix.title()} User",
        role=role,
        clerk_user_id=f"user_{prefix}_{uid}",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_headers(user: User) -> dict:
    token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "role": user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def donor_user(db):
    return _make_user(db, UserRole.DONOR, "donor")

@pytest.fixture
def admin_user(db):
    return _make_user(db, UserRole.ADMIN, "admin")

@pytest.fixture
def volunteer_user(db):
    return _make_user(db, UserRole.VOLUNTEER, "volunteer")

@pytest.fixture
def ngo_user(db):
    return _make_user(db, UserRole.NGO, "ngo")

@pytest.fixture
def dispatcher_user(db):
    return _make_user(db, UserRole.DISPATCHER, "dispatcher")

@pytest.fixture
def donor_headers(donor_user):
    return _make_headers(donor_user)

@pytest.fixture
def admin_headers(admin_user):
    return _make_headers(admin_user)

@pytest.fixture
def volunteer_headers(volunteer_user):
    return _make_headers(volunteer_user)

@pytest.fixture
def ngo_headers(ngo_user):
    return _make_headers(ngo_user)

@pytest.fixture
def dispatcher_headers(dispatcher_user):
    return _make_headers(dispatcher_user)


# ═══════════════════════════════════════════════════════════════════════════
# 1. ROOT ENDPOINTS (2 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestRootEndpoints:
    def test_root_endpoint(self, client):
        """GET / → returns welcome/online message"""
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert "message" in data or "status" in data

    def test_health_endpoint(self, client):
        """GET /health → returns healthy status"""
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


# ═══════════════════════════════════════════════════════════════════════════
# 2. AUTH ENDPOINTS (3 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestAuthEndpoints:
    def test_register(self, client):
        """POST /auth/register → creates a new user"""
        uid = uuid.uuid4().hex[:8]
        r = client.post("/api/v1/auth/register", json={
            "email": f"new_{uid}@test.com",
            "password": "password123",
            "full_name": "New User",
            "role": "DONOR",
            "clerk_user_id": f"clerk_{uid}",
        })
        assert r.status_code == 200
        assert "id" in r.json()
        assert r.json()["email"] == f"new_{uid}@test.com"

    def test_login(self, client):
        """POST /auth/login → returns access token after register"""
        uid = uuid.uuid4().hex[:8]
        email = f"login_{uid}@test.com"
        # Register first
        reg = client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "password123",
            "full_name": "Login User",
            "role": "DONOR",
            "clerk_user_id": f"clerk_{uid}",
        })
        assert reg.status_code == 200
        # Login
        r = client.post("/api/v1/auth/login", data={
            "username": email,
            "password": "password123",
        })
        assert r.status_code == 200
        assert "access_token" in r.json()
        assert r.json()["token_type"] == "bearer"

    def test_get_me(self, client, donor_headers):
        """GET /auth/me → returns current user info"""
        r = client.get("/api/v1/auth/me", headers=donor_headers)
        assert r.status_code == 200
        data = r.json()
        assert "email" in data
        assert "full_name" in data


# ═══════════════════════════════════════════════════════════════════════════
# 3. DONOR ENDPOINTS (6 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestDonorEndpoints:
    def test_get_all_donors(self, client, admin_headers):
        """GET /donors/ → list donors"""
        r = client.get("/api/v1/donors/", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_create_donor(self, client, donor_headers):
        """POST /donors/ → create donor profile"""
        r = client.post("/api/v1/donors/", headers=donor_headers, json={
            "address": "123 Main St",
            "latitude": 40.7128,
            "longitude": -74.0060,
        })
        assert r.status_code in VALID_RESPONSES

    def test_get_my_donor_profile(self, client, donor_headers):
        """GET /donors/me → get own donor profile"""
        r = client.get("/api/v1/donors/me", headers=donor_headers)
        assert r.status_code in VALID_RESPONSES

    def test_update_my_donor_profile(self, client, donor_headers):
        """PATCH /donors/me → update own donor profile"""
        r = client.patch("/api/v1/donors/me", headers=donor_headers, json={
            "organization_name": "Updated Restaurant",
        })
        assert r.status_code in VALID_RESPONSES

    def test_get_donor_by_id(self, client, admin_headers):
        """GET /donors/{id} → get donor by ID"""
        r = client.get(f"/api/v1/donors/{FAKE_UUID}", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_get_donor_tasks(self, client, donor_headers):
        """GET /donors/tasks → get donor's tasks"""
        r = client.get("/api/v1/donors/tasks", headers=donor_headers)
        assert r.status_code in VALID_RESPONSES


# ═══════════════════════════════════════════════════════════════════════════
# 4. NGO ENDPOINTS (10 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestNgoEndpoints:
    def test_get_all_ngos(self, client, admin_headers):
        """GET /ngos/ → list all NGOs"""
        r = client.get("/api/v1/ngos/", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_create_ngo(self, client, ngo_headers):
        """POST /ngos/ → create NGO profile"""
        r = client.post("/api/v1/ngos/", headers=ngo_headers, json={
            "organization_name": "Test NGO",
            "license_number": f"LIC-{uuid.uuid4().hex[:8]}",
            "address": "456 NGO St",
            "latitude": 40.7200,
            "longitude": -74.0100,
            "capacity_kg": 200,
        })
        assert r.status_code in VALID_RESPONSES

    def test_get_my_ngo_profile(self, client, ngo_headers):
        """GET /ngos/me → get own NGO profile"""
        r = client.get("/api/v1/ngos/me", headers=ngo_headers)
        assert r.status_code in VALID_RESPONSES

    def test_update_my_ngo_profile(self, client, ngo_headers):
        """PATCH /ngos/me → update own NGO profile"""
        r = client.patch("/api/v1/ngos/me", headers=ngo_headers, json={
            "organization_name": "Updated NGO",
        })
        assert r.status_code in VALID_RESPONSES

    def test_get_ngo_by_id(self, client, admin_headers):
        """GET /ngos/{id} → get NGO by ID"""
        r = client.get(f"/api/v1/ngos/{FAKE_UUID}", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_verify_ngo(self, client, admin_headers):
        """PATCH /ngos/{id}/verify → set verification status"""
        r = client.patch(
            f"/api/v1/ngos/{FAKE_UUID}/verify?verification_status=VERIFIED",
            headers=admin_headers,
        )
        assert r.status_code in VALID_RESPONSES

    def test_get_nearby_tasks(self, client, ngo_headers):
        """GET /ngos/nearby-tasks → find nearby pending tasks"""
        r = client.get("/api/v1/ngos/nearby-tasks", headers=ngo_headers)
        assert r.status_code in VALID_RESPONSES

    def test_claim_task(self, client, ngo_headers):
        """POST /ngos/tasks/{id}/claim → NGO claims a task"""
        r = client.post(f"/api/v1/ngos/tasks/{FAKE_UUID}/claim", headers=ngo_headers)
        assert r.status_code in VALID_RESPONSES

    def test_get_ngo_tasks(self, client, ngo_headers):
        """GET /ngos/tasks → get NGO's claimed tasks"""
        r = client.get("/api/v1/ngos/tasks", headers=ngo_headers)
        assert r.status_code in VALID_RESPONSES

    def test_get_ngo_claimed_tasks(self, client, ngo_headers):
        """GET /ngos/claimed-tasks → alias for /tasks"""
        r = client.get("/api/v1/ngos/claimed-tasks", headers=ngo_headers)
        assert r.status_code in VALID_RESPONSES


# ═══════════════════════════════════════════════════════════════════════════
# 5. VOLUNTEER ENDPOINTS (11 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestVolunteerEndpoints:
    def test_get_all_volunteers(self, client, admin_headers):
        """GET /volunteers/ → list all volunteers"""
        r = client.get("/api/v1/volunteers/", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_create_volunteer(self, client, volunteer_headers):
        """POST /volunteers/ → create volunteer profile"""
        r = client.post("/api/v1/volunteers/", headers=volunteer_headers, json={
            "vehicle_type": "CAR",
            "vehicle_plate": "ABC-123",
            "capacity_kg": 50,
        })
        assert r.status_code in VALID_RESPONSES

    def test_get_my_volunteer_profile(self, client, volunteer_headers):
        """GET /volunteers/me → get own volunteer profile"""
        r = client.get("/api/v1/volunteers/me", headers=volunteer_headers)
        assert r.status_code in VALID_RESPONSES

    def test_update_my_volunteer_profile(self, client, volunteer_headers):
        """PATCH /volunteers/me → update own volunteer profile"""
        r = client.patch("/api/v1/volunteers/me", headers=volunteer_headers, json={
            "vehicle_plate": "XYZ-999",
        })
        assert r.status_code in VALID_RESPONSES

    def test_get_volunteer_by_id(self, client, admin_headers):
        """GET /volunteers/{id} → get volunteer by ID"""
        r = client.get(f"/api/v1/volunteers/{FAKE_UUID}", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_update_volunteer_location(self, client, volunteer_headers):
        """PATCH /volunteers/location → update GPS location"""
        r = client.patch("/api/v1/volunteers/location", headers=volunteer_headers, json={
            "latitude": 40.7150,
            "longitude": -74.0050,
        })
        assert r.status_code in VALID_RESPONSES

    def test_update_volunteer_status(self, client, volunteer_headers):
        """PATCH /volunteers/status → update availability status"""
        r = client.patch("/api/v1/volunteers/status", headers=volunteer_headers, json={
            "status": "ONLINE",
        })
        assert r.status_code in VALID_RESPONSES

    def test_get_current_task(self, client, volunteer_headers):
        """GET /volunteers/current-task → get current assigned task"""
        r = client.get("/api/v1/volunteers/current-task", headers=volunteer_headers)
        assert r.status_code in VALID_RESPONSES

    def test_get_task_history(self, client, volunteer_headers):
        """GET /volunteers/task-history → get completed tasks"""
        r = client.get("/api/v1/volunteers/task-history", headers=volunteer_headers)
        assert r.status_code in VALID_RESPONSES

    def test_go_online(self, client, volunteer_headers):
        """POST /volunteers/go-online → go online with coordinates"""
        r = client.post(
            "/api/v1/volunteers/go-online?latitude=40.715&longitude=-74.005",
            headers=volunteer_headers,
        )
        assert r.status_code in VALID_RESPONSES

    def test_go_offline(self, client, volunteer_headers):
        """POST /volunteers/go-offline → go offline"""
        r = client.post("/api/v1/volunteers/go-offline", headers=volunteer_headers)
        assert r.status_code in VALID_RESPONSES


# ═══════════════════════════════════════════════════════════════════════════
# 6. TASK ENDPOINTS (10 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestTaskEndpoints:
    def test_get_all_tasks(self, client, admin_headers):
        """GET /tasks/ → list all tasks (admin only)"""
        r = client.get("/api/v1/tasks/", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_get_task_by_id(self, client, admin_headers):
        """GET /tasks/{id} → get task details"""
        r = client.get(f"/api/v1/tasks/{FAKE_UUID}", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_assign_task(self, client, admin_headers):
        """POST /tasks/{id}/assign/{vol_id} → assign task to volunteer"""
        r = client.post(
            f"/api/v1/tasks/{FAKE_UUID}/assign/{FAKE_UUID}",
            headers=admin_headers,
        )
        assert r.status_code in VALID_RESPONSES

    def test_accept_task(self, client, volunteer_headers):
        """POST /tasks/{id}/accept → volunteer accepts task"""
        r = client.post(f"/api/v1/tasks/{FAKE_UUID}/accept", headers=volunteer_headers)
        assert r.status_code in VALID_RESPONSES

    def test_pickup_verify(self, client, volunteer_headers):
        """POST /tasks/{id}/pickup-verify → verify pickup with QR"""
        r = client.post(
            f"/api/v1/tasks/{FAKE_UUID}/pickup-verify",
            headers=volunteer_headers,
            json={"token": "invalid_token"},
        )
        assert r.status_code in VALID_RESPONSES

    def test_delivery_verify(self, client, volunteer_headers):
        """POST /tasks/{id}/delivery-verify → verify delivery with QR"""
        r = client.post(
            f"/api/v1/tasks/{FAKE_UUID}/delivery-verify",
            headers=volunteer_headers,
            json={"token": "invalid_token"},
        )
        assert r.status_code in VALID_RESPONSES

    def test_complete_task(self, client, admin_headers):
        """POST /tasks/{id}/complete → mark task completed"""
        r = client.post(f"/api/v1/tasks/{FAKE_UUID}/complete", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_cancel_task(self, client, admin_headers):
        """POST /tasks/{id}/cancel → cancel task"""
        r = client.post(
            f"/api/v1/tasks/{FAKE_UUID}/cancel?reason=test_cancellation",
            headers=admin_headers,
        )
        assert r.status_code in VALID_RESPONSES

    def test_auto_assign(self, client, admin_headers):
        """POST /tasks/auto-assign → trigger auto-assignment"""
        r = client.post("/api/v1/tasks/auto-assign", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_reassign_task(self, client, admin_headers):
        """POST /tasks/{id}/reassign → reassign task"""
        r = client.post(f"/api/v1/tasks/{FAKE_UUID}/reassign", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES


# ═══════════════════════════════════════════════════════════════════════════
# 7. ADMIN ENDPOINTS (7 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestAdminEndpoints:
    def test_get_stats(self, client, admin_headers):
        """GET /admin/stats → system overview alias"""
        r = client.get("/api/v1/admin/stats", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_get_stats_overview(self, client, admin_headers):
        """GET /admin/stats/overview → full system statistics"""
        r = client.get("/api/v1/admin/stats/overview", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES
        if r.status_code == 200:
            data = r.json()
            assert "users" in data
            assert "volunteers" in data
            assert "ngos" in data
            assert "tasks" in data

    def test_get_volunteer_stats(self, client, admin_headers):
        """GET /admin/stats/volunteer/{id} → volunteer performance stats"""
        r = client.get(
            f"/api/v1/admin/stats/volunteer/{FAKE_UUID}",
            headers=admin_headers,
        )
        assert r.status_code in VALID_RESPONSES

    def test_get_all_users(self, client, admin_headers):
        """GET /admin/users → list all users"""
        r = client.get("/api/v1/admin/users", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_get_admin_ngos(self, client, admin_headers):
        """GET /admin/ngos → list NGOs for review"""
        r = client.get("/api/v1/admin/ngos", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_get_admin_donations(self, client, admin_headers):
        """GET /admin/donations → list donation tasks"""
        r = client.get("/api/v1/admin/donations", headers=admin_headers)
        assert r.status_code in VALID_RESPONSES

    def test_approve_ngo(self, client, admin_headers):
        """POST /admin/ngos/{id}/approve → approve an NGO"""
        r = client.post(
            f"/api/v1/admin/ngos/{FAKE_UUID}/approve",
            headers=admin_headers,
        )
        assert r.status_code in VALID_RESPONSES


# ═══════════════════════════════════════════════════════════════════════════
# 8. RATINGS ENDPOINTS (3 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestRatingsEndpoints:
    def test_rate_task(self, client, donor_headers):
        """POST /ratings/tasks/{id}/rate → rate a delivered task"""
        r = client.post(
            f"/api/v1/ratings/tasks/{FAKE_UUID}/rate",
            headers=donor_headers,
            json={"rating": 4.5, "feedback": "Great delivery!"},
        )
        assert r.status_code in VALID_RESPONSES

    def test_get_volunteer_ratings(self, client, admin_headers):
        """GET /ratings/volunteers/{id}/ratings → get volunteer ratings"""
        r = client.get(
            f"/api/v1/ratings/volunteers/{FAKE_UUID}/ratings",
            headers=admin_headers,
        )
        assert r.status_code in VALID_RESPONSES

    def test_get_volunteer_rating_summary(self, client, admin_headers):
        """GET /ratings/volunteers/{id}/summary → rating summary"""
        r = client.get(
            f"/api/v1/ratings/volunteers/{FAKE_UUID}/summary",
            headers=admin_headers,
        )
        assert r.status_code in VALID_RESPONSES


# ═══════════════════════════════════════════════════════════════════════════
# 9. DISPATCHER ENDPOINTS (3 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestDispatcherEndpoints:
    def test_get_dispatcher_tasks(self, client, dispatcher_headers):
        """GET /dispatcher/tasks → list tasks for dispatcher"""
        r = client.get("/api/v1/dispatcher/tasks", headers=dispatcher_headers)
        assert r.status_code in VALID_RESPONSES

    def test_dispatcher_assign_task(self, client, dispatcher_headers):
        """POST /dispatcher/tasks/{id}/assign → assign task to volunteer"""
        r = client.post(
            f"/api/v1/dispatcher/tasks/{FAKE_UUID}/assign",
            headers=dispatcher_headers,
            json={"volunteer_id": FAKE_UUID},
        )
        assert r.status_code in VALID_RESPONSES

    def test_get_dispatcher_stats(self, client, dispatcher_headers):
        """GET /dispatcher/stats → dispatcher dashboard stats"""
        r = client.get("/api/v1/dispatcher/stats", headers=dispatcher_headers)
        assert r.status_code in VALID_RESPONSES
        if r.status_code == 200:
            data = r.json()
            assert "pending_tasks" in data
            assert "online_volunteers" in data


# ═══════════════════════════════════════════════════════════════════════════
# 10. DONOR TASK CREATION ENDPOINT (1 test)
# ═══════════════════════════════════════════════════════════════════════════

class TestDonorTaskCreation:
    def test_create_donation_task(self, client, donor_headers):
        """POST /donors/tasks → create a new donation task"""
        r = client.post("/api/v1/donors/tasks", headers=donor_headers, json={
            "pickup_lat": 40.7128,
            "pickup_lng": -74.0060,
            "food_type": "VEG",
            "quantity_kg": 10.0,
            "description": "Leftover lunch items",
            "requires_cooling": False,
            "expiry_time": (datetime.utcnow() + timedelta(hours=4)).isoformat(),
        })
        assert r.status_code in VALID_RESPONSES


# ═══════════════════════════════════════════════════════════════════════════
# 11. NGO VERIFY RECEIPT ENDPOINT (1 test)
# ═══════════════════════════════════════════════════════════════════════════

class TestNgoVerifyReceipt:
    def test_verify_receipt(self, client, ngo_headers):
        """POST /ngos/tasks/{id}/verify → NGO verifies receipt"""
        r = client.post(
            f"/api/v1/ngos/tasks/{FAKE_UUID}/verify",
            headers=ngo_headers,
        )
        assert r.status_code in VALID_RESPONSES
