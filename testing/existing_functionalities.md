# Existing Functionalities — Food Rescue Platform

> Auto-generated inventory of all implemented features as of Sprint 1.

---

## Backend (FastAPI)

### 1. Authentication (`/api/v1/auth`)

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | POST | `/register` | Register new user (auto-creates Donor/Volunteer/NGO profile based on role) |
| 2 | POST | `/login` | Login and get JWT access token (TEST_MODE only) |
| 3 | GET | `/me` | Get current authenticated user profile |

### 2. Donors (`/api/v1/donors`)

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 4 | GET | `/` | List all donors (requires auth) |
| 5 | GET | `/me` | Get current user's donor profile |
| 6 | PATCH | `/me` | Update current user's donor profile |
| 7 | GET | `/tasks` | Get all tasks created by current donor |
| 8 | POST | `/tasks` | Create a new donation task |
| 9 | GET | `/{donor_id}` | Get donor by ID |
| 10 | POST | `/` | Create a new donor profile |

### 3. NGOs (`/api/v1/ngos`)

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 11 | GET | `/` | List all NGOs (filterable by verification status) |
| 12 | GET | `/me` | Get current NGO profile |
| 13 | PATCH | `/me` | Update current NGO profile |
| 14 | GET | `/nearby-tasks` | Find nearby pending donation tasks (verified NGOs only) |
| 15 | GET | `/tasks` | Get all tasks assigned to current NGO |
| 16 | GET | `/claimed-tasks` | Alias for `/tasks` |
| 17 | POST | `/` | Create NGO profile |
| 18 | POST | `/tasks/{task_id}/claim` | NGO claims a pending task |
| 19 | POST | `/tasks/{task_id}/verify` | NGO verifies receipt/delivery of donation |
| 20 | GET | `/{ngo_id}` | Get NGO by ID |
| 21 | PATCH | `/{ngo_id}/verify` | Admin: Set NGO verification status |

### 4. Volunteers (`/api/v1/volunteers`)

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 22 | GET | `/` | List all volunteers (filterable by status) |
| 23 | GET | `/me` | Get current volunteer profile |
| 24 | PATCH | `/me` | Update current volunteer profile |
| 25 | GET | `/current-task` | Get volunteer's current assigned task |
| 26 | GET | `/task-history` | Get volunteer's completed task history |
| 27 | POST | `/` | Create volunteer profile |
| 28 | PATCH | `/location` | Update volunteer's GPS location |
| 29 | PATCH | `/status` | Update volunteer's availability status |
| 30 | POST | `/go-online` | Go online with GPS coordinates |
| 31 | POST | `/go-offline` | Go offline |
| 32 | GET | `/{volunteer_id}` | Get volunteer by ID |

