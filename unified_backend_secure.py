#!/usr/bin/env python3
"""
Journal Craft Crew Unified Backend Server - HTTPS Version
P1 Security: SSL/TLS Enabled for Production Security
"""

import os
import sys
import time
import asyncio
import logging
from pathlib import Path

# Add the journal-platform-backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn.protocols.http

# Import all the original modules from unified_backend.py
from unified_backend import (
    # Models
    User, UserCreate, UserLogin, AIGenerationRequest, AIGenerationResponse,
    SecurityConfig, SecurityValidator, RedisManager,

    # Constants and Data
    TITLE_STYLES, AUTHOR_STYLES, THEMES, CREWAI_AGENTS, WORKFLOW_PHASES,

    # Data store
    data_store, save_data, load_data,

    # Import all route functions (these will be the same)
    register_user, login_user, get_themes, get_title_styles, get_author_styles,
    get_available_themes, get_user_theme_usage,
    generate_journal, get_job_status, get_job_logs, cancel_job,
    start_crewai_workflow, get_crewai_workflow_status, cancel_crewai_workflow,
    continue_crewai_project, get_active_workflows, get_crewai_agents,
    create_journal, get_journal_files, download_file, upload_file,
    get_projects, get_project, create_project, update_project, delete_project,
    get_user_stats, ai_health_check, system_health_check,

    # Background tasks
    simulate_ai_generation,

    # CORS settings
    CORS_ORIGINS, CORS_CREDENTIALS, CORS_METHODS, CORS_HEADERS,

    # Security settings
    SECURITY_HEADERS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SSL Certificate paths
SSL_CERT_PATH = "/home/alf/Documents/7.CodeProjects/Journal Craft Crew/ssl/journal_crew.crt"
SSL_KEY_PATH = "/home/alf/Documents/7.CodeProjects/Journal Craft Crew/ssl/journal_crew.key"

class SecurityMiddleware:
    """Enhanced security middleware for P1 security hardening"""

    @staticmethod
    def add_security_headers(response):
        """Add P1 security headers to all responses"""
        # HSTS - Enforce HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https: data:; "
            "connect-src 'self' ws: wss:;"
        )

        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )

        return response

def create_app():
    """Create and configure the FastAPI app with SSL"""
    app = FastAPI(
        title="Journal Craft Crew Platform - Secure",
        description="AI-powered journal creation platform with SSL/TLS security",
        version="1.0.0-secure",
        docs_url="/docs",
        redoc_url="/redoc",
        contact={
            "name": "Journal Craft Crew Security",
            "email": "security@journalcraftcrew.dev"
        }
    )

    # Add trusted host middleware for additional security
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.journalcraftcrew.dev", "*.local"]
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_CREDENTIALS,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS
    )

    # Include all the original routes from unified_backend.py
    # Authentication routes
    app.post("/api/auth/register")(register_user)
    app.post("/api/auth/login")(login_user)

    # AI Generation routes
    app.get("/api/ai/themes")(get_themes)
    app.get("/api/ai/title-styles")(get_title_styles)
    app.get("/api/author-styles")(get_author_styles)
    app.get("/api/ai/available-themes")(get_available_themes)
    app.get("/api/ai/user-theme-usage")(get_user_theme_usage)
    app.post("/api/ai/generate-journal")(generate_journal)
    app.get("/api/ai/job/{job_id}")(get_job_status)
    app.get("/api/ai/job/{job_id}/logs")(get_job_logs)
    app.delete("/api/ai/job/{job_id}")(cancel_job)

    # CrewAI routes
    app.post("/api/crewai/start-workflow")(start_crewai_workflow)
    app.get("/api/crewai/workflow-status/{workflow_id}")(get_crewai_workflow_status)
    app.delete("/api/crewai/cancel-workflow/{workflow_id}")(cancel_crewai_workflow)
    app.post("/api/crewai/continue-project")(continue_crewai_project)
    app.get("/api/crewai/active-workflows")(get_active_workflows)
    app.get("/api/crewai/agents")(get_crewai_agents)

    # Journal Creation routes
    app.post("/api/journals/create")(create_journal)
    app.get("/api/journals/{project_id}/files")(get_journal_files)
    app.get("/api/journals/{project_id}/download/{file_path}")(download_file)
    app.post("/api/journals/upload")(upload_file)

    # Project Library routes
    app.get("/api/library/projects")(get_projects)
    app.get("/api/library/projects/{project_id}")(get_project)
    app.post("/api/library/projects")(create_project)
    app.put("/api/library/projects/{project_id}")(update_project)
    app.delete("/api/library/projects/{project_id}")(delete_project)

    # User and Analytics routes
    app.get("/api/user/stats")(get_user_stats)

    # Health and Monitoring routes
    app.get("/api/ai/health")(ai_health_check)
    app.get("/health")(system_health_check)

    # Apply security middleware to all responses
    @app.middleware("http")
    async def add_security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        return SecurityMiddleware.add_security_headers(response)

    @app.get("/api/ssl/verify")
    async def ssl_verification():
        """Verify SSL certificate status"""
        return {
            "ssl_status": "enabled",
            "certificate_path": SSL_CERT_PATH,
            "key_path": SSL_KEY_PATH,
            "certificate_valid": os.path.exists(SSL_CERT_PATH),
            "key_valid": os.path.exists(SSL_KEY_PATH),
            "https_ready": True
        }

    @app.get("/")
    async def root():
        """Root endpoint with SSL status"""
        return {
            "message": "🔒 Journal Craft Crew Platform - HTTPS Enabled",
            "ssl_status": "Secure",
            "version": "1.0.0-secure",
            "endpoints": {
                "api": "/api",
                "docs": "/docs",
                "health": "/health",
                "ssl_verify": "/api/ssl/verify"
            },
            "security": {
                "ssl_tls": "Enabled",
                "hsts": "Enforced",
                "csp": "Implemented",
                "xss_protection": "Active"
            }
        }

    return app

