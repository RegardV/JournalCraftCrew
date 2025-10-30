#!/usr/bin/env python3
"""
Journal Platform Backend - FastAPI Application
Phase 3: Backend Development
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import uvicorn
import asyncio
import logging

# Import our modules (will be created)
from app.core.config import settings
from app.api.routes import auth, users, projects, themes, export

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class JournalPlatformAPI(FastAPI):
    """Main FastAPI application for journaling platform"""

    def __init__(self):
        super().__init__(
            title="Journal Platform API",
            description="Comprehensive journaling platform backend services",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )

        # Add CORS middleware
        self.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add trusted host middleware
        self.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )

app = JournalPlatformAPI()

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["User Management"])
app.include_router(projects.router, prefix="/api/projects", tags=["Project Management"])
app.include_router(themes.router, prefix="/api/themes", tags=["Theme Engine"])
app.include_router(export.router, prefix="/api/export", tags=["Export Service"])

# Health check endpoint
@app.get("/health", status_code=200, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "journal-platform-api"}

@app.get("/", status_code=200, tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Journal Platform API",
        "version": "1.0.0",
        "description": "Comprehensive journaling platform backend services",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    # Configure logging for production
    logging.info("Starting Journal Platform API server...")

    # Run the application
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )