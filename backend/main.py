from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from database import init_db
from routes import donations, auth

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Food Rescue Platform API",
    description="Backend API for Food Rescue Platform - NGO Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Debug Middleware
@app.middleware("http")
async def dbg_middleware(request: Request, call_next):
    print(f"📥 REQUEST: {request.method} {request.url}")
    origin = request.headers.get("origin")
    print(f"   Origin: {origin}")
    try:
        response = await call_next(request)
        print(f"ox Status: {response.status_code}")
        return response
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        raise e

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    # Allow any origin that matches these patterns
    allow_origin_regex=r"https?://.*", 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(donations.router)

# ============= Startup Event =============

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting Food Rescue Platform API...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # We don't raise here so the server can still start and show docs/errors
    
    print("📚 API Documentation available at: http://localhost:8000/docs")

# ============= Root Endpoint =============

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Food Rescue Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# ============= Health Check =============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Food Rescue Platform API"
    }
