"""
Journal Platform Backend Configuration
Phase 3: Backend Development
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Journal Platform API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:5173",  # Vite dev server
        "https://yourdomain.com",    # Production domain
    ]
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0"
    ]

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost/journal_platform"
    )

    # Redis
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://yourdomain.com"
    ]

    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    # Email (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Amazon KDP
    KDP_ACCESS_KEY: Optional[str] = os.getenv("KDP_ACCESS_KEY")
    KDP_SECRET_KEY: Optional[str] = os.getenv("KDP_SECRET_KEY")
    KDP_MARKETPLACE: str = "ATVPDKDK"  # Amazon Kindle Direct Publishing

    # OAuth2 Settings
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GITHUB_CLIENT_ID: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")

    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    LOG_LEVEL: str = "INFO"

# Create settings instance
settings = Settings()