# M7 Logistics - Quick Setup Script (Windows)
# This script helps set up the new features

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "M7 Volunteer Module - Setup Script" -ForegroundColor Cyan
Write-Host "Maps & QR Verification Features" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Backend Setup
Write-Host "📦 Setting up Backend..." -ForegroundColor Yellow
Set-Location backend

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please ensure .env is configured with Supabase credentials" -ForegroundColor Red
    exit 1
}

Write-Host "✅ .env file found" -ForegroundColor Green

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "⚠️  IMPORTANT: Database Migration Required" -ForegroundColor Yellow
Write-Host "Please run the following SQL in your Supabase SQL Editor:" -ForegroundColor Yellow
Write-Host ""
Write-Host "-------------------------------------------" -ForegroundColor Cyan
Get-Content migrations/add_qr_tokens.sql
Write-Host "-------------------------------------------" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter once you've applied the migration"

# Start backend server
Write-Host ""
Write-Host "🚀 Starting Backend Server..." -ForegroundColor Yellow
Start-Process python -ArgumentList "main.py" -NoNewWindow
Write-Host "Backend server started" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📱 Setting up Flutter App..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Set-Location ../volunteer_app

# Install Flutter dependencies
Write-Host "Installing Flutter dependencies..." -ForegroundColor Yellow
flutter pub get

Write-Host ""
Write-Host "⚠️  IMPORTANT: Google Maps Configuration Required" -ForegroundColor Yellow
Write-Host ""
Write-Host "For Android, add to android/app/src/main/AndroidManifest.xml:" -ForegroundColor Yellow
Write-Host "<meta-data" -ForegroundColor Cyan
Write-Host '  android:name="com.google.android.geo.API_KEY"' -ForegroundColor Cyan
Write-Host '  android:value="YOUR_GOOGLE_MAPS_API_KEY"/>' -ForegroundColor Cyan
Write-Host ""
Write-Host "For iOS, add to ios/Runner/AppDelegate.swift:" -ForegroundColor Yellow
Write-Host "import GoogleMaps" -ForegroundColor Cyan
Write-Host 'GMSServices.provideAPIKey("YOUR_GOOGLE_MAPS_API_KEY")' -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter once you've configured Google Maps API key"

Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the Flutter app:" -ForegroundColor Yellow
Write-Host "  cd volunteer_app" -ForegroundColor Cyan
Write-Host "  flutter run" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend is running on: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
