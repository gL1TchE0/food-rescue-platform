# 🚀 Quick Start Guide - M7 Volunteer Maps & QR Features

## ⚡ 5-Minute Setup

### Step 1: Apply Database Migration
```bash
# Copy the SQL from backend/migrations/add_qr_tokens.sql
# Paste and run in Supabase SQL Editor at:
# https://app.supabase.com/project/bwrwszeftkiwbybolzrh/sql
```

### Step 2: Start Backend
```bash
cd backend
python main.py
# Should start on http://localhost:8000
```

### Step 3: Configure Flutter
```bash
cd volunteer_app

# Install dependencies
flutter pub get

# Add Google Maps API key to:
# - android/app/src/main/AndroidManifest.xml
# - ios/Runner/AppDelegate.swift
```

### Step 4: Run App
```bash
flutter run
```

## 📱 Testing the Features

### 1. Create Test Task
Create a task in Supabase with:
- `pickup_token`: Any 6-char string (e.g., "ABC123")
- `delivery_token`: Any 6-char string (e.g., "XYZ789")
- Assign to a volunteer

### 2. Test Navigation
- Open app as volunteer
- Navigate to RouteScreen with task
- See route to pickup location
- Markers should appear

### 3. Test QR Scanning
- Tap "Scan Pickup QR" button
- Scan QR code with token "ABC123"
- Should verify and update task status
- Map switches to delivery location

### 4. Complete Delivery
- Tap "Scan Delivery QR" button
- Scan QR code with token "XYZ789"
- Task completes
- Returns to home screen

## 🔧 Common Issues

### Maps Not Showing?
```bash
# Check:
1. Google Maps API key configured?
2. Location permissions granted?
3. Internet connection active?
```

### QR Scanner Not Working?
```bash
# Check:
1. Camera permissions granted?
2. Testing on physical device? (not simulator)
3. QR code clearly visible?
```

### Backend API Errors?
```bash
# Check:
1. Backend server running?
2. Supabase connection working?
3. Migration applied?
4. Check logs in terminal
```

## 📋 API Endpoints

### Verify Pickup
```http
POST /api/v1/task/{task_id}/verify-pickup
Content-Type: application/json

{
  "qr_token": "ABC123"
}
```

### Verify Delivery
```http
POST /api/v1/task/{task_id}/verify-dropoff
Content-Type: application/json

{
  "qr_token": "XYZ789"
}
```

## 🎯 Key Files to Know

### Backend
- `backend/.env` - Database config
- `backend/app/models/models.py` - Task model with tokens
- `backend/app/api/v1/endpoints/tasks.py` - Verification endpoints

### Flutter
- `lib/ui/screens/route_screen.dart` - Main navigation screen
- `lib/ui/widgets/qr_scanner_modal.dart` - QR scanner
- `lib/data/task_api_service.dart` - API client

## 🔑 Important Notes

1. **Tokens**: Auto-generated 6-char hex strings (e.g., "A3B5C7")
2. **State Flow**: ASSIGNED → PICKED_UP → IN_TRANSIT → COMPLETED
3. **Maps**: Uses Google Maps (not Mapbox)
4. **Scanner**: Uses mobile_scanner (not qr_code_scanner)

## 📊 Task Status Flow

```
PENDING
   ↓ (assignment)
ASSIGNED
   ↓ (navigate to pickup)
IN_PROGRESS
   ↓ (scan pickup QR)
PICKED_UP
   ↓ (navigate to delivery)
IN_TRANSIT
   ↓ (scan delivery QR)
DELIVERED → COMPLETED
```

## ✅ Pre-Deployment Checklist

- [ ] Database migration applied
- [ ] Backend .env configured with Supabase
- [ ] Backend server starts without errors
- [ ] Flutter dependencies installed
- [ ] Google Maps API key added
- [ ] App builds successfully
- [ ] Location permissions work
- [ ] Camera permissions work
- [ ] End-to-end test completed

## 🆘 Getting Help

1. Check `IMPLEMENTATION_GUIDE.md` for detailed docs
2. Review `CHANGES_SUMMARY.md` for what changed
3. Check error logs in backend terminal
4. Run `flutter doctor` for Flutter issues

## 🎉 Success Indicators

✅ Backend server running on port 8000
✅ Map displays with markers
✅ Route draws between locations
✅ QR scanner opens and scans
✅ Verification succeeds
✅ Task status updates
✅ State transitions work

---

**Quick Help**: All files are documented with inline comments.
**Full Guide**: See `IMPLEMENTATION_GUIDE.md`
**Changes**: See `CHANGES_SUMMARY.md`
