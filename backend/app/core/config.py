"""
M7 Logistics - Configuration Management
Centralized configuration using Pydantic Settings
"""
from pydantic import validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache
from pathlib import Path

# Get the .env file path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application Settings"""
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        case_sensitive=True,
        extra='ignore'
    )
    
    # Application
    APP_NAME: str = "M7 Volunteer Logistics API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "M7 Logistics System"
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, any]) -> any:
        if isinstance(v, str):
            return v
        return f"postgresql+psycopg2://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str | None = None

    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: str | None, values: dict[str, any]) -> any:
        if isinstance(v, str):
            return v
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    # Firebase
    FIREBASE_PROJECT_ID: str
    FIREBASE_SERVER_KEY: str
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: str = "./firebase-service-account.json"
    
    # Mapbox
    MAPBOX_ACCESS_TOKEN: str
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # WebSocket
    SOCKET_IO_CORS_ALLOWED_ORIGINS: str = "*"
    
    # Task Assignment
    MAX_ASSIGNMENT_RADIUS_KM: float = 10.0  # Max distance for volunteer assignment
    LOCATION_UPDATE_INTERVAL_SEC: int = 5   # GPS update frequency
    TASK_EXPIRY_BUFFER_HOURS: int = 2       # Hours before expiry to alert


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
