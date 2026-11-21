import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Academia–Industry Skill Mapping and Placement Portal"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security: Secret key for JWT encoding/decoding.
    # In production, this must be set via the SECRET_KEY environment variable.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sih2026-group-g29-skill-mapping-portal-secret-key-production-ready")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database: Supports PostgreSQL or SQLite fallback
    # To use PostgreSQL, set DATABASE_URL="postgresql://user:password@localhost:5432/skill_portal"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./skill_portal.db")
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    # Upload storage directory
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

    class Config:
        case_sensitive = True

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
