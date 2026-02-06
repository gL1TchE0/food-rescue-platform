# Food Rescue Platform - Backend API

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Seed Database with Test Data

```bash
python seed_data.py
```

This creates:
- 3 test NGO accounts (2 approved, 1 pending)
- 7 sample donations (6 available, 1 claimed)

### 3. Start the Server

```bash
uvicorn main:app --reload
```

Server will start at: `http://localhost:8000`

### 4. Access API Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Test Credentials

### NGO 1 (Approved - Can Claim)
- **Email**: `hope@foundation.org`
- **Password**: `password123`
- **Capacity**: 150 kg

### NGO 2 (Approved - Can Claim)
- **Email**: `contact@foodforall.org`
- **Password**: `password123`
- **Capacity**: 200 kg

### NGO 3 (Pending - Cannot Claim)
- **Email**: `info@helpinghands.org`
- **Password**: `password123`
- **Status**: Pending approval

## 📡 API Endpoints

### Authentication

#### POST `/api/auth/login`
Login and get JWT token

**Request:**
```json
{
  "email": "hope@foundation.org",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST `/api/auth/register`
Register new NGO

**Request:**
```json
{
  "name": "New NGO",
  "email": "new@ngo.org",
  "password": "password123",
  "phone": "+91-9876543210",
  "address": "123 Street, City",
  "serving_capacity": 100.0
}
```

#### GET `/api/auth/me`
Get current user (requires authentication)

#### GET `/api/auth/ngo`
Get current NGO details (requires authentication)

---

### Donations

#### GET `/api/donations/available`
Get all available donations (NGO only, requires authentication)

**Headers:**
```
Authorization: Bearer <your_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "donor_name": "Taj Hotel",
    "food_type": "VEG",
    "quantity": 25.5,
    "address": "Apollo Bunder, Mumbai",
    "expiry_time": "2026-01-31T10:00:00",
    "status": "AVAILABLE"
  }
]
```

#### PATCH `/api/donations/{id}/status`
Claim a donation (NGO only, requires authentication)

**Headers:**
```
Authorization: Bearer <your_token>
```

**Request:**
```json
{
  "new_status": "ASSIGNED"
}
```

**Response:**
```json
{
  "id": 1,
  "donor_name": "Taj Hotel",
  "status": "ASSIGNED",
  "ngo_id": 1,
  "claimed_at": "2026-01-30T23:30:00"
}
```

#### POST `/api/donations`
Create a new donation (for donors)

**Request:**
```json
{
  "donor_name": "Restaurant Name",
  "donor_phone": "+91-9876543210",
  "food_type": "VEG",
  "quantity": 25.5,
  "address": "Full address",
  "expiry_time": "2026-01-31T10:00:00"
}
```

#### GET `/api/donations/{id}/verify`
Verify donation via QR code (for volunteers)

**Response:**
```json
{
  "id": 1,
  "donor_name": "Taj Hotel",
  "food_type": "VEG",
  "quantity": 25.5,
  "address": "Apollo Bunder, Mumbai",
  "status": "ASSIGNED",
  "ngo_name": "Hope Foundation",
  "verified": true
}
```

## 🧪 Testing with Flutter App

### 1. Get Your Computer's IP Address

**Windows:**
```bash
ipconfig
```

**Mac/Linux:**
```bash
ifconfig
```

Look for IPv4 Address (e.g., `192.168.1.100`)

### 2. Update Flutter App Configuration

Edit `lib/config/api_config.dart`:

```dart
// For Android Emulator
static const String baseUrl = 'http://10.0.2.2:8000';

// For Physical Device (use your IP)
static const String baseUrl = 'http://192.168.1.100:8000';
```

### 3. Test the Flow

1. **Start Backend**: `uvicorn main:app --reload`
2. **Login in Flutter**: Use test credentials
3. **View Donations**: See available donations
4. **Claim Donation**: Tap CLAIM button
5. **Get QR Code**: QR code appears with donation ID
6. **Verify**: Use `/api/donations/{id}/verify` endpoint

## 🗄️ Database

- **Type**: SQLite
- **File**: `food_rescue.db` (auto-created)
- **Location**: `backend/` directory

### Reset Database

```bash
# Delete database file
rm food_rescue.db

# Re-seed
python seed_data.py
```

## 🔐 Security

- **JWT Authentication**: 30-minute token expiry
- **Password Hashing**: bcrypt
- **CORS**: Enabled for all origins (development)

## 📝 Environment Variables

Create `.env` file (or use existing one):

```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./food_rescue.db
ALLOWED_ORIGINS=*
```

## 🛠️ Development

### Run with Auto-Reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Check Logs

Server logs will show all API requests and responses.

## 📦 Project Structure

```
backend/
├── main.py                 # FastAPI app
├── database.py            # Database configuration
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── auth.py                # Authentication utilities
├── seed_data.py           # Database seeding
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
├── .env.example          # Environment template
└── routes/
    ├── __init__.py
    ├── auth.py           # Auth endpoints
    └── donations.py      # Donation endpoints
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 8000 (Mac/Linux)
lsof -ti:8000 | xargs kill -9
```

### Database Locked

Close any database viewers and restart the server.

### CORS Errors

Make sure CORS is enabled in `main.py` (already configured).

## 🎯 Business Rules

1. **NGO Approval**: Only APPROVED NGOs can claim donations
2. **Capacity Check**: Donation quantity must not exceed 120% of NGO capacity
3. **Expiry Check**: Cannot claim expired donations
4. **Status Check**: Can only claim AVAILABLE donations

---

**Built with FastAPI 🚀 | Food Rescue Platform 🍽️**
