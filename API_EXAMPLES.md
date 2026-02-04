# API Testing Examples

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently not implemented in the provided code. Add as needed:
```http
Authorization: Bearer YOUR_TOKEN_HERE
```

---

## 🔍 1. Create Task (Existing Endpoint)

### Request
```http
POST /task/create
Content-Type: application/json

{
  "donor_id": "123e4567-e89b-12d3-a456-426614174000",
  "ngo_id": "123e4567-e89b-12d3-a456-426614174001",
  "pickup_lat": 40.7128,
  "pickup_lng": -74.0060,
  "drop_lat": 40.7589,
  "drop_lng": -73.9851,
  "food_type": "Fresh Vegetables",
  "expiry_time": "2026-02-05T18:00:00Z",
  "requires_cooling": true
}
```

### Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "donor_id": "123e4567-e89b-12d3-a456-426614174000",
  "ngo_id": "123e4567-e89b-12d3-a456-426614174001",
  "volunteer_id": null,
  "distance_km": 5.42,
  "food_type": "Fresh Vegetables",
  "expiry_time": "2026-02-05T18:00:00Z",
  "requires_cooling": true,
  "status": "PENDING",
  "pickup_token": "A3B5C7",
  "delivery_token": "D8E9F0",
  "created_at": "2026-02-04T10:30:00Z"
}
```

**Note**: The task automatically gets `pickup_token` and `delivery_token` generated!

---

## ✅ 2. Verify Pickup (Modified Endpoint)

### Request
```http
POST /task/123e4567-e89b-12d3-a456-426614174002/verify-pickup
Content-Type: application/json

{
  "qr_token": "A3B5C7"
}
```

### Success Response (200 OK)
```json
{
  "status": "success",
  "message": "Pickup verified, starting transit to NGO",
  "new_task_status": "PICKED_UP"
}
```

### Error Responses

#### Invalid Token (400 Bad Request)
```json
{
  "detail": "Invalid pickup QR code"
}
```

#### Task Not Found (404 Not Found)
```json
{
  "detail": "Task not found"
}
```

#### Invalid State Transition (400 Bad Request)
```json
{
  "detail": "Invalid transition from COMPLETED to PICKUP_VERIFIED"
}
```

---

## ✅ 3. Verify Delivery (Modified Endpoint)

### Request
```http
POST /task/123e4567-e89b-12d3-a456-426614174002/verify-dropoff
Content-Type: application/json

{
  "qr_token": "D8E9F0"
}
```

### Success Response (200 OK)
```json
{
  "status": "success",
  "message": "Task completed successfully",
  "new_task_status": "COMPLETED"
}
```

### Error Responses

#### Invalid Token (400 Bad Request)
```json
{
  "detail": "Invalid delivery QR code"
}
```

#### Wrong State (400 Bad Request)
```json
{
  "detail": "Invalid transition from ASSIGNED to DROPOFF_VERIFIED"
}
```

---

## 📋 4. Get Task Details (Existing Endpoint)

### Request
```http
GET /task/123e4567-e89b-12d3-a456-426614174002
```

### Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "donor_id": "123e4567-e89b-12d3-a456-426614174000",
  "ngo_id": "123e4567-e89b-12d3-a456-426614174001",
  "volunteer_id": "123e4567-e89b-12d3-a456-426614174003",
  "distance_km": 5.42,
  "food_type": "Fresh Vegetables",
  "expiry_time": "2026-02-05T18:00:00Z",
  "requires_cooling": true,
  "status": "IN_TRANSIT",
  "pickup_token": "A3B5C7",
  "delivery_token": "D8E9F0",
  "created_at": "2026-02-04T10:30:00Z",
  "completed_at": null
}
```

---

## 🎯 5. Accept Task (Existing Endpoint)

### Request
```http
POST /task/123e4567-e89b-12d3-a456-426614174002/accept
Content-Type: application/json

{
  "volunteer_id": "123e4567-e89b-12d3-a456-426614174003"
}
```

### Response
```json
{
  "status": "success",
  "message": "Task accepted"
}
```

---

## 🔴 6. Report Exception (Existing Endpoint)

### Request
```http
POST /task/123e4567-e89b-12d3-a456-426614174002/exception
Content-Type: application/json

{
  "issue_type": "FLAT_TIRE",
  "description": "Got a flat tire on highway, need assistance"
}
```

### Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174004",
  "task_id": "123e4567-e89b-12d3-a456-426614174002",
  "issue_type": "FLAT_TIRE",
  "description": "Got a flat tire on highway, need assistance",
  "resolved": false,
  "reported_at": "2026-02-04T11:15:00Z"
}
```

---

## 🧪 Testing Workflow

### Complete Pickup → Delivery Flow

```bash
# 1. Create Task
curl -X POST http://localhost:8000/api/v1/task/create \
  -H "Content-Type: application/json" \
  -d '{
    "donor_id": "123e4567-e89b-12d3-a456-426614174000",
    "ngo_id": "123e4567-e89b-12d3-a456-426614174001",
    "pickup_lat": 40.7128,
    "pickup_lng": -74.0060,
    "drop_lat": 40.7589,
    "drop_lng": -73.9851,
    "food_type": "Fresh Vegetables",
    "expiry_time": "2026-02-05T18:00:00Z",
    "requires_cooling": true
  }'

# Save the task ID and tokens from response

# 2. Accept Task (if not auto-assigned)
curl -X POST http://localhost:8000/api/v1/task/{TASK_ID}/accept \
  -H "Content-Type: application/json" \
  -d '{
    "volunteer_id": "123e4567-e89b-12d3-a456-426614174003"
  }'

# 3. Verify Pickup
curl -X POST http://localhost:8000/api/v1/task/{TASK_ID}/verify-pickup \
  -H "Content-Type: application/json" \
  -d '{
    "qr_token": "A3B5C7"
  }'

# 4. Verify Delivery
curl -X POST http://localhost:8000/api/v1/task/{TASK_ID}/verify-dropoff \
  -H "Content-Type: application/json" \
  -d '{
    "qr_token": "D8E9F0"
  }'
```

---

## 📱 Flutter API Service Usage

### Verify Pickup
```dart
final taskApi = TaskApiService();

try {
  bool success = await taskApi.verifyPickup(
    'task-id-here',
    'A3B5C7'
  );
  
  if (success) {
    print('Pickup verified!');
  } else {
    print('Verification failed');
  }
} catch (e) {
  print('Error: $e');
}
```

### Verify Delivery
```dart
final taskApi = TaskApiService();

try {
  bool success = await taskApi.verifyDelivery(
    'task-id-here',
    'D8E9F0'
  );
  
  if (success) {
    print('Delivery verified! Task complete!');
  } else {
    print('Verification failed');
  }
} catch (e) {
  print('Error: $e');
}
```

### Get Task Details
```dart
final taskApi = TaskApiService();

Task? task = await taskApi.getTask('task-id-here');

if (task != null) {
  print('Task: ${task.foodType}');
  print('Status: ${task.status}');
  print('Pickup Token: ${task.pickupToken}');
  print('Delivery Token: ${task.deliveryToken}');
}
```

---

## 🎯 Postman Collection

Import this collection into Postman:

```json
{
  "info": {
    "name": "M7 Volunteer API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Verify Pickup",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"qr_token\": \"A3B5C7\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/task/{{task_id}}/verify-pickup",
          "host": ["http://localhost"],
          "port": "8000",
          "path": ["api", "v1", "task", "{{task_id}}", "verify-pickup"]
        }
      }
    },
    {
      "name": "Verify Delivery",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"qr_token\": \"D8E9F0\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/task/{{task_id}}/verify-dropoff",
          "host": ["http://localhost"],
          "port": "8000",
          "path": ["api", "v1", "task", "{{task_id}}", "verify-dropoff"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "task_id",
      "value": "your-task-id-here"
    }
  ]
}
```

---

## 🔒 Security Testing

### Test Invalid Token
```bash
curl -X POST http://localhost:8000/api/v1/task/{TASK_ID}/verify-pickup \
  -H "Content-Type: application/json" \
  -d '{
    "qr_token": "INVALID"
  }'

# Should return 400: Invalid pickup QR code
```

### Test Wrong State Transition
```bash
# Try to verify delivery before pickup
curl -X POST http://localhost:8000/api/v1/task/{TASK_ID}/verify-dropoff \
  -H "Content-Type: application/json" \
  -d '{
    "qr_token": "D8E9F0"
  }'

# Should return 400: Invalid transition
```

---

## 📊 Expected Status Codes

| Endpoint | Success | Invalid Token | Wrong State | Not Found |
|----------|---------|---------------|-------------|-----------|
| verify-pickup | 200 | 400 | 400 | 404 |
| verify-dropoff | 200 | 400 | 400 | 404 |

---

## 🐛 Debugging Tips

### Enable Verbose Logging
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Database
```sql
-- View task with tokens
SELECT id, status, pickup_token, delivery_token 
FROM tasks 
WHERE id = 'your-task-id';

-- View volunteer state
SELECT id, full_name, status 
FROM volunteers 
WHERE id = 'your-volunteer-id';
```

### Monitor WebSocket
Use browser console or WebSocket client to monitor real-time updates:
```javascript
const socket = io('http://localhost:8000');
socket.on('task_update', (data) => {
  console.log('Task updated:', data);
});
```

---

**Tip**: Use the FastAPI automatic docs at `http://localhost:8000/docs` for interactive API testing!
