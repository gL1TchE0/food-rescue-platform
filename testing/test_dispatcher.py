"""
Dispatcher Role - Exclusive Test Suite
20 tests covering all dispatcher API endpoints, access control, edge cases,
and interaction with task/volunteer workflows.

Run with:  python -m pytest testing/test_dispatcher.py -v --tb=short
"""
import pytest
import sys
import os
import uuid
import time
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

from main import fastapi_app
from database import Base, get_db
from models import (
    User, UserRole, Volunteer, VolunteerStatus, Task, TaskStatus,
    Donor, NGO, FoodType, VerificationStatus, VehicleType
)
from utils.auth import create_access_token

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"connect_timeout": 10},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

FAKE_UUID = "00000000-0000-0000-0000-000000000000"
DB_CONNECT_RETRIES = 3
DB_CONNECT_RETRY_DELAY = 2


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def db():
    """Database session with transaction isolation and retry logic."""
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


def _make_user(db, role, prefix):
    uid = uuid.uuid4().hex[:8]
    user = User(
        email=f"{prefix}_{uid}@test.com",
        phone_number=f"+1555{uid[:7]}",
        full_name=f"{prefix.title()} Test User",
        role=role,
        clerk_user_id=f"user_{prefix}_{uid}",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_headers(user):
    token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "role": user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def dispatcher_user(db):
    return _make_user(db, UserRole.DISPATCHER, "dispatcher")

@pytest.fixture
def dispatcher_headers(dispatcher_user):
    return _make_headers(dispatcher_user)

@pytest.fixture
def admin_user(db):
    return _make_user(db, UserRole.ADMIN, "admin")

@pytest.fixture
def admin_headers(admin_user):
    return _make_headers(admin_user)

@pytest.fixture
def donor_user(db):
    return _make_user(db, UserRole.DONOR, "donor")

@pytest.fixture
def donor_headers(donor_user):
    return _make_headers(donor_user)

@pytest.fixture
def volunteer_user(db):
    return _make_user(db, UserRole.VOLUNTEER, "volunteer")

@pytest.fixture
def volunteer_headers(volunteer_user):
    return _make_headers(volunteer_user)

@pytest.fixture
def ngo_user(db):
    return _make_user(db, UserRole.NGO, "ngo")

@pytest.fixture
def ngo_headers(ngo_user):
    return _make_headers(ngo_user)


# ═══════════════════════════════════════════════════════════════════════════
# TEST 1 - Dispatcher can view all tasks
# ═══════════════════════════════════════════════════════════════════════════

class TestDispatcherViewTasks:

    def test_dispatcher_can_list_tasks(self, client, dispatcher_headers):
        """Dispatcher calls GET /dispatcher/tasks and receives a list."""
        r = client.get("/api/v1/dispatcher/tasks", headers=dispatcher_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ═══════════════════════════════════════════════════════════════════════════
# TEST 2 - Dispatcher tasks response is a list even when empty
# ═══════════════════════════════════════════════════════════════════════════

    def test_dispatcher_tasks_returns_list_type(self, client, dispatcher_headers):
        """The tasks endpoint always returns a JSON array."""
        r = client.get("/api/v1/dispatcher/tasks", headers=dispatcher_headers)
        assert r.status_code == 200
        data = r.json()
        assert type(data) is list


# ═══════════════════════════════════════════════════════════════════════════
# TEST 3 - Admin can also access dispatcher tasks endpoint
# ═══════════════════════════════════════════════════════════════════════════

    def test_admin_can_access_dispatcher_tasks(self, client, admin_headers):
        """Admin role also has access to dispatcher endpoints."""
        r = client.get("/api/v1/dispatcher/tasks", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ═══════════════════════════════════════════════════════════════════════════
# TEST 4 - Donor cannot access dispatcher tasks
# ═══════════════════════════════════════════════════════════════════════════

class TestDispatcherAccessControl:

    def test_donor_cannot_access_dispatcher_tasks(self, client, donor_headers):
        """A donor role user should be denied access to dispatcher endpoints."""
        r = client.get("/api/v1/dispatcher/tasks", headers=donor_headers)
        assert r.status_code == 403

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 5 - Volunteer cannot access dispatcher tasks
    # ═══════════════════════════════════════════════════════════════════════

    def test_volunteer_cannot_access_dispatcher_tasks(self, client, volunteer_headers):
        """A volunteer role user should be denied access to dispatcher endpoints."""
        r = client.get("/api/v1/dispatcher/tasks", headers=volunteer_headers)
        assert r.status_code == 403

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 6 - NGO cannot access dispatcher tasks
    # ═══════════════════════════════════════════════════════════════════════

    def test_ngo_cannot_access_dispatcher_tasks(self, client, ngo_headers):
        """An NGO role user should be denied access to dispatcher endpoints."""
        r = client.get("/api/v1/dispatcher/tasks", headers=ngo_headers)
        assert r.status_code == 403

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 7 - Unauthenticated user cannot access dispatcher tasks
    # ═══════════════════════════════════════════════════════════════════════

    def test_unauthenticated_user_denied(self, client):
        """A request with no auth token should be rejected."""
        r = client.get("/api/v1/dispatcher/tasks")
        assert r.status_code == 401

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 8 - Invalid token is rejected
    # ═══════════════════════════════════════════════════════════════════════

    def test_invalid_token_rejected(self, client):
        """A request with a garbage token should be rejected."""
        r = client.get(
            "/api/v1/dispatcher/tasks",
            headers={"Authorization": "Bearer invalid_token_garbage_12345"},
        )
        assert r.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# TEST 9 - Dispatcher can view dashboard stats
# ═══════════════════════════════════════════════════════════════════════════

class TestDispatcherStats:

    def test_dispatcher_can_view_stats(self, client, dispatcher_headers):
        """Dispatcher calls GET /dispatcher/stats and receives dashboard data."""
        r = client.get("/api/v1/dispatcher/stats", headers=dispatcher_headers)
        assert r.status_code == 200

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 10 - Stats contain pending tasks count
    # ═══════════════════════════════════════════════════════════════════════

    def test_stats_contain_pending_tasks(self, client, dispatcher_headers):
        """The stats response must include the pending_tasks field."""
        r = client.get("/api/v1/dispatcher/stats", headers=dispatcher_headers)
        assert r.status_code == 200
        assert "pending_tasks" in r.json()

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 11 - Stats contain active tasks count
    # ═══════════════════════════════════════════════════════════════════════

    def test_stats_contain_active_tasks(self, client, dispatcher_headers):
        """The stats response must include the active_tasks field."""
        r = client.get("/api/v1/dispatcher/stats", headers=dispatcher_headers)
        assert r.status_code == 200
        assert "active_tasks" in r.json()

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 12 - Stats contain completed today count
    # ═══════════════════════════════════════════════════════════════════════

    def test_stats_contain_completed_today(self, client, dispatcher_headers):
        """The stats response must include the completed_today field."""
        r = client.get("/api/v1/dispatcher/stats", headers=dispatcher_headers)
        assert r.status_code == 200
        assert "completed_today" in r.json()

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 13 - Stats contain online volunteers count
    # ═══════════════════════════════════════════════════════════════════════

    def test_stats_contain_online_volunteers(self, client, dispatcher_headers):
        """The stats response must include the online_volunteers field."""
        r = client.get("/api/v1/dispatcher/stats", headers=dispatcher_headers)
        assert r.status_code == 200
        assert "online_volunteers" in r.json()

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 14 - Stats contain total volunteers count
    # ═══════════════════════════════════════════════════════════════════════

    def test_stats_contain_total_volunteers(self, client, dispatcher_headers):
        """The stats response must include the total_volunteers field."""
        r = client.get("/api/v1/dispatcher/stats", headers=dispatcher_headers)
        assert r.status_code == 200
        assert "total_volunteers" in r.json()

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 15 - Stats values are non-negative integers
    # ═══════════════════════════════════════════════════════════════════════

    def test_stats_values_are_non_negative(self, client, dispatcher_headers):
        """All stat counts should be zero or positive integers."""
        r = client.get("/api/v1/dispatcher/stats", headers=dispatcher_headers)
        assert r.status_code == 200
        data = r.json()
        for key in ["pending_tasks", "active_tasks", "completed_today", "online_volunteers", "total_volunteers"]:
            assert isinstance(data[key], int)
            assert data[key] >= 0

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 16 - Donor cannot access dispatcher stats
    # ═══════════════════════════════════════════════════════════════════════

    def test_donor_cannot_access_stats(self, client, donor_headers):
        """Donor role should be denied access to dispatcher stats."""
        r = client.get("/api/v1/dispatcher/stats", headers=donor_headers)
        assert r.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# TEST 17 - Dispatcher assign task with non-existent task returns 404
# ═══════════════════════════════════════════════════════════════════════════

class TestDispatcherAssignTask:

    def test_assign_nonexistent_task_returns_404(self, client, dispatcher_headers):
        """Assigning a task that does not exist should return 404."""
        r = client.post(
            f"/api/v1/dispatcher/tasks/{FAKE_UUID}/assign",
            headers=dispatcher_headers,
            json={"volunteer_id": FAKE_UUID},
        )
        assert r.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 18 - Donor cannot assign tasks via dispatcher endpoint
    # ═══════════════════════════════════════════════════════════════════════

    def test_donor_cannot_assign_task(self, client, donor_headers):
        """Donor role should be denied access to the assign endpoint."""
        r = client.post(
            f"/api/v1/dispatcher/tasks/{FAKE_UUID}/assign",
            headers=donor_headers,
            json={"volunteer_id": FAKE_UUID},
        )
        assert r.status_code == 403

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 19 - Assign with missing volunteer_id returns 422
    # ═══════════════════════════════════════════════════════════════════════

    def test_assign_missing_volunteer_id_returns_422(self, client, dispatcher_headers):
        """Sending an assign request without volunteer_id should return 422."""
        r = client.post(
            f"/api/v1/dispatcher/tasks/{FAKE_UUID}/assign",
            headers=dispatcher_headers,
            json={},
        )
        assert r.status_code == 422

    # ═══════════════════════════════════════════════════════════════════════
    # TEST 20 - Admin can also assign tasks via dispatcher endpoint
    # ═══════════════════════════════════════════════════════════════════════

    def test_admin_can_assign_via_dispatcher(self, client, admin_headers):
        """Admin role should also be able to use the dispatcher assign endpoint."""
        r = client.post(
            f"/api/v1/dispatcher/tasks/{FAKE_UUID}/assign",
            headers=admin_headers,
            json={"volunteer_id": FAKE_UUID},
        )
        # Should get 404 (task not found) not 403 (forbidden) since admin has access
        assert r.status_code == 404
