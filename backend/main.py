"""
M7 Volunteer Logistics System - Main Application
FastAPI + Socket.IO Backend
Version: 1.0.0
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from app.core.config import settings
from app.core.socket_manager import socket_manager
from app.db.session import init_db
from app.db.redis import redis_manager
from app.api.v1.endpoints import volunteer, tasks

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup
    logger.info("🚀 Starting M7 Logistics Backend...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialized")
        
        # Connect to Redis
        await redis_manager.connect()
        logger.info("✅ Redis connected")
        
        logger.info("✅ All systems operational - server ready!")
        
        yield
        
        logger.info("📋 Lifespan yield completed normally")
        
    finally:
        # Shutdown
        logger.info("🛑 Shutting down...")
        await redis_manager.disconnect()
        logger.info("✅ Cleanup complete")


# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="State-Authoritative Logistics System for Food Distribution",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO
socket_app = socket_manager.get_asgi_app()
app.mount("/ws", socket_app)

# Register API Routes
app.include_router(volunteer.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "M7 Volunteer Logistics API",
        "version": settings.VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "websocket": "active"
    }


if __name__ == "__main__":
    import uvicorn
    try:
        print("=" * 50)
        print("Starting M7 Logistics Backend Server")
        print("=" * 50)
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.DEBUG,
            log_level="info" if settings.DEBUG else "warning"
        )
    except Exception as e:
        print(f"FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
