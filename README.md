# 🍲 SurplusSync — Food Rescue Platform

**SurplusSync** is a full-stack food rescue platform that connects surplus food donors with NGOs and volunteers. This branch (`user_authentication-Eswar`) implements a complete **user authentication system** with **two-factor authentication (2FA)** via email OTP.

---

## 🔐 User Authentication

### Overview

The authentication system provides secure, role-based access control with a two-step verification process:

1. **Registration** — User signs up with name, email, phone, password, and role → receives a 6-digit OTP via email.
2. **OTP Verification** — User enters the OTP to activate their account and receive a JWT access token.
3. **Login** — User enters credentials → receives a new OTP → verifies OTP to get a fresh JWT token.

### User Roles

| Role         | Description                              |
|--------------|------------------------------------------|
| `ADMIN`      | Platform administrator                   |
| `DISPATCHER` | Coordinates food pickups and deliveries  |
| `NGO`        | Non-profit organizations receiving food  |
| `VOLUNTEER`  | Volunteers for pickups and deliveries    |
| `DONOR`      | Food donors (restaurants, events, etc.)  |

### Auth Flow Diagram

```
┌──────────────┐    POST /api/auth/register    ┌──────────────┐
│   Sign Up    │ ─────────────────────────────► │  Save User   │
│   Screen     │                                │  (unverified)│
└──────┬───────┘                                └──────┬───────┘
       │                                               │
       │                                        Send OTP Email
       │                                               │
       ▼                                               ▼
┌──────────────┐    POST /api/auth/verify-otp   ┌──────────────┐
│  OTP Screen  │ ─────────────────────────────► │ Verify & Get │
│  (6 digits)  │                                │  JWT Token   │
└──────────────┘                                └──────────────┘

┌──────────────┐    POST /api/auth/login        ┌──────────────┐
│   Login      │ ─────────────────────────────► │ Verify Creds │
│   Screen     │                                │ + Send OTP   │
└──────┬───────┘                                └──────┬───────┘
       │                                               │
       ▼                                               ▼
┌──────────────┐    POST /api/auth/login/verify  ┌──────────────┐
│  OTP Screen  │ ─────────────────────────────►  │ Verify OTP & │
│  (6 digits)  │                                 │ Return JWT   │
└──────────────┘                                 └──────────────┘
```

### API Endpoints

| Method | Endpoint                | Description                        |
|--------|-------------------------|------------------------------------|
| POST   | `/api/auth/register`    | Register a new user, sends OTP     |
| POST   | `/api/auth/verify-otp`  | Verify OTP after registration      |
| POST   | `/api/auth/login`       | Login with credentials, sends OTP  |
| POST   | `/api/auth/login/verify`| Verify login OTP, returns JWT      |
| POST   | `/api/auth/resend-otp`  | Resend OTP to user's email         |
| GET    | `/api/auth/me?token=`   | Get current user info from token   |

---

## 🛠️ Services & Tech Stack

### Backend (Python)

| Service / Library        | Purpose                                          |
|--------------------------|--------------------------------------------------|
| **FastAPI**              | High-performance async web framework              |
| **SQLAlchemy**           | ORM for database models and queries               |
| **Supabase PostgreSQL**  | Cloud-hosted PostgreSQL database                  |
| **python-jose (JWT)**    | JSON Web Token generation and verification        |
| **passlib + bcrypt**     | Secure password hashing                           |
| **SMTP (Gmail)**         | Sending OTP verification emails                   |
| **python-dotenv**        | Environment variable management                   |
| **Uvicorn**              | ASGI server to run FastAPI                        |
| **Pydantic**             | Request/response data validation                  |

### Frontend (Flutter/Dart)

| Component                | Purpose                                           |
|--------------------------|---------------------------------------------------|
| **Flutter**              | Cross-platform mobile UI framework                |
| **auth_service.dart**    | Handles all auth API calls (register, login, OTP) |
| **login_screen.dart**    | Login page with email & password                  |
| **signup_screen.dart**   | Registration page with role selection             |
| **otp_screen.dart**      | OTP input screen for 2FA verification             |
| **splash_screen.dart**   | Animated splash with auto-login check             |

---

## 🚀 How to Run

### Prerequisites

- **Python 3.9+**
- **Flutter SDK 3.x+**
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/gL1TchE0/food-rescue-platform.git
cd food-rescue-platform
git checkout user_authentication-Eswar
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL="postgresql://<user>:<password>@<host>:<port>/<database>"

# JWT Settings
SECRET_KEY="your-random-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Email (SMTP) — For Gmail, use an App Password
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
FROM_EMAIL="your-email@gmail.com"
```

> [!TIP]
> If SMTP credentials are not configured, OTPs will be printed to the backend console for development/testing.

#### Run the Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd frontend

# Get Flutter dependencies
flutter pub get

# Run the app
flutter run
```

> [!IMPORTANT]
> Make sure the backend URL in `auth_service.dart` points to your running backend (e.g., `http://10.0.2.2:8000` for Android emulator or `http://localhost:8000` for web).

---

## 📁 Project Structure

```
surplus-sync/
├── backend/
│   ├── main.py              # FastAPI app, donation endpoints, WebSocket
│   ├── auth.py              # Authentication module (JWT, OTP, RBAC)
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables (not committed)
│
└── frontend/
    └── lib/
        ├── main.dart              # App entry point & routing
        ├── models/                # Data models
        ├── providers/             # State management
        ├── screens/
        │   ├── login_screen.dart       # Login UI
        │   ├── signup_screen.dart      # Registration UI
        │   ├── otp_screen.dart         # OTP verification UI
        │   ├── splash_screen.dart      # Splash & auto-login
        │   └── dispatcher_map_screen.dart  # Map view
        ├── services/
        │   ├── auth_service.dart       # Auth API integration
        │   └── api_service.dart        # General API calls
        └── widgets/               # Reusable UI components
```

---

## 👥 Contributors

- **Eswar** — User Authentication Module
