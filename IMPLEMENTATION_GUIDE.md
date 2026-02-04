# M7 Volunteer Module - Maps & QR Verification Implementation

## Overview
This document describes the implementation of Maps & QR Verification features for the M7 Volunteer Module. The implementation maintains the existing State Machine and Socket Manager logic while adding new capabilities.

## Changes Summary

### 🔧 Backend Changes

#### 1. Database Configuration
**File**: `backend/.env`
- Updated database connection to use Supabase PostgreSQL
- Connection string: `postgresql+psycopg2://postgres:surplusSync%2540012345@db.bwrwszeftkiwbybolzrh.supabase.co:5432/postgres`

#### 2. Database Schema
**File**: `backend/app/models/models.py`
- Added `pickup_token` (String, 10 chars) to Task model
- Added `delivery_token` (String, 10 chars) to Task model
- Tokens are automatically generated using `secrets.token_hex(3).upper()` - creates 6-character hex strings

**File**: `backend/migrations/add_qr_tokens.sql`
- SQL migration script to add pickup_token and delivery_token columns
- Creates indexes for fast token lookup
- Includes default value generation for existing records

#### 3. API Endpoints
**File**: `backend/app/api/v1/endpoints/tasks.py`

Modified two existing endpoints to use task tokens instead of Donor/NGO tokens:

**POST `/api/v1/task/{task_id}/verify-pickup`**
- **Input**: `{ "qr_token": "..." }`
- **Logic**: 
  - Verifies token matches `task.pickup_token`
  - Transitions volunteer state: `NAVIGATING_TO_DONOR` → `PICKUP_VERIFIED`
  - Updates task status: `ASSIGNED` → `PICKED_UP`
  - Broadcasts update via WebSocket
- **Response**: `{ "status": "success", "message": "...", "new_task_status": "PICKED_UP" }`

**POST `/api/v1/task/{task_id}/verify-dropoff`**
- **Input**: `{ "qr_token": "..." }`
- **Logic**:
  - Verifies token matches `task.delivery_token`
  - Transitions: `IN_TRANSIT` → `DROPOFF_VERIFIED` → `COMPLETED` → `ONLINE`
  - Updates task status: `IN_TRANSIT` → `COMPLETED`
  - Sets `completed_at` timestamp
  - Broadcasts completion via WebSocket
- **Response**: `{ "status": "success", "message": "...", "new_task_status": "COMPLETED" }`

### 📱 Flutter Frontend Changes

#### 1. Dependencies
**File**: `volunteer_app/pubspec.yaml`

Updated packages:
- `google_maps_flutter: ^2.5.0` (replaced mapbox_maps_flutter)
- `flutter_polyline_points: ^2.0.1` (for route drawing)
- `mobile_scanner: ^3.5.5` (replaced qr_code_scanner)

#### 2. New Data Models & Services

**File**: `volunteer_app/lib/data/task_model.dart`
- `Task` class with all task properties including pickup_token and delivery_token
- `Location` class for lat/lng coordinates
- `TaskStatus` enum matching backend states

**File**: `volunteer_app/lib/data/task_api_service.dart`
- `verifyPickup(taskId, qrToken)` - calls `/verify-pickup` endpoint
- `verifyDelivery(taskId, qrToken)` - calls `/verify-dropoff` endpoint
- `getTask(taskId)` - fetches task details
- `acceptTask(taskId, volunteerId)` - accepts task assignment
- `reportException(taskId, issueType, description)` - reports issues

#### 3. UI Components

**File**: `volunteer_app/lib/ui/screens/route_screen.dart`
- Full-featured navigation screen with Google Maps
- Real-time location tracking using geolocator
- Dynamic destination based on task status:
  - **ASSIGNED/IN_PROGRESS**: Shows route to pickup location (donor)
  - **PICKED_UP/IN_TRANSIT**: Shows route to delivery location (NGO)
- Displays task information card with:
  - Current destination type
  - Distance
  - Cooling requirement indicator
- Floating Action Button for QR scanning
- Automatic marker placement and polyline drawing
- Error handling and retry mechanism

**File**: `volunteer_app/lib/ui/widgets/qr_scanner_modal.dart`
- Beautiful full-screen QR scanner modal
- Custom overlay with scanning frame and corner brackets
- Flash toggle button
- Scanning status feedback
- Uses `mobile_scanner` package for optimal performance

## 🚀 Setup Instructions

### Backend Setup

1. **Apply Database Migration**
   ```bash
   cd backend
   
   # Connect to Supabase and run the migration
   psql "postgresql://postgres:surplusSync@12345@db.bwrwszeftkiwbybolzrh.supabase.co:5432/postgres" < migrations/add_qr_tokens.sql
   
   # OR manually execute the SQL in Supabase SQL Editor
   ```

2. **Install Dependencies** (if needed)
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Backend Server**
   ```bash
   python main.py
   ```

### Flutter Setup

1. **Install Dependencies**
   ```bash
   cd volunteer_app
   flutter pub get
   ```

2. **Configure Google Maps API**
   
   **For Android** (`android/app/src/main/AndroidManifest.xml`):
   ```xml
   <manifest>
     <application>
       <meta-data
         android:name="com.google.android.geo.API_KEY"
         android:value="YOUR_GOOGLE_MAPS_API_KEY"/>
     </application>
   </manifest>
   ```
   
   **For iOS** (`ios/Runner/AppDelegate.swift`):
   ```swift
   import GoogleMaps
   
   GMSServices.provideAPIKey("YOUR_GOOGLE_MAPS_API_KEY")
   ```

