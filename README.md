# Food Rescue NGO Platform

A mobile-first platform for NGOs, donors and volunteers to coordinate safe food redistribution. This README documents implemented user stories, how they were implemented, database schema, tooling, and how the system works end-to-end.

**Note:** The codebase contains a FastAPI backend (`backend/`) and a Flutter mobile app (`lib/`). See the Backend README at [backend/README.md](backend/README.md) for API usage and quick-start commands.

## Implemented User Stories (Summary)

- **NGO registration with approval**: NGO signup implemented via the `POST /api/auth/register` endpoint. Registered NGOs receive an approval status (`PENDING` by default in models; demo auto-approves in routes). (See [backend/routes/auth.py](backend/routes/auth.py#L1))
- **Specify serving/storage capacity**: NGOs have a `storage_capacity` attribute used during claim capacity checks when claiming donations. (`NGO.storage_capacity` in [backend/models.py](backend/models.py#L18)).
- **Multiple operating locations**: NGO branches are implemented as `NGOBranch` records allowing multiple operating locations per NGO. (See [backend/models.py](backend/models.py#L36)).
- **NGO view & claim donations**: NGOs can list available donations (`GET /api/donations/available`) and claim them (`PATCH /api/donations/{id}/status`). Capacity and expiry checks are enforced in `backend/routes/donations.py`.
- **QR-based verification flow**: Donations produce QR-code verification flows (app shows QR; volunteers can verify using `GET /api/donations/{id}/verify`). NGOs confirm pickup using `PUT /api/donations/{id}/verify` which sets status to `COMPLETED`.

### Partial / Future Work
- **License / document upload for NGO registration**: The registration flow exists, but a dedicated `license` file field and file-upload handling are not present in the current database models or endpoints.
- **Volunteer ID upload, availability, ratings, training videos, admin suspend**: The `User` role enum supports `VOLUNTEER`, but detailed volunteer features (ID upload, availability schedule, ratings, training content management, admin suspend flag) are not yet implemented in models or routes.

## Database Schema (Key Attributes)

The primary models and attributes are defined in `backend/models.py`:

- **NGO** (`ngos` table):
  - **id**: Integer (PK)
  - **name**: String
  - **email**: String (unique)
  - **phone**: String
  - **address**: String
  - **storage_capacity**: Float (kg) - *Used for capacity checks*
  - **approval_status**: Enum (`PENDING` / `APPROVED` / `REJECTED`)
  - **created_at**: DateTime

- **User** (`users` table):
  - **id**: Integer (PK)
  - **email**: String (unique)
  - **hashed_password**: String
  - **role**: Enum (`NGO`, `DONOR`, `VOLUNTEER`, `DISPATCHER`)
  - **ngo_id**: Integer (FK to `ngos.id`, optional)
  - **created_at**: DateTime

- **NGOBranch** (`ngo_branches` table):
  - **id**: Integer (PK)
  - **ngo_id**: Integer (FK)
  - **name**: String
  - **address**: String
  - **storage_capacity**: Float (kg)
  - **latitude / longitude**: Float
  - **is_active**: Integer (1/0)

- **Donation** (`donations` table):
  - **id**: Integer (PK)
  - **donor_name**, **donor_phone**: String
  - **food_type**: Enum (`VEG`, `NON_VEG`, `VEGAN`, `MIXED`, `SNACK`)
  - **quantity**: Float (kg)
  - **address**: String
  - **expiry_time**: DateTime
  - **status**: Enum (`AVAILABLE`, `ASSIGNED`, `COMPLETED`, `CANCELLED`)
  - **ngo_id**: Integer (FK when claimed)
  - **branch_id**: Integer (FK to branch assigned)
  - **claimed_at**: DateTime

For full model definitions, see [backend/models.py](backend/models.py).

## Implementation Details

### Backend (FastAPI)
- **Authentication**: JWT-based auth in `backend/auth.py`. Users are created with hashed passwords (`bcrypt`).
- **NGO Registration**: `POST /api/auth/register` creates `NGO` and `User` records transactionally.
- **Donation Lifecycle**:
  1. **Create**: Donor submits to `POST /api/donations` (Status: `AVAILABLE`).
  2. **View**: NGOs fetch `GET /api/donations/available`.
  3. **Claim**: NGOs claim via `PATCH /api/donations/{id}/status` (Status: `ASSIGNED`). **Logic**: Enforces capacity limits (Total NGO capacity or Branch capacity) and checks expiry.
  4. **Verify**: Volunteer scans QR -> `GET /api/donations/{id}/verify`.
  5. **Complete**: NGO confirms receipt -> `PUT /api/donations/{id}/verify` (Status: `COMPLETED`).

### Frontend (Flutter)
- **Config**: `lib/config/api_config.dart` manages the backend URL.
- **Services**: `lib/services/donation_api_service.dart` handles API calls and token management.
- **Screens**:
  - `MyClaimsScreen`: Lists claimed donations and shows QR codes.
  - `DashboardScreen`: Shows NGO stats and available donations.
- **Widgets**: `ClaimedDonationCard` displays donation info and actions.

## Tools & Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy (ORM), Pydantic (Validation), Uvicorn (Server), PostgreSQL (Database).
- **Frontend**: Flutter, Dart, `http` (Networking), `shared_preferences` (Local Storage), `qr_flutter` (QR Generation).
- **Dev Tools**: VS Code, Android Emulator / Physical Device.

## How to Run

### 1. Backend
```bash
cd backend
# Create virtual env (optional but recommended)
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
python seed_data.py   # Optional: Seeds demo data
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend
1. **Configure IP**: Open `lib/config/api_config.dart` and set `baseUrl` to your computer's IP (e.g., `http://192.168.1.5:8000`) if running on a physical device, or `http://10.0.2.2:8000` for Android emulator.

2. **Run App**:
```bash
flutter pub get
flutter run
```

---
*Generated by GitHub Copilot*