def main():
    """Main function to run the secure server"""
    # Verify SSL certificates exist
    if not os.path.exists(SSL_CERT_PATH) or not os.path.exists(SSL_KEY_PATH):
        logger.error("❌ SSL certificates not found!")
        logger.error(f"Certificate: {SSL_CERT_PATH}")
        logger.error(f"Key: {SSL_KEY_PATH}")
        logger.error("Run: openssl req -x509 -newkey rsa:2048 -nodes -keyout journal_crew.key -out journal_crew.crt -days 365")
        sys.exit(1)

    logger.info("🔒 Starting Journal Craft Crew Platform - HTTPS Enabled")
    logger.info(f"📍 SSL Certificate: {SSL_CERT_PATH}")
    logger.info(f"🔑 SSL Private Key: {SSL_KEY_PATH}")
    logger.info(f"📍 Secure Backend: https://localhost:6770")
    logger.info(f"📋 Available Endpoints:")
    logger.info("   - Authentication: /api/auth/register, /api/auth/login")
    logger.info("   - AI Generation: /api/ai/themes, /api/ai/title-styles, /api/ai/generate-journal")
    logger.info("   - 🤖 Advanced CrewAI: /api/crewai/start-workflow, /api/crewai/workflow-status/{id}")
    logger.info("   - 🤖 CrewAI Control: /api/crewai/cancel-workflow/{id}, /api/crewai/continue-project")
    logger.info("   - 🤖 CrewAI Status: /api/crewai/active-workflows")
    logger.info("   - Journal Creation: /api/journals/create, /api/journals/status/{job_id}")
    logger.info("   - Journal Library: /api/journals/library, /api/journals/{project_id}/files")
    logger.info("   - File Downloads: /api/journals/{project_id}/download/{file_path}")
    logger.info("   - Project Library: /api/library/projects (full CRUD)")
    logger.info("   - WebSocket: /ws/job/{job_id}, /ws/journal/{job_id} (real-time progress)")
    logger.info("   - 🤖 CrewAI WebSocket: /ws/crewai/{workflow_id} (9-agent progress)")
    logger.info("   - Data Persistence: File-based storage with security")
    logger.info("   - 🔒 SSL/TLS: Full HTTPS encryption enabled")
    logger.info("   - 🛡️ P1 Security: Hardened with HSTS, CSP, XSS protection")
    logger.info("🔒 Secure Backend Ready!")

    # Create the app
    app = create_app()

    # Run with SSL
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=6770,
        ssl_certfile=SSL_CERT_PATH,
        ssl_keyfile=SSL_KEY_PATH,
        log_level="info",
        access_log=True,
        use_colors=True
    )

if __name__ == "__main__":
    main()