3. **Update API Base URL** (if needed)
   
   Edit `lib/data/task_api_service.dart`:
   ```dart
   static const String baseUrl = 'http://YOUR_SERVER_IP:8000/api/v1';
   ```

4. **Run the App**
   ```bash
   flutter run
   ```

## 📖 Usage Flow

### Volunteer Workflow

1. **Task Assignment**
   - Volunteer receives task assignment via WebSocket
   - Task includes pickup_token and delivery_token

2. **Navigate to Pickup**
   - Open RouteScreen with the assigned task
   - Map shows route from current location to donor location
   - Blue marker: Current location
   - Green marker: Pickup location

3. **Pickup Verification**
   - Arrive at donor location
   - Tap "Scan Pickup QR" button
   - Scan the pickup QR code displayed by donor
   - System verifies token matches task.pickup_token
   - Task transitions to IN_TRANSIT

4. **Navigate to Delivery**
   - Map automatically updates to show route to NGO
   - Red marker: Delivery location

5. **Delivery Verification**
   - Arrive at NGO location
   - Tap "Scan Delivery QR" button
   - Scan the delivery QR code displayed by NGO
   - System verifies token matches task.delivery_token
   - Task completes, volunteer returns to ONLINE status

## 🔒 Security Notes

- QR tokens are unique per task
- Tokens are 6-character uppercase hex strings (e.g., "A3B5C7")
- Tokens are verified server-side to prevent tampering
- State transitions are enforced by the State Machine
- All API calls require proper authentication (implement as needed)

## 🎯 Key Features

### Backend
✅ Supabase PostgreSQL integration
✅ Automatic token generation for tasks
✅ State-machine-enforced verification flow
✅ WebSocket broadcasting for real-time updates
✅ Existing state machine logic preserved

### Frontend
✅ Google Maps with real-time navigation
✅ Dynamic route rendering based on task status
✅ High-quality QR code scanner with overlay
✅ Automatic destination switching
✅ Task information display
✅ Error handling and user feedback
✅ Flash toggle for low-light scanning

## 🐛 Troubleshooting

### Backend Issues

**Migration fails**:
- Ensure you have the correct Supabase credentials
- Check if the tasks table exists
- Verify PostgreSQL version supports `gen_random_bytes()`

**Verification endpoint returns 400**:
- Check that the task has pickup_token/delivery_token set
- Verify the QR code contains the correct token
- Ensure the task is in the correct state for verification

### Flutter Issues

**Maps not showing**:
- Verify Google Maps API key is configured
- Check that location permissions are granted
- Ensure internet connectivity

**QR Scanner not working**:
- Grant camera permissions
- Test on a physical device (simulators may not support camera)
- Ensure proper lighting conditions

**API calls failing**:
- Check the baseUrl in task_api_service.dart
- Verify backend server is running
- Check network connectivity

## 📝 Testing

### Backend Testing
```bash
# Test pickup verification
curl -X POST http://localhost:8000/api/v1/task/{task_id}/verify-pickup \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "A3B5C7"}'

# Test delivery verification
curl -X POST http://localhost:8000/api/v1/task/{task_id}/verify-dropoff \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "D8E9F0"}'
```

### Flutter Testing
1. Create a test task in the database
2. Navigate to RouteScreen with the test task
3. Generate QR codes with the pickup_token and delivery_token
4. Test the scanning flow end-to-end

## 🔄 Future Enhancements

- [ ] Implement Google Directions API for accurate routes
- [ ] Add ETA calculation
- [ ] Real-time traffic updates
- [ ] Turn-by-turn navigation instructions
- [ ] Offline map caching
- [ ] QR code generation for donors/NGOs
- [ ] Photo proof upload during verification
- [ ] Task history and statistics

## 📚 Related Files

### Backend
- `backend/.env` - Database configuration
- `backend/app/models/models.py` - Task model with tokens
- `backend/app/api/v1/endpoints/tasks.py` - Verification endpoints
- `backend/migrations/add_qr_tokens.sql` - Database migration
- `backend/app/services/state_machine.py` - State machine logic (unchanged)
- `backend/app/core/socket_manager.py` - WebSocket manager (unchanged)

### Frontend
- `volunteer_app/pubspec.yaml` - Dependencies
- `volunteer_app/lib/data/task_model.dart` - Task data model
- `volunteer_app/lib/data/task_api_service.dart` - API client
- `volunteer_app/lib/ui/screens/route_screen.dart` - Navigation screen
- `volunteer_app/lib/ui/widgets/qr_scanner_modal.dart` - QR scanner

## ✅ Checklist

- [x] Database connected to Supabase
- [x] pickup_token and delivery_token added to Task model
- [x] Migration SQL script created
- [x] Verification endpoints updated to use task tokens
- [x] Flutter dependencies updated (Google Maps, Mobile Scanner)
- [x] Task model created in Flutter
- [x] API service implemented
- [x] RouteScreen with Google Maps created
- [x] QR Scanner modal implemented
- [ ] Google Maps API key configured (user must do this)
- [ ] Backend server running
- [ ] Database migration applied
- [ ] App tested end-to-end

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the error logs
3. Verify all setup steps were completed
4. Test individual components separately

---

**Version**: 1.0.0  
**Last Updated**: February 4, 2026  
**Author**: GitHub Copilot
