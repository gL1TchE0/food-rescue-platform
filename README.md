# Food Rescue NGO Platform

A comprehensive mobile and web platform designed to streamline food rescue operations by connecting verified NGOs with food donors and volunteers. This application helps manage donations, track pickups, and ensure food safety compliance.

##  Features

- **For NGOs:**
  - Register with license verification.
  - Manage multiple operating branches/locations.
  - View and claim available food donations in real-time.
  - Track storage capacity and inventory.
  - Generate QR codes for secure pickups.

- **For Volunteers:**
  - ID verification and profile management.
  - Availability scheduling for efficient matching.
  - Training resources for food safety procedures.

- **Platform Safety:**
  - Robust authentication and role-based access.
  - Admin tools for monitoring and suspending suspicious accounts.
  - Rating system for trust and safety.

##  Tech Stack

### Frontend (Mobile App)
- **Framework:** Flutter (Dart)
- **Key Packages:**
  - \http\: API communication
  - \qr_flutter\: QR code generation for pickups
  - \shared_preferences\: Local data persistence
  - \intl\: Date and time formatting

### Backend (API)
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL (via SQLAlchemy ORM)
- **Authentication:** JWT (JSON Web Tokens)
- **Key Libraries:** \uvicorn\, \pydantic\, \passlib\

##  Getting Started

### Prerequisites
- Flutter SDK (>=3.0.0)
- Python (>=3.8)
- PostgreSQL Database

### 1. Backend Setup
1. Navigate to the backend directory:
   \\\ash
   cd backend
   \\\
2. Install dependencies:
   \\\ash
   pip install -r requirements.txt
   \\\
3. Run the server:
   \\\ash
   uvicorn main:app --reload
   \\\
   The API will be available at \http://localhost:8000\.

### 2. Mobile App Setup
1. Navigate to the project root.
2. Install dependencies:
   \\\ash
   flutter pub get
   \\\
3. **Configure API URL**:
   Edit \lib/config/api_config.dart\ to point to your backend:
   \\\dart
   // For Android Emulator
   static const String baseUrl = 'http://10.0.2.2:8000';
   // For iOS Simulator
   static const String baseUrl = 'http://localhost:8000';
   \\\
4. Run the application:
   \\\ash
   flutter run
   \\\

##  Project Structure
- \lib/\: Flutter application source code.
  - \screens/\: UI screens (Dashboard, Claiming, Profile).
  - \widgets/\: Reusable UI components.
  - \services/\: API service integration.
  - \models/\: Data models.
- \ackend/\: FastAPI backend source code.
  - \outes/\: API endpoints.
  - \schemas.py\: Pydantic models.
  - \models.py\: Database models.
