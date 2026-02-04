#!/bin/bash

# M7 Logistics - Quick Setup Script
# This script helps set up the new features

echo "=========================================="
echo "M7 Volunteer Module - Setup Script"
echo "Maps & QR Verification Features"
echo "=========================================="
echo ""

# Backend Setup
echo "📦 Setting up Backend..."
cd backend

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please ensure .env is configured with Supabase credentials"
    exit 1
fi

echo "✅ .env file found"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "⚠️  IMPORTANT: Database Migration Required"
echo "Please run the following SQL in your Supabase SQL Editor:"
echo ""
echo "-------------------------------------------"
cat migrations/add_qr_tokens.sql
echo "-------------------------------------------"
echo ""
echo "Or connect via psql and run:"
echo "psql \"postgresql://postgres:surplusSync@12345@db.bwrwszeftkiwbybolzrh.supabase.co:5432/postgres\" < migrations/add_qr_tokens.sql"
echo ""

read -p "Press Enter once you've applied the migration..."

# Start backend server
echo ""
echo "🚀 Starting Backend Server..."
python main.py &
BACKEND_PID=$!
echo "Backend server started (PID: $BACKEND_PID)"

echo ""
echo "=========================================="
echo "📱 Setting up Flutter App..."
echo "=========================================="

cd ../volunteer_app

# Install Flutter dependencies
echo "Installing Flutter dependencies..."
flutter pub get

echo ""
echo "⚠️  IMPORTANT: Google Maps Configuration Required"
echo ""
echo "For Android, add to android/app/src/main/AndroidManifest.xml:"
echo "<meta-data"
echo "  android:name=\"com.google.android.geo.API_KEY\""
echo "  android:value=\"YOUR_GOOGLE_MAPS_API_KEY\"/>"
echo ""
echo "For iOS, add to ios/Runner/AppDelegate.swift:"
echo "import GoogleMaps"
echo "GMSServices.provideAPIKey(\"YOUR_GOOGLE_MAPS_API_KEY\")"
echo ""

read -p "Press Enter once you've configured Google Maps API key..."

echo ""
echo "✅ Setup Complete!"
echo ""
echo "To run the Flutter app:"
echo "  cd volunteer_app"
echo "  flutter run"
echo ""
echo "Backend is running on: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "To stop the backend server:"
echo "  kill $BACKEND_PID"
echo ""
