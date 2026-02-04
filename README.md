# M7 Volunteer Logistics Subsystem

> **Version**: 1.0.0  
> **Status**: ✅ Ready for Implementation  
> **Architecture**: State-Authoritative, Offline-First

## 🎯 System Overview

The M7 Volunteer Logistics System is a **production-grade food distribution platform** featuring:

- **Volunteer Mobile App** (Flutter) - GPS tracking, QR verification, offline operations
- **Dispatcher/Donor Web Console** (React) - Real-time monitoring dashboard
- **Backend Core** (FastAPI + PostgreSQL + Redis) - State machine, WebSocket streaming

### Core Philosophy: State-Authoritative Model
The **Backend is the single source of truth**. Mobile and web clients are projections of backend state.

---

## 📂 Project Structure

```
M7_Logistics_System/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/  # REST API endpoints
│   │   ├── core/              # Config, WebSocket manager
│   │   ├── db/                # Database & Redis clients
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   └── services/          # 🔥 state_machine.py (CRITICAL)
│   ├── main.py
│   ├── requirements.txt
│   └── database_schema.sql    # PostgreSQL + PostGIS schema
│
├── volunteer_app/              # Flutter Mobile App
│   ├── lib/
│   │   ├── data/              # SQLite, Location service
│   │   ├── ui/
│   │   │   ├── screens/       # Home, Active Task screens
│   │   │   └── widgets/       # Slide-to-accept widget
│   │   └── main.dart
│   └── pubspec.yaml
│
└── donor_dashboard/            # React Web Console
    ├── src/
    │   ├── components/        # MapView, VolunteerCard
    │   ├── hooks/             # useLiveTracking
    │   └── pages/             # Dashboard
    └── package.json
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **PostgreSQL 15** with PostGIS extension
- **Redis 7+**
- **Node.js 18+**
- **Flutter 3.x**
- **Mapbox API Token** (free tier)
- **Firebase Project** (for authentication)

### 1. Database Setup

```bash
# Install PostgreSQL + PostGIS
# Windows: Download from https://www.postgresql.org/download/windows/
# Linux: sudo apt install postgresql-15 postgresql-15-postgis-3

# Create database
psql -U postgres
CREATE DATABASE m7_logistics;
\c m7_logistics
CREATE EXTENSION postgis;

# Run schema
psql -U postgres -d m7_logistics -f backend/database_schema.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run server
python main.py
# Server: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 3. Web Dashboard Setup

```bash
cd donor_dashboard

# Install dependencies
npm install

# Configure Mapbox token
echo "VITE_MAPBOX_TOKEN=your_token_here" > .env

# Run dev server
npm run dev
# Dashboard: http://localhost:3000
```

### 4. Mobile App Setup

```bash
cd volunteer_app

# Get Flutter dependencies
flutter pub get

# Configure Firebase
# 1. Add google-services.json (Android)
# 2. Add GoogleService-Info.plist (iOS)

# Run on device/emulator
flutter run
```

---

## 🔥 Core Features

### State Machine (Finite State Machine)

The system enforces strict workflow control:

```
OFFLINE → ONLINE → ASSIGNED → NAVIGATING_TO_DONOR 
→ PICKUP_VERIFIED → IN_TRANSIT → DROPOFF_VERIFIED 
→ COMPLETED → ONLINE
```

**Guards**:
- `PICKUP_VERIFIED` requires QR scan at donor location
- `DROPOFF_VERIFIED` requires QR scan at NGO location
- `EXCEPTION` state freezes workflow for dispatcher intervention

### Real-Time Location Streaming

- **GPS updates every 5 seconds** during active tasks
- **WebSocket broadcasts** to dispatcher console
- **Donor tracking view** visible only during `NAVIGATING_TO_DONOR` state
- **Offline queue** stores updates when network unavailable

### Offline-First Mobile App

- **SQLite local storage** for tasks and location queue
- **Automatic sync** when connectivity restored
- **QR scanner** works offline
- **Photo proofs** uploaded when online

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python FastAPI (Async) |
| **Database** | PostgreSQL 15 + PostGIS |
| **Cache** | Redis 7 |
| **WebSocket** | Socket.IO |
| **Mobile** | Flutter + Dart |
| **Web** | React.js + Tailwind CSS |
| **Maps** | Mapbox GL |
| **Auth** | Firebase Auth (Phone OTP) |
| **Notifications** | FCM (Firebase Cloud Messaging) |
| **Storage** | Cloudinary (Image uploads) |

---

## 📡 API Endpoints

### Volunteer Endpoints

```
POST   /api/v1/volunteer/register          # Register new volunteer
POST   /api/v1/volunteer/status            # Update ONLINE/OFFLINE status
POST   /api/v1/volunteer/location          # Send GPS update
GET    /api/v1/volunteer/task/current      # Get active task
GET    /api/v1/volunteer/available-actions # Get state-based actions
```

### Task Endpoints

```
POST   /api/v1/task/create                # Create new task
POST   /api/v1/task/{id}/accept           # Accept assigned task
POST   /api/v1/task/{id}/verify-pickup    # QR verification at pickup
POST   /api/v1/task/{id}/verify-dropoff   # QR verification at dropoff
POST   /api/v1/task/{id}/exception        # Report issue (flat tire, etc.)
GET    /api/v1/task/pending               # Get pending tasks (dispatcher)
```

### WebSocket Events

```javascript
// Client → Server
volunteer_register        // Register volunteer session
dispatcher_register       // Register dispatcher session
donor_track_task          // Donor subscribes to task tracking
location_update          // Volunteer sends GPS coordinates

// Server → Client
task_assigned            // Push task to volunteer
state_changed            // Notify state transition
volunteer_location       // Broadcast location to dispatcher
task_exception          // Alert dispatcher of issue
```

---

## 🎨 UI Design Specifications

### Design System

- **Primary Color**: `#2563EB` (Royal Blue)
- **Success**: `#10B981` (Emerald)
- **Warning**: `#F59E0B` (Amber)
- **Danger**: `#EF4444` (Red)
- **Background Light**: `#F4F5F7`
- **Background Dark**: `#121212`
- **Typography**: Inter font family

### Mobile App Key Screens

1. **Home Screen**: Blurred map background + "Slide to Online" toggle
2. **Incoming Task Modal**: Full-screen takeover with pulsing urgency badge
3. **Active Dashboard**: Mapbox map with blue route polyline + bottom sheet
4. **QR Scanner**: Camera view with corner brackets + exploding checkmark animation
5. **Exception Mode**: Big buttons for issue types, freezes map updates

### Web Console

- **Dark mode map** (Mapbox Dark v11)
- **Priority queue sidebar** sorted by food expiry time
- **Green dots** for active volunteers
- **Responsive tracking view** for donors

---

## 🔐 Security Considerations

1. **Firebase Authentication**: Phone OTP for volunteer login
2. **JWT Tokens**: Short-lived access tokens (24 hours)
3. **QR Token Verification**: Unique tokens per donor/NGO
4. **CORS Protection**: Whitelist trusted origins
5. **Rate Limiting**: Prevent API abuse
6. **Encrypted Storage**: Sensitive data in SQLite encrypted

---

## 📊 Database Schema Highlights

### Key Tables

- **`volunteers`**: Profile, status, current location (PostGIS Point)
- **`tasks`**: Pickup/drop locations, expiry time, status
- **`tracking_sessions`**: Ephemeral GPS tracking data
- **`task_exceptions`**: Issue reports with resolution tracking
- **`performance_stats`**: Volunteer ratings and completion metrics

### PostGIS Functions

```sql
-- Find volunteers within 10km radius
SELECT * FROM find_nearby_volunteers(12.9716, 77.5946, 10);
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd donor_dashboard
npm test

# Flutter tests
cd volunteer_app
flutter test
```

---

## 🚢 Deployment

### Backend (Docker)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Web Dashboard (Vercel/Netlify)

```bash
npm run build
# Deploy dist/ folder
```

### Mobile App

```bash
# Android APK
flutter build apk --release

# iOS IPA (requires Mac)
flutter build ios --release
```

---

## 📈 Performance Optimization

- **Redis caching** for live location data (60s TTL)
- **Connection pooling** for PostgreSQL (10 connections)
- **Lazy loading** for map markers
- **Debounced GPS updates** (5-second intervals)
- **SQLite indexing** for offline queries

---

## 🐛 Troubleshooting

### Backend won't start
- Check PostgreSQL connection string in `.env`
- Ensure Redis is running: `redis-cli ping`
- Verify PostGIS extension: `SELECT PostGIS_Version();`

### Mobile app location not updating
- Check permissions in Android/iOS settings
- Verify GPS is enabled
- Test with `LocationService.instance.getCurrentLocation()`

### WebSocket not connecting
- Check CORS settings in `socket_manager.py`
- Verify port 8000 is open
- Test Socket.IO endpoint: `http://localhost:8000/ws`

---

## 📝 License

This project is part of the M7 Volunteer initiative. All rights reserved.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📞 Support

For issues or questions:
- **Technical**: Open a GitHub issue
- **Architecture**: Review `/backend/app/services/state_machine.py`
- **Documentation**: Check inline code comments

---

**Built with ❤️ by the M7 Team**
