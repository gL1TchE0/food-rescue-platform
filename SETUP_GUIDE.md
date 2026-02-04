# 🚀 M7 Logistics System - Complete Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start (Development)](#quick-start-development)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Download Link |
|----------|---------|---------------|
| Python | 3.11+ | https://www.python.org/downloads/ |
| PostgreSQL | 15+ | https://www.postgresql.org/download/ |
| Redis | 7+ | https://redis.io/download |
| Node.js | 18+ | https://nodejs.org/ |
| Flutter | 3.x | https://flutter.dev/docs/get-started/install |

### Required Accounts (Free Tier)

1. **Mapbox** - For maps and navigation
   - Sign up: https://account.mapbox.com/auth/signup/
   - Get access token from: https://account.mapbox.com/access-tokens/

2. **Firebase** - For authentication and notifications
   - Console: https://console.firebase.google.com/
   - Create new project
   - Enable: Authentication (Phone), Cloud Messaging

3. **Cloudinary** (Optional) - For image storage
   - Sign up: https://cloudinary.com/users/register/free

---

## Quick Start (Development)

### Step 1: Database Setup

```powershell
# Install PostgreSQL with PostGIS
# Download installer: https://www.postgresql.org/download/windows/

# After installation, open pgAdmin or psql
psql -U postgres

# In psql console:
CREATE DATABASE m7_logistics;
\c m7_logistics
CREATE EXTENSION postgis;
CREATE EXTENSION "uuid-ossp";
\q

# Import schema
cd M7_Logistics_System/backend
psql -U postgres -d m7_logistics -f database_schema.sql
```

### Step 2: Redis Setup

```powershell
# Windows: Download Redis from https://github.com/microsoftarchive/redis/releases
# Or use WSL: wsl --install

# Start Redis server
redis-server

# Test connection (in new terminal)
redis-cli ping
# Should return: PONG
```

### Step 3: Backend Setup

```powershell
cd M7_Logistics_System/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate  # Windows PowerShell
# OR
venv\Scripts\activate.bat  # Windows CMD

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
notepad .env
```

**Important: Update `.env` file with:**
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/m7_logistics
REDIS_URL=redis://localhost:6379/0
FIREBASE_PROJECT_ID=your-firebase-project-id
MAPBOX_ACCESS_TOKEN=pk.YOUR_MAPBOX_TOKEN
SECRET_KEY=generate-a-random-secret-key-here
```

```powershell
# Run backend server
python main.py

# Server should start at: http://localhost:8000
# API Docs available at: http://localhost:8000/docs
```

### Step 4: Web Dashboard Setup

```powershell
# Open new terminal
cd M7_Logistics_System/donor_dashboard

# Install dependencies
npm install

# Create .env file
echo "VITE_MAPBOX_TOKEN=pk.YOUR_MAPBOX_TOKEN" > .env

# Start development server
npm run dev

# Dashboard should open at: http://localhost:3000
```

### Step 5: Mobile App Setup

```powershell
# Open new terminal
cd M7_Logistics_System/volunteer_app

# Get Flutter dependencies
flutter pub get

# Check Flutter setup
flutter doctor

# Connect Android device or start emulator
flutter devices

# Run app
flutter run
```

**Firebase Configuration for Mobile:**
1. Download `google-services.json` from Firebase Console
2. Place in: `volunteer_app/android/app/google-services.json`
3. Download `GoogleService-Info.plist`
4. Place in: `volunteer_app/ios/Runner/GoogleService-Info.plist`

---

## Production Deployment

### Option 1: Docker Compose (Recommended)

```powershell
# Ensure Docker Desktop is installed
# Download: https://www.docker.com/products/docker-desktop/

cd M7_Logistics_System

# Build and start all services
docker-compose up -d

# Services will be available at:
# - Backend: http://localhost:8000
# - Web Dashboard: http://localhost:3000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Manual Deployment

#### Backend (Cloud VM)

