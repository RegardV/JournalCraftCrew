#!/usr/bin/env python3
"""
Simple FastAPI Test Server
Minimal setup to test our API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from typing import Dict, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Journal Platform API - Test Mode",
    description="Simple test server for Phase 1 implementation"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add HTTPS redirect
app.add_middleware(HTTPSRedirectMiddleware)

# Simple test endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Journal Craft Crew Phase 1 API - Test Server",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "register": "/api/auth/register",
            "login": "/api/auth/login",
            "ai_generation": "/api/ai/generate-journal",
            "project_library": "/api/library/projects"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "journal-platform-api-test",
        "timestamp": "2025-10-27T10:15:00Z"
    }

@app.post("/api/test/echo")
async def echo_endpoint(request: Dict[str, Any]):
    """Echo endpoint for testing"""
    try:
        body = await request.json()
        logger.info(f"Received test request: {body}")
        return {
            "success": True,
            "received": body,
            "echo": f"Echo: {body}"
        }
    except Exception as e:
        logger.error(f"Echo endpoint error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Simulate AI generation endpoint (without actual AI agents)
@app.post("/api/ai/generate-journal-test")
async def test_ai_generation():
    """Test AI generation endpoint"""
    return {
        "message": "AI generation test endpoint",
        "job_id": f"test_job_{int(time.time())}",
        "status": "pending",
        "estimated_time": 180
    }

@app.get("/api/ai/progress/{job_id}")
async def test_progress(job_id: str):
    """Test progress tracking endpoint"""
    return {
        "job_id": job_id,
        "status": "in_progress",
        "progress_percentage": 50,
        "current_stage": "Testing AI generation workflow"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Journal Platform Test Server")
    print("📍 Backend: http://localhost:8000")
    print("📍 Health Check: http://localhost:8000/health")
    print("📍 Frontend: http://localhost:5173")
    print("📋 Available Test Endpoints:")
    print("   - http://localhost:8000/health")
    print("   - http://localhost:8000/api/test/echo")
    print("   - http://localhost:8000/api/ai/generate-journal-test")
    print("   - http://localhost:8000/api/ai/progress/{job_id}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )