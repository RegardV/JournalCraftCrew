#!/usr/bin/env python3
"""
Journal Platform Backend - Main Application
Phase 3: Backend Development
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, close_db, db_manager
from app.api.dependencies import get_db
from app.api.routes import auth, users, projects, themes, exports, ai_generation, websocket_endpoints, project_library, onboarding, crewai_workflow, journal_content_analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.LOG_LEVEL == "INFO" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", mode="a")
    ]
)

# Create FastAPI application
app = FastAPI(
    title="Journal Platform API",
    description="Comprehensive journaling platform backend services",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url="/docs" if not settings.DEBUG else None,
    redoc_url="/redoc" if not settings.DEBUG else None
)

# Add middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API routes with tags
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["User Management"])
app.include_router(projects.router, prefix="/api/projects", tags=["Project Management"])
app.include_router(themes.router, prefix="/api/themes", tags=["Theme Engine"])
app.include_router(exports.router, prefix="/api/export", tags=["Export Service"])
app.include_router(ai_generation.router, prefix="/api/ai", tags=["AI Generation"])
app.include_router(websocket_endpoints.router, tags=["WebSocket"])
app.include_router(project_library.router, prefix="/api", tags=["Project Library"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["Onboarding Agent"])
app.include_router(crewai_workflow.router, prefix="/api/crewai", tags=["CrewAI Workflow"])
app.include_router(journal_content_analysis.router, prefix="/api/journal-content", tags=["Journal Content Analysis"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logging.error(f"Global error: {exc}")
    return {
        "detail": str(exc),
        "status_code": 500,
        "error": "Internal server error"
    }

# Health check endpoint
@app.get("/health", status_code=200, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        import os
        import sys
        from datetime import datetime

        # Database health check
        db_health = await db_manager.health_check()

        overall_status = "healthy" if db_health["status"] == "healthy" else "unhealthy"

        return {
            "status": overall_status,
            "service": "journal-platform-api",
            "database": db_health,
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "python_version": sys.version,
                "platform": os.name,
                "architecture": "x64" if sys.maxsize > 0 else "x86"
            }
        }
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "journal-platform-api",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/", status_code=200, tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Journal Platform API",
        "version": "1.0.0",
        "description": "Comprehensive journaling platform backend services",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "authentication": "/api/auth",
            "users": "/api/users",
            "projects": "/api/projects",
            "themes": "/api/themes",
            "export": "/api/export",
            "ai_generation": "/api/ai",
            "websocket": "/ws",
            "project_library": "/api/library",
            "onboarding": "/api/onboarding",
            "crewai_workflow": "/api/crewai"
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logging.info("Starting Journal Platform API server...")
    logging.info(f"Environment: {'development' if settings.DEBUG else 'production'}")
    logging.info(f"Database URL: {settings.DATABASE_URL}")
    logging.info(f"Listening on port {settings.PORT}")

    # Initialize database
    try:
        await init_db()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        # Don't fail startup for development environment
        if not settings.DEBUG:
            raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logging.info("Shutting down Journal Platform API server...")
    try:
        await close_db()
        logging.info("Database connections closed")
    except Exception as e:
        logging.error(f"Error closing database connections: {e}")

# Main execution
if __name__ == "__main__":
    # Configure logging for production
    if not settings.DEBUG:
        logging.getLogger("uvicorn.error").propagate = False
        logging.getLogger("uvicorn.access").propagate = False

    # Create async context manager for lifespan management
    @asynccontextmanager.asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        logging.info("Application starting up...")

        yield

        # Shutdown
        logging.info("Application shutting down...")

    # Run application
    import uvicorn
    try:
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            log_level="info",
            access_log=True,
            lifespan=lifespan
        )
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
    except Exception as e:
        logging.error(f"Application failed to start: {e}")
        raise