```bash
# SSH into server
ssh user@your-server.com

# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip postgresql-15 postgresql-15-postgis-3 redis

# Clone repository
git clone <your-repo-url>
cd M7_Logistics_System/backend

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup systemd service
sudo nano /etc/systemd/system/m7-backend.service
```

**systemd service file:**
```ini
[Unit]
Description=M7 Logistics Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/M7_Logistics_System/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl start m7-backend
sudo systemctl enable m7-backend
```

#### Web Dashboard (Vercel/Netlify)

```powershell
cd donor_dashboard

# Build production bundle
npm run build

# Deploy to Vercel
npm install -g vercel
vercel --prod

# OR deploy to Netlify
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

#### Mobile App (App Stores)

```powershell
cd volunteer_app

# Android APK
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk

# Android App Bundle (for Play Store)
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab

# iOS (requires Mac)
flutter build ios --release
# Then open Xcode and archive
```

---

## Environment Configuration

### Backend `.env` Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/m7_logistics

# Redis
REDIS_URL=redis://localhost:6379/0

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./firebase-service-account.json

# Mapbox
MAPBOX_ACCESS_TOKEN=pk.your_token

# Cloudinary (Optional)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Twilio (Optional - for SMS)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Security
SECRET_KEY=your-super-secret-key-min-32-characters
ENVIRONMENT=production
DEBUG=False

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Web Dashboard `.env`

```env
VITE_MAPBOX_TOKEN=pk.your_mapbox_token
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## Troubleshooting

### Backend Issues

#### "Connection refused" error
```powershell
# Check if PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Check if Redis is running
redis-cli ping

# Check if port 8000 is available
netstat -an | findstr :8000
```

#### "PostGIS not found"
```sql
-- Connect to database
psql -U postgres -d m7_logistics

-- Install extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify installation
SELECT PostGIS_Version();
```

#### "Import Error: No module named..."
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Web Dashboard Issues

#### "Cannot connect to backend"
- Check backend is running: `http://localhost:8000/health`
- Verify CORS settings in `backend/app/core/config.py`
- Check browser console for errors (F12)

#### "Mapbox map not loading"
- Verify `VITE_MAPBOX_TOKEN` in `.env`
- Check Mapbox token is valid: https://account.mapbox.com/access-tokens/
- Open browser console and look for 401 errors

### Mobile App Issues

#### "Location permission denied"
```dart
// Check permissions in Android Manifest
// volunteer_app/android/app/src/main/AndroidManifest.xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

#### "Firebase not initialized"
1. Verify `google-services.json` is in correct location
2. Run: `flutter clean && flutter pub get`
3. Check Firebase Console for correct package name

#### "Build failed"
```powershell
# Clean build cache
flutter clean

# Get dependencies
flutter pub get

# Run Flutter doctor
flutter doctor -v

# Rebuild
flutter run
```

### Database Issues

#### "Too many connections"
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Increase max connections
-- Edit postgresql.conf
max_connections = 200
```

#### "Disk space full"
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('m7_logistics'));

-- Vacuum database
VACUUM FULL;
```

---

## Performance Tuning

### PostgreSQL

```sql
-- Increase shared buffers (25% of RAM)
shared_buffers = 2GB

-- Increase work memory
work_mem = 50MB

-- Enable query optimization
effective_cache_size = 6GB
```

### Redis

```conf
# redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
```

### Backend

```python
# Increase worker count based on CPU cores
# uvicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

---

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database health
psql -U postgres -d m7_logistics -c "SELECT 1;"

# Redis health
redis-cli ping
```

### Logs

```powershell
# Backend logs
tail -f logs/app.log

# PostgreSQL logs
# Location: C:\Program Files\PostgreSQL\15\data\log\

# Docker logs
docker-compose logs -f backend
```

---

## Support

- **Documentation**: See [README.md](README.md)
- **API Docs**: http://localhost:8000/docs (when backend running)
- **GitHub Issues**: Open an issue for bugs or feature requests

---

**Built by M7 Team** | Version 1.0.0
