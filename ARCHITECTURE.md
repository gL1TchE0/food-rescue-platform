# M7 Volunteer Module - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     M7 VOLUNTEER SYSTEM                          │
│                  Maps & QR Verification Flow                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│                  │         │                  │         │                  │
│  FLUTTER APP     │◄────────┤  FASTAPI BACKEND │◄────────┤  SUPABASE DB     │
│  (Volunteer)     │────────►│  (Python Async)  │────────►│  (PostgreSQL)    │
│                  │         │                  │         │                  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
        │                             │                            │
        │                             │                            │
   ┌────▼─────┐                  ┌───▼────┐                  ┌────▼─────┐
   │ Google   │                  │ State  │                  │  Tasks   │
   │  Maps    │                  │Machine │                  │ +tokens  │
   └──────────┘                  └────────┘                  └──────────┘
        │                             │                            │
   ┌────▼─────┐                  ┌───▼────┐                  ┌────▼─────┐
   │ Mobile   │                  │ Socket │                  │Volunteers│
   │ Scanner  │                  │Manager │                  └──────────┘
   └──────────┘                  └────────┘
```

## Data Flow - Pickup Verification

```
┌─────────────┐                                    ┌─────────────┐
│             │  1. Open RouteScreen               │             │
│  VOLUNTEER  │───────────────────────────────────►│  FLUTTER    │
│             │                                    │     APP     │
└─────────────┘                                    └─────────────┘
                                                           │
                                                           │ 2. Show Map
                                                           │    + Route
                                                           ▼
                                                    ┌─────────────┐
                                                    │   GOOGLE    │
                                                    │    MAPS     │
                                                    └─────────────┘
                                                           │
      ┌────────────────────────────────────────────────────┘
      │ 3. Tap "Scan QR"
      ▼
┌─────────────┐
│   MOBILE    │  4. Scan QR Code
│   SCANNER   │────────────┐
└─────────────┘            │
                           │ 5. Get Token (e.g., "ABC123")
                           ▼
                    ┌─────────────┐
                    │ API SERVICE │
                    │ (Dio)       │
                    └─────────────┘
                           │
                           │ 6. POST /verify-pickup
                           │    { qr_token: "ABC123" }
                           ▼
                    ┌─────────────┐
                    │  FASTAPI    │
                    │  ENDPOINT   │
                    └─────────────┘
                           │
                           │ 7. Verify token ==
                           │    task.pickup_token
                           ▼
                    ┌─────────────┐
                    │    STATE    │  8. Transition:
                    │   MACHINE   │     ASSIGNED → PICKED_UP
                    └─────────────┘
                           │
                           │ 9. Update DB
                           ▼
                    ┌─────────────┐
                    │  SUPABASE   │  10. Save new status
                    │     DB      │
                    └─────────────┘
                           │
                           │ 11. Broadcast update
                           ▼
                    ┌─────────────┐
                    │   SOCKET    │  12. Notify all clients
                    │   MANAGER   │
                    └─────────────┘
                           │
                           │ 13. Return success
                           ▼
                    ┌─────────────┐
                    │  FLUTTER    │  14. Update UI
                    │     APP     │      Show delivery route
                    └─────────────┘
```

## Database Schema Changes

```sql
┌─────────────────────────────────────────────────────────┐
│                    TASKS TABLE                          │
├──────────────────┬────────────────────┬─────────────────┤
│ Column           │ Type               │ Description     │
├──────────────────┼────────────────────┼─────────────────┤
│ id               │ UUID               │ Primary Key     │
│ donor_id         │ UUID               │ Foreign Key     │
│ ngo_id           │ UUID               │ Foreign Key     │
│ volunteer_id     │ UUID               │ Foreign Key     │
│ pickup_location  │ GEOMETRY(POINT)    │ Donor coords    │
│ drop_location    │ GEOMETRY(POINT)    │ NGO coords      │
│ distance_km      │ DECIMAL(5,2)       │ Distance        │
│ food_type        │ VARCHAR(50)        │ Food type       │
│ expiry_time      │ TIMESTAMP          │ Expiry          │
│ requires_cooling │ BOOLEAN            │ Cooling flag    │
│ status           │ VARCHAR(30)        │ Task status     │
│ pickup_token     │ VARCHAR(10) ★NEW★  │ QR token pickup │
│ delivery_token   │ VARCHAR(10) ★NEW★  │ QR token drop   │
│ created_at       │ TIMESTAMP          │ Created         │
│ completed_at     │ TIMESTAMP          │ Completed       │
└──────────────────┴────────────────────┴─────────────────┘
```

## State Machine Flow

```
                    ┌──────────┐
                    │ OFFLINE  │
                    └────┬─────┘
                         │
                         ▼
                    ┌──────────┐
                    │  ONLINE  │◄──────────────────┐
                    └────┬─────┘                   │
                         │                         │
                         │ Task Assignment         │
                         ▼                         │
                    ┌──────────┐                   │
                    │ ASSIGNED │                   │
                    └────┬─────┘                   │
                         │                         │
                         │ Start Navigation        │
                         ▼                         │
               ┌──────────────────┐                │
               │ NAVIGATING_TO_   │                │
               │     DONOR        │                │
               └────────┬─────────┘                │
                        │                          │
                        │ ★ SCAN PICKUP QR ★       │
                        ▼                          │
               ┌──────────────────┐                │
               │ PICKUP_VERIFIED  │                │
               └────────┬─────────┘                │
                        │                          │
                        │ Start Transit            │
                        ▼                          │
               ┌──────────────────┐                │
               │   IN_TRANSIT     │                │
               └────────┬─────────┘                │
                        │                          │
                        │ ★ SCAN DELIVERY QR ★     │
                        ▼                          │
               ┌──────────────────┐                │
               │ DROPOFF_VERIFIED │                │
               └────────┬─────────┘                │
                        │                          │
                        ▼                          │
               ┌──────────────────┐                │
               │    COMPLETED     │                │
               └────────┬─────────┘                │
                        │                          │
                        └──────────────────────────┘
                         Return to ONLINE

         (Exception state can be triggered from any active state)