### 5. Tasks (`/api/v1/tasks`)

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 33 | GET | `/` | List all tasks (admin only, filterable by status) |
| 34 | GET | `/{task_id}` | Get task details |
| 35 | POST | `/{task_id}/assign/{volunteer_id}` | Admin: manually assign task to volunteer |
| 36 | POST | `/{task_id}/accept` | Volunteer accepts assigned task |
| 37 | POST | `/{task_id}/pickup-verify` | Verify pickup via QR token |
| 38 | POST | `/{task_id}/delivery-verify` | Verify delivery via QR token |
| 39 | POST | `/{task_id}/complete` | Admin: mark delivered task as completed |
| 40 | POST | `/{task_id}/cancel` | Cancel task (admin or task's donor) |
| 41 | POST | `/auto-assign` | Admin: trigger auto-assignment for all pending tasks |
| 42 | POST | `/{task_id}/reassign` | Admin: reassign task to different volunteer |

### 6. Admin (`/api/v1/admin`)

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 43 | GET | `/stats` | Get system overview (alias) |
| 44 | GET | `/stats/overview` | Full system statistics (users, volunteers, NGOs, tasks) |
| 45 | GET | `/stats/volunteer/{volunteer_id}` | Get detailed stats for a specific volunteer |
| 46 | GET | `/users` | List all users (filterable by role) |
| 47 | GET | `/ngos` | List NGOs for admin review |
| 48 | GET | `/donations` | List all donation tasks |
| 49 | POST | `/ngos/{ngo_id}/approve` | Approve an NGO |

### 7. Ratings (`/api/v1/ratings`)

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 50 | POST | `/tasks/{task_id}/rate` | Rate a delivered task (donor/NGO rates volunteer) |
| 51 | GET | `/volunteers/{volunteer_id}/ratings` | Get all ratings for a volunteer |
| 52 | GET | `/volunteers/{volunteer_id}/summary` | Get rating summary (average, distribution) |

### 8. Dispatcher (`/api/v1/dispatcher`)

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 53 | GET | `/tasks` | Get all tasks for dispatcher view |
| 54 | POST | `/tasks/{task_id}/assign` | Assign task to volunteer |
| 55 | GET | `/stats` | Get dispatcher dashboard stats |

### 9. Root Endpoints

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 56 | GET | `/` | Root — returns welcome message |
| 57 | GET | `/health` | Health check — reports DB, Redis, WebSocket status |

### 10. Utility Modules (Backend)

| Module | Description |
|--------|-------------|
| `utils/auth.py` | JWT creation/verification, password hashing, Clerk integration, `get_current_user` dependency |
| `utils/qr_generator.py` | QR token generation for pickup/delivery verification |
| `utils/redis_manager.py` | Redis connection manager for caching |
| `utils/serialize.py` | PostGIS geometry → JSON serialization helpers |
| `utils/socket_manager.py` | Socket.IO manager for real-time volunteer tracking & task updates |
| `utils/spatial.py` | PostGIS point creation, coordinate extraction, nearby-task search |

---

## Frontend (Next.js + TypeScript)

### Pages

| Page | File | Description |
|------|------|-------------|
| Home | `src/app/page.tsx` | Landing page with hero, features, ecosystem sections |
| Login | `src/app/login/page.tsx` | Email/password login form |
| Register | `src/app/register/page.tsx` | Registration form with role selection (Donor/Volunteer/NGO) |
| Admin Dashboard | `src/app/dashboard/admin/page.tsx` | Admin panel |
| Dispatcher Dashboard | `src/app/dashboard/dispatcher/page.tsx` | Dispatcher panel |
| NGO Dashboard | `src/app/dashboard/ngo/page.tsx` | NGO panel |

### Components (`src/components/`)

| Component | Description |
|-----------|-------------|
| `Navbar.tsx` | Navigation bar |
| `HeroSection.tsx` | Landing page hero banner |
| `FeaturesSection.tsx` | Platform features showcase |
| `IntelligentDistribution.tsx` | AI distribution info section |
| `EcosystemSection.tsx` | Platform ecosystem visualization |
| `CTASection.tsx` | Call-to-action section |
| `TrustedByMarquee.tsx` | Partner logos marquee |
| `Footer.tsx` | Page footer |
| `ParallaxBackground.tsx` | Animated background |
| `RevealOnScroll.tsx` | Scroll-triggered animations |

### Library (`src/lib/`)

| Module | Description |
|--------|-------------|
| `api-config.ts` | API base URL and endpoint constants |
| `api-service.ts` | `ApiService` class — HTTP client for all backend calls |
| `auth-context.tsx` | `AuthProvider` context — login/logout/role-based routing |
| `toast-context.tsx` | Toast notification provider |
| `websocket-service.ts` | Socket.IO client for real-time updates |

---

## Database Models (SQLAlchemy + PostGIS)

| Model | Table | Key Fields |
|-------|-------|------------|
| `User` | `users` | id, clerk_user_id, email, phone, full_name, role, is_active |
| `Donor` | `donors` | id, user_id, organization_name, address, location (PostGIS), qr_token |
| `NGO` | `ngos` | id, user_id, organization_name, license_number, verification_status, location |
| `NGOBranch` | `ngo_branches` | id, ngo_id, branch_name, address, location |
| `Volunteer` | `volunteers` | id, user_id, vehicle_type, status, current_location, current_task_id |
| `Task` | `tasks` | id, donor_id, ngo_id, volunteer_id, pickup/drop locations, food_type, status, tokens |
| `TrackingSession` | `tracking_sessions` | id, task_id, volunteer_id, route_polyline, timestamps |
| `TaskException` | `task_exceptions` | id, task_id, volunteer_id, issue_type, description |
| `PerformanceStat` | `performance_stats` | id, volunteer_id, task_id, on_time, rating, feedback |
| `AdminAction` | `admin_actions` | id, admin_user_id, target_user_id, action_type, reason |

### Enums

| Enum | Values |
|------|--------|
| `UserRole` | DONOR, NGO, VOLUNTEER, ADMIN, DISPATCHER |
| `FoodType` | VEG, NON_VEG, VEGAN, MIXED |
| `TaskStatus` | PENDING, ASSIGNED, PICKED_UP, IN_TRANSIT, DELIVERED, COMPLETED, CANCELLED |
| `VolunteerStatus` | ONLINE, BUSY, OFFLINE |
| `VehicleType` | BIKE, SCOOTER, CAR, VAN |
| `VerificationStatus` | PENDING, VERIFIED, REJECTED, SUSPENDED |
