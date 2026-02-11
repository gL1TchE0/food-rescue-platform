# 🧪 Unit Testing Report — Food Rescue Platform Backend

**Date:** 2026-02-12  
**Framework:** pytest 9.0.2  
**Database:** Supabase PostgreSQL  
**Total Tests:** 38  
**Result:** ✅ ALL 38 PASSED

This report details every test case executed, explaining exactly **what it checks** and **why it's important**.

---

## 1️⃣ Authentication Utilities (`tests/test_auth.py`)

These **Unit Tests** verify the core security functions in `auth.py` without needing the full API.

### 🔐 Password Hashing

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_get_password_hash_deterministic` | Checks if hashing the same password twice produces the **same output**. | Critical for verifying passwords later (hash matching). |
| `test_get_password_hash_is_hex` | Verifies the hash format is a **64-character hexadecimal string** (SHA-256). | Ensures compatibility with database storage fields. |
| `test_verify_password_correct` | verifying a **correct password** against its hash returns `True`. | The core mechanism for logging users in. |
| `test_verify_password_incorrect` | verifying a **wrong password** against a hash returns `False`. | Prevents unauthorized access with bad passwords. |

### 🎟 JWT Token Operations

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_create_access_token_returns_string` | calling `create_access_token` returns a **valid string**. | Ensures the login endpoint can actually return a token. |
| `test_decode_access_token_valid` | decoding a valid token returns correct data (email, user_id, role). | The API needs to trust who the user claims to be. |
| `test_decode_access_token_invalid` | decoding a **manipulated/garbage token** raises a 401 error. | security against attackers forging tokens. |
| `test_decode_access_token_expired` | decoding an **expired token** raises a 401 error. | Tokens must stop working after their 30-min lifetime. |
| `test_decode_access_token_missing_sub` | decoding a token without a "subject" (email) raises a 401 error. | Prevents malformed tokens from crashing the app. |

### 👤 User Authentication

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_authenticate_user_success` | `authenticate_user` returns the **User object** for valid credentials. | The database lookup and password check work together. |
| `test_authenticate_user_wrong_password` | `authenticate_user` returns **None** for a wrong password. | Login must fail securely. |
| `test_authenticate_user_nonexistent_email` | `authenticate_user` returns **None** for an unknown email. | Prevents logging in to non-existent accounts. |

---

## 2️⃣ Authentication Routes (`tests/test_routes_auth.py`)

These **Integration Tests** verify the actual API endpoints (HTTP requests).

### 🔑 Login Endpoint (`POST /api/auth/login`)

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_login_success` | Valid login returns HTTP **200 OK** and a JSON with `access_token`. | Users must be able to log in and get a token. |
| `test_login_wrong_password` | Wrong password returns HTTP **401 Unauthorized**. | Security: API rejects bad credentials. |
| `test_login_nonexistent_user` | Unknown email returns HTTP **401 Unauthorized**. | Security: API rejects unknown users. |

### 👤 Current User (`GET /api/auth/me`)

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_get_me_authenticated` | Request with a valid token returns the **logged-in user's details**. | The frontend needs to know who is logged in. |
| `test_get_me_unauthenticated` | Request **without a token** returns HTTP **401 Unauthorized**. | Protects user data from public access. |

### 🏢 NGO Endpoint (`GET /api/auth/ngo`)

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_get_ngo_details` | An **NGO user** can fetch their own NGO details. | NGOs need to see their profile info. |
| `test_get_ngo_non_ngo_user` | A **Donor/Volunteer** trying to access this gets HTTP **403 Forbidden**. | Role-Based Access Control (RBAC) is working. |

---

## 3️⃣ Donation Routes (`tests/test_routes_donations.py`)

These **Integration Tests** cover the main business logic: donating, claiming, and verifying food.

### 📦 Available Donations (`GET /api/donations/available`)

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_get_available_donations` | Returns a list containing donations with status **"AVAILABLE"**. | NGOs need to see what food is up for grabs. |
| `test_expired_donation_not_in_available` | Ensures **expired food** does NOT appear in the list. | Safety: Don't let NGOs claim spoiled food. |

### ➕ Create Donation (`POST /api/donations`)

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_create_donation` | Creating a donation returns HTTP **201 Created** and the correct data. | Donors must be able to submit food. |
| `test_create_donation_missing_fields` | Submitting without required fields (e.g., name) returns HTTP **422**. | Data integrity: Rejects incomplete forms. |

### 📋 Get All Donations (`GET /api/donations`)

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_get_all_donations` | Admin endpoint returns **all donations** regardless of status. | For admin dashboards/debugging. |

### 🔍 QR Verification (`GET /api/donations/{id}/verify`)

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_verify_donation_success` | Scanning a valid QR code returns **verification details**. | Volunteers need to verify food before pickup. |
| `test_verify_donation_not_found` | Scanning an invalid ID returns HTTP **404 Not Found**. | Handles bad/fake QR codes gracefully. |

### 🏷 Claim Donation (`PATCH /api/donations/{id}/status`)

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_claim_donation_success` | An NGO claiming food updates status to **"ASSIGNED"** and links their ID. | The core feature: Booking food. |
| `test_claim_already_assigned` | Trying to claim food that's **already taken** returns HTTP **400**. | Prevents double-booking race conditions. |
| `test_claim_expired_donation` | Trying to claim **expired food** returns HTTP **400**. | Safety: Blocks claiming bad food even if ID is known. |
| `test_claim_donation_unauthenticated` | Trying to claim **without logging in** returns HTTP **401**. | Only registered NGOs can claim food. |

### ✅ Pickup Verification (`PUT /api/donations/{id}/verify`)

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_verify_pickup_success` | The owning NGO verifying pickup updates status to **"COMPLETED"**. | Closes the loop: Food successfully rescued. |
| `test_verify_pickup_wrong_ngo` | **Another NGO** trying to verify pickup gets HTTP **403 Forbidden**. | Security: You can't verify someone else's pickup. |
| `test_verify_pickup_not_assigned` | Verifying a donation that hasn't been claimed yet returns HTTP **400/403**. | Logic check: Must claim before picking up. |

### ⚖️ Capacity & Multiple Location Logic

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_claim_exceeds_ngo_capacity` | Claiming a donation that exceeds the **NGO's total capacity** returns HTTP **403**. | Prevents hoarding/over-claiming beyond ability to store. |
| `test_claim_for_specific_branch` | Claiming for a **specific branch ID** works and assigns the branch. | Multi-location NGOs need to route food to specific sites. |
| `test_claim_exceeds_branch_capacity` | Claiming that exceeds a **single branch's capacity** returns HTTP **403**. | Even if NGO has space elsewhere, specific branch limits must be respected. |

---

## 4️⃣ Main App Routes (`tests/test_main.py`)

### 🌐 System Health

| Test Case | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| `test_root_returns_api_info` | Root URL (`/`) returns API name and version. | Basic connectivity check. |
| `test_health_check` | `/health` returns status **"healthy"**. | Used by monitoring tools (AWS, Docker) to check if app is alive. |

---

## 📊 Summary Statistics

- **Total Tests:** 38
- **Unit Tests:** 12
- **Integration Tests:** 26
- **Coverage:** Auth, Donations, Database Models, Security