```

## Component Interaction Map

```
┌────────────────────────────────────────────────────────────────┐
│                        FLUTTER APP                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐  │
│  │  HomeScreen   │  │  RouteScreen  │  │ QRScannerModal   │  │
│  │               │  │               │  │                  │  │
│  │ - Status      │  │ - GoogleMap   │  │ - MobileScanner  │  │
│  │ - Tasks       │  │ - Markers     │  │ - Overlay        │  │
│  │               │  │ - Polylines   │  │ - Flash Toggle   │  │
│  └───────────────┘  └───────────────┘  └──────────────────┘  │
│         │                    │                     │           │
│         └────────────────────┼─────────────────────┘           │
│                              │                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              DATA LAYER                                  │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ TaskModel    │  │ TaskAPI      │  │ LocationSvc  │  │  │
│  │  │              │  │ Service      │  │              │  │  │
│  │  │ - Task       │  │ - Dio        │  │ - Geolocator │  │  │
│  │  │ - Location   │  │ - Verify     │  │ - GPS        │  │  │
│  │  │ - Status     │  │   Pickup     │  │              │  │  │
│  │  │              │  │ - Verify     │  │              │  │  │
│  │  │              │  │   Delivery   │  │              │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   API ENDPOINTS                          │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  /task/{id}/verify-pickup    ★ MODIFIED ★              │  │
│  │  /task/{id}/verify-dropoff   ★ MODIFIED ★              │  │
│  │  /task/create                                           │  │
│  │  /task/{id}/accept                                      │  │
│  │  /task/{id}/exception                                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                 │
│  ┌──────────────────┐  ┌──────────────────┐                  │
│  │  STATE MACHINE   │  │  SOCKET MANAGER  │                  │
│  │  (Preserved)     │  │  (Preserved)     │                  │
│  │                  │  │                  │                  │
│  │ - Transitions    │  │ - Broadcasts     │                  │
│  │ - Guards         │  │ - Real-time      │                  │
│  │ - Validation     │  │   Updates        │                  │
│  └──────────────────┘  └──────────────────┘                  │
│                              │                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                     MODELS                               │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  Task (+ pickup_token, delivery_token) ★ MODIFIED ★     │  │
│  │  Volunteer                                               │  │
│  │  Donor                                                   │  │
│  │  NGO                                                     │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ SQLAlchemy
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    SUPABASE POSTGRESQL                          │
├────────────────────────────────────────────────────────────────┤
│  - Tasks (with pickup_token & delivery_token)                  │
│  - Volunteers                                                   │
│  - Donors                                                       │
│  - NGOs                                                         │
│  - Performance Stats                                            │
│  - PostGIS Extension                                            │
└────────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌──────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  FRONTEND (Flutter)                                       │
│  ├─ google_maps_flutter      (Maps)                      │
│  ├─ mobile_scanner          (QR Scanning)                │
│  ├─ flutter_polyline_points (Route Drawing)              │
│  ├─ geolocator              (GPS Location)               │
│  ├─ dio                     (HTTP Client)                │
│  └─ provider                (State Management)           │
│                                                           │
│  BACKEND (Python)                                         │
│  ├─ FastAPI                 (Web Framework)              │
│  ├─ SQLAlchemy              (ORM - Async)                │
│  ├─ GeoAlchemy2             (PostGIS)                    │
│  ├─ Pydantic                (Validation)                 │
│  └─ python-socketio         (WebSocket)                  │
│                                                           │
│  DATABASE                                                 │
│  ├─ PostgreSQL              (Supabase)                   │
│  ├─ PostGIS                 (Geo Extension)              │
│  └─ Redis                   (Caching)                    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

**Legend**:
- ★ = New/Modified Feature
- ◄─► = Bidirectional Communication
- ─► = Unidirectional Flow
- ▼ = State Transition
