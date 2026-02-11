# 🧪 Unit Testing Report — Food Rescue Platform Backend

**Date:** 2026-02-12  
**Framework:** pytest 9.0.2  
**Database:** Supabase PostgreSQL  
**Python:** 3.13.2  
**Total Tests:** 35  
**Result:** ✅ ALL 35 PASSED (84.32 seconds)

---

## 📋 Table of Contents

1. [Test Summary](#test-summary)
2. [Detailed Test Results](#detailed-test-results)
3. [Testing Methodology](#testing-methodology)
4. [How to Run the Tests](#how-to-run-the-tests)
5. [File Structure](#file-structure)

---

## Test Summary

| Test File | Module Tested | Tests | Status |
|-----------|--------------|-------|--------|
| `tests/test_auth.py` | `auth.py` (Password & JWT utilities) | 12 | ✅ All Passed |
| `tests/test_routes_auth.py` | `routes/auth.py` (Auth API endpoints) | 7 | ✅ All Passed |
| `tests/test_routes_donations.py` | `routes/donations.py` (Donation API endpoints) | 14 | ✅ All Passed |
| `tests/test_main.py` | `main.py` (Root & Health endpoints) | 2 | ✅ All Passed |
| **Total** | | **35** | **✅ All Passed** |

---

## Detailed Test Results

### 1. `test_auth.py` — Authentication Utilities (12 Tests)

These tests verify the core authentication functions in `auth.py`.

#### Password Hashing (4 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 1 | `test_get_password_hash_deterministic` | Same password always produces the same hash | Hash of "hello" called twice → both are equal | ✅ PASSED |
| 2 | `test_get_password_hash_is_hex` | Hash output format is valid SHA-256 | Returns a 64-character lowercase hex string | ✅ PASSED |
| 3 | `test_verify_password_correct` | Correct password verification | `verify_password("mypassword", hash)` → `True` | ✅ PASSED |
| 4 | `test_verify_password_incorrect` | Wrong password rejection | `verify_password("wrongpassword", hash)` → `False` | ✅ PASSED |

#### JWT Token Operations (5 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 5 | `test_create_access_token_returns_string` | Token creation | Returns a non-empty string | ✅ PASSED |
| 6 | `test_decode_access_token_valid` | Decoding a valid token | Returns `TokenData` with correct email, user_id, role | ✅ PASSED |
| 7 | `test_decode_access_token_invalid` | Decoding a garbage token | Raises `HTTPException` with status 401 | ✅ PASSED |
| 8 | `test_decode_access_token_expired` | Decoding an expired token | Raises `HTTPException` with status 401 | ✅ PASSED |
| 9 | `test_decode_access_token_missing_sub` | Token without email claim | Raises `HTTPException` with status 401 | ✅ PASSED |

#### User Authentication (3 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 10 | `test_authenticate_user_success` | Valid email + password login | Returns the `User` object | ✅ PASSED |
| 11 | `test_authenticate_user_wrong_password` | Correct email, wrong password | Returns `None` | ✅ PASSED |
| 12 | `test_authenticate_user_nonexistent_email` | Email not in database | Returns `None` | ✅ PASSED |

---

### 2. `test_routes_auth.py` — Authentication API Routes (7 Tests)

These tests verify the auth API endpoints using FastAPI's `TestClient`.

#### POST `/api/auth/login` (3 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 1 | `test_login_success` | Login with valid credentials | Status 200 + JSON with `access_token` and `token_type: "bearer"` | ✅ PASSED |
| 2 | `test_login_wrong_password` | Login with wrong password | Status 401 Unauthorized | ✅ PASSED |
| 3 | `test_login_nonexistent_user` | Login with non-existent email | Status 401 Unauthorized | ✅ PASSED |

#### GET `/api/auth/me` (2 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 4 | `test_get_me_authenticated` | Fetch user info with valid JWT | Status 200 + user email and role in response | ✅ PASSED |
| 5 | `test_get_me_unauthenticated` | Fetch user info without token | Status 401 Unauthorized | ✅ PASSED |

#### GET `/api/auth/ngo` (2 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 6 | `test_get_ngo_details` | NGO user fetches their NGO info | Status 200 + NGO name and approval_status | ✅ PASSED |
| 7 | `test_get_ngo_non_ngo_user` | Non-NGO (DONOR) user tries to access NGO endpoint | Status 403 Forbidden | ✅ PASSED |

---

### 3. `test_routes_donations.py` — Donation API Routes (14 Tests)

These tests verify all donation-related API endpoints.

#### GET `/api/donations/available` (2 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 1 | `test_get_available_donations` | Fetch available donations list | Status 200 + list containing the sample donation | ✅ PASSED |
| 2 | `test_expired_donation_not_in_available` | Expired donations excluded | Status 200 + expired donation NOT in the list | ✅ PASSED |

#### POST `/api/donations` (2 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 3 | `test_create_donation` | Create a new donation | Status 201 + donation with status "AVAILABLE" | ✅ PASSED |
| 4 | `test_create_donation_missing_fields` | Submit incomplete data | Status 422 Unprocessable Entity | ✅ PASSED |

#### GET `/api/donations` (1 test)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 5 | `test_get_all_donations` | Fetch all donations | Status 200 + list containing the sample donation | ✅ PASSED |

#### GET `/api/donations/{id}/verify` — QR Verification (2 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 6 | `test_verify_donation_success` | Verify an existing donation | Status 200 + `verified: true` | ✅ PASSED |
| 7 | `test_verify_donation_not_found` | Verify non-existent donation | Status 404 Not Found | ✅ PASSED |

#### PATCH `/api/donations/{id}/status` — Claiming (4 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 8 | `test_claim_donation_success` | Approved NGO claims available donation | Status 200 + status changes to "ASSIGNED" | ✅ PASSED |
| 9 | `test_claim_already_assigned` | Claim a donation already assigned | Status 400 Bad Request | ✅ PASSED |
| 10 | `test_claim_expired_donation` | Claim an expired donation | Status 400 Bad Request | ✅ PASSED |
| 11 | `test_claim_donation_unauthenticated` | Claim without auth token | Status 401 Unauthorized | ✅ PASSED |

#### PUT `/api/donations/{id}/verify` — Pickup Verification (3 tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 12 | `test_verify_pickup_success` | NGO verifies own donation pickup | Status 200 + status changes to "COMPLETED" | ✅ PASSED |
| 13 | `test_verify_pickup_wrong_ngo` | Different NGO tries to verify | Status 403 Forbidden | ✅ PASSED |
| 14 | `test_verify_pickup_not_assigned` | Verify a non-ASSIGNED donation | Status 400 or 403 (depends on check order) | ✅ PASSED |

---

### 4. `test_main.py` — Application Endpoints (2 Tests)

| # | Test Name | What It Tests | Expected Outcome | Result |
|---|-----------|--------------|------------------|--------|
| 1 | `test_root_returns_api_info` | `GET /` root endpoint | Status 200 + message, version, status fields | ✅ PASSED |
| 2 | `test_health_check` | `GET /health` health check | Status 200 + `status: "healthy"` | ✅ PASSED |

---

## Testing Methodology

### 1. Technology Stack

- **pytest** — test runner and assertion framework
- **FastAPI TestClient** (powered by `httpx`) — simulates HTTP requests to the API without starting a real server
- **SQLAlchemy** — ORM used to interact with the Supabase PostgreSQL database

### 2. Database Strategy: Transaction Rollback

Instead of using a separate test database, we connect to the **same Supabase PostgreSQL** database but wrap each test in a database transaction that is **rolled back** after the test completes.

```
┌─────────────────────────────────────────┐
│  Test starts                             │
│  ├── Open DB connection                  │
│  ├── BEGIN TRANSACTION                   │
│  ├── Insert test data (NGO, User, etc.)  │
│  ├── Run test assertions                 │
│  ├── ROLLBACK TRANSACTION ← nothing saved│
│  └── Close connection                    │
└─────────────────────────────────────────┘
```

**Why this approach?**
- ✅ Tests run against the real PostgreSQL database (same constraints, types, FK checks)
- ✅ No test data pollutes the production database
- ✅ Each test is fully isolated from others
- ✅ No need to set up a separate test database

### 3. Test Fixtures (`conftest.py`)

We use **pytest fixtures** to create reusable test data:

| Fixture | What It Creates |
|---------|----------------|
| `db_session` | A SQLAlchemy session bound to a rolled-back transaction |
| `client` | FastAPI `TestClient` with `get_db` overridden to use the test session |
| `sample_ngo` | An approved NGO with 500kg storage capacity |
| `sample_user` | An NGO user linked to `sample_ngo` with password "password123" |
| `donor_user` | A DONOR user (not an NGO) |
| `sample_donation` | An AVAILABLE donation expiring in 5 hours |
| `expired_donation` | An AVAILABLE donation that expired 1 hour ago |
| `auth_headers` | `Authorization: Bearer <JWT>` headers for `sample_user` |
| `donor_auth_headers` | `Authorization: Bearer <JWT>` headers for `donor_user` |

### 4. Dependency Injection Override

FastAPI uses dependency injection for `get_db()`. In tests, we override this so every route handler uses our test session (which will be rolled back):

```python
app.dependency_overrides[get_db] = _override_get_db
```

### 5. Test Categories

| Category | Type | Description |
|----------|------|-------------|
| **Unit Tests** | Pure function tests | Test individual functions (`get_password_hash`, `verify_password`, `create_access_token`, `decode_access_token`) without needing a database |
| **Integration Tests** | API endpoint tests | Test full request→response cycle through FastAPI routes, including database operations, authentication, and business logic |

---

## How to Run the Tests

### Prerequisites

Make sure pytest and httpx are installed:
```bash
d:\look\backend\venv\Scripts\python.exe -m pip install pytest httpx email-validator
```

### Run all tests
```bash
cd d:\look\backend
d:\look\backend\venv\Scripts\python.exe -m pytest tests/ -v
```

### Run a specific test file
```bash
d:\look\backend\venv\Scripts\python.exe -m pytest tests/test_auth.py -v
d:\look\backend\venv\Scripts\python.exe -m pytest tests/test_routes_donations.py -v
```

### Run a specific test class or test
```bash
d:\look\backend\venv\Scripts\python.exe -m pytest tests/test_auth.py::TestPasswordHashing -v
d:\look\backend\venv\Scripts\python.exe -m pytest tests/test_auth.py::TestJWTTokens::test_decode_access_token_expired -v
```

---

## File Structure

```
backend/
├── tests/
│   ├── __init__.py              # Makes tests a Python package
│   ├── conftest.py              # Shared fixtures (DB session, test data, auth headers)
│   ├── test_auth.py             # 12 tests — password hashing, JWT, authenticate_user
│   ├── test_routes_auth.py      # 7 tests  — login, /me, /ngo endpoints
│   ├── test_routes_donations.py # 14 tests — available, create, claim, verify, pickup
│   └── test_main.py             # 2 tests  — root and health check
├── pytest.ini                   # Pytest configuration
├── auth.py                      # ← tested
├── routes/
│   ├── auth.py                  # ← tested
│   └── donations.py             # ← tested
├── main.py                      # ← tested
├── models.py                    # Used by tests (ORM models)
├── schemas.py                   # Used by tests (Pydantic schemas)
└── database.py                  # Used by tests (DB connection)
```

---

## Raw Test Output

```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.0.2, pluggy-1.6.0
rootdir: D:\look\backend
configfile: pytest.ini
plugins: anyio-4.12.1

tests/test_auth.py::TestPasswordHashing::test_get_password_hash_deterministic PASSED [  2%]
tests/test_auth.py::TestPasswordHashing::test_get_password_hash_is_hex PASSED [  5%]
tests/test_auth.py::TestPasswordHashing::test_verify_password_correct PASSED [  8%]
tests/test_auth.py::TestPasswordHashing::test_verify_password_incorrect PASSED [ 11%]
tests/test_auth.py::TestJWTTokens::test_create_access_token_returns_string PASSED [ 14%]
tests/test_auth.py::TestJWTTokens::test_decode_access_token_valid PASSED [ 17%]
tests/test_auth.py::TestJWTTokens::test_decode_access_token_invalid PASSED [ 20%]
tests/test_auth.py::TestJWTTokens::test_decode_access_token_expired PASSED [ 22%]
tests/test_auth.py::TestJWTTokens::test_decode_access_token_missing_sub PASSED [ 25%]
tests/test_auth.py::TestAuthenticateUser::test_authenticate_user_success PASSED [ 28%]
tests/test_auth.py::TestAuthenticateUser::test_authenticate_user_wrong_password PASSED [ 31%]
tests/test_auth.py::TestAuthenticateUser::test_authenticate_user_nonexistent_email PASSED [ 34%]
tests/test_main.py::TestRootEndpoint::test_root_returns_api_info PASSED  [ 37%]
tests/test_main.py::TestHealthCheck::test_health_check PASSED            [ 40%]
tests/test_routes_auth.py::TestLogin::test_login_success PASSED          [ 42%]
tests/test_routes_auth.py::TestLogin::test_login_wrong_password PASSED   [ 45%]
tests/test_routes_auth.py::TestLogin::test_login_nonexistent_user PASSED [ 48%]
tests/test_routes_auth.py::TestGetMe::test_get_me_authenticated PASSED   [ 51%]
tests/test_routes_auth.py::TestGetMe::test_get_me_unauthenticated PASSED [ 54%]
tests/test_routes_auth.py::TestGetNGO::test_get_ngo_details PASSED       [ 57%]
tests/test_routes_auth.py::TestGetNGO::test_get_ngo_non_ngo_user PASSED  [ 60%]
tests/test_routes_donations.py::TestAvailableDonations::test_get_available_donations PASSED [ 62%]
tests/test_routes_donations.py::TestAvailableDonations::test_expired_donation_not_in_available PASSED [ 65%]
tests/test_routes_donations.py::TestCreateDonation::test_create_donation PASSED [ 68%]
tests/test_routes_donations.py::TestCreateDonation::test_create_donation_missing_fields PASSED [ 71%]
tests/test_routes_donations.py::TestGetAllDonations::test_get_all_donations PASSED [ 74%]
tests/test_routes_donations.py::TestVerifyDonation::test_verify_donation_success PASSED [ 77%]
tests/test_routes_donations.py::TestVerifyDonation::test_verify_donation_not_found PASSED [ 80%]
tests/test_routes_donations.py::TestClaimDonation::test_claim_donation_success PASSED [ 82%]
tests/test_routes_donations.py::TestClaimDonation::test_claim_already_assigned PASSED [ 85%]
tests/test_routes_donations.py::TestClaimDonation::test_claim_expired_donation PASSED [ 88%]
tests/test_routes_donations.py::TestClaimDonation::test_claim_donation_unauthenticated PASSED [ 91%]
tests/test_routes_donations.py::TestVerifyPickup::test_verify_pickup_success PASSED [ 94%]
tests/test_routes_donations.py::TestVerifyPickup::test_verify_pickup_wrong_ngo PASSED [ 97%]
tests/test_routes_donations.py::TestVerifyPickup::test_verify_pickup_not_assigned PASSED [100%]
================= 35 passed, 78 warnings in 84.32s (0:01:24) ==================
```
