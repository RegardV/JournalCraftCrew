#!/usr/bin/env python3
"""
Working Backend Server for Journal Craft Crew Phase 1
Provides all API endpoints that the frontend expects, without complex dependencies
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List, Optional
import json
import asyncio
import time
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Journal Platform API - Working Version",
    description="Backend API with all endpoints frontend expects"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str
    profile_type: str = "personal_journaler"

class UserLogin(BaseModel):
    email: str
    password: str

class AIGenerationRequest(BaseModel):
    theme: str
    title_style: str
    description: Optional[str] = None

class CustomizationSettings(BaseModel):
    layout: str = "single-column"
    font_size: str = "medium"
    color_scheme: str = "default"
    paper_type: str = "standard"
    binding_type: str = "perfect"

# In-memory storage (for demo purposes)
users_db = {}
projects_db = {}
ai_jobs = {}
ws_connections = {}

# Available themes
AVAILABLE_THEMES = [
    {
        "id": "mindfulness",
        "name": "Mindfulness & Meditation",
        "description": "Daily prompts for mindfulness and meditation practice",
        "estimated_days": 30
    },
    {
        "id": "productivity",
        "name": "Productivity Focus",
        "description": "Prompts to boost productivity and goal achievement",
        "estimated_days": 30
    },
    {
        "id": "creativity",
        "name": "Creative Writing",
        "description": "Sparks for creative writing and artistic expression",
        "estimated_days": 30
    },
    {
        "id": "gratitude",
        "name": "Gratitude Practice",
        "description": "Daily gratitude and positive reflection prompts",
        "estimated_days": 30
    }
]

# Available title styles
TITLE_STYLES = [
    {"id": "inspirational", "name": "Inspirational Quotes", "examples": ["Find Your Inner Peace", "The Journey Within"]},
    {"id": "minimalist", "name": "Minimalist Clean", "examples": ["Mindfulness Journal", "Daily Reflections"]},
    {"id": "creative", "name": "Creative & Artistic", "examples": ["Soulful Pages", "Whispers of Mind"]},
    {"id": "professional", "name": "Professional Focus", "examples": ["Executive Mindfulness", "Productivity Planner"]}
]

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        self.active_connections[job_id] = websocket
        logger.info(f"WebSocket connected for job {job_id}")

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]
            logger.info(f"WebSocket disconnected for job {job_id}")

    async def send_progress(self, job_id: str, progress_data: dict):
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_text(json.dumps(progress_data))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                self.disconnect(job_id)

manager = ConnectionManager()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Journal Craft Crew Backend API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "journal-platform-api",
        "timestamp": "2025-10-27T10:15:00Z"
    }

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user_data: UserRegistration):
    try:
        # Simulate user creation
        user_id = f"user_{len(users_db) + 1}"

        # Determine AI credits based on profile type
        ai_credits = 50 if user_data.profile_type == "content_creator" else 10

        users_db[user_id] = {
            "id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "profile_type": user_data.profile_type,
            "ai_credits": ai_credits,
            "created_at": time.time()
        }

        logger.info(f"User registered: {user_data.email}")

        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "email": user_data.email,
                "full_name": user_data.full_name,
                "profile_type": user_data.profile_type,
                "ai_credits": ai_credits
            }
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login_user(login_data: UserLogin):
    # Simple mock login (in production, verify password hash)
    user = None
    for uid, user_data in users_db.items():
        if user_data["email"] == login_data.email:
            user = user_data
            break

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Mock JWT token
    token = f"mock_token_{uuid.uuid4().hex[:16]}"

    return {
        "success": True,
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

# AI Generation endpoints
@app.get("/api/ai/themes")
async def get_available_themes():
    return {
        "themes": AVAILABLE_THEMES,
        "count": len(AVAILABLE_THEMES)
    }

@app.get("/api/ai/title-styles")
async def get_title_styles():
    return {
        "title_styles": TITLE_STYLES,
        "count": len(TITLE_STYLES)
    }

@app.post("/api/ai/generate-journal")
async def generate_journal(request: AIGenerationRequest):
    try:
        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Simulate starting AI generation job
        ai_jobs[job_id] = {
            "id": job_id,
            "status": "pending",
            "theme": request.theme,
            "title_style": request.title_style,
            "description": request.description,
            "progress": 0,
            "created_at": time.time()
        }

        # Start background task to simulate AI generation
        asyncio.create_task(simulate_ai_generation(job_id))

        logger.info(f"AI generation started: {job_id}")

        return {
            "success": True,
            "message": "AI journal generation started",
            "job_id": job_id,
            "estimated_time": 180,  # 3 minutes
            "status": "pending"
        }
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/progress/{job_id}")
async def get_generation_progress(job_id: str):
    if job_id not in ai_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = ai_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress_percentage": job["progress"],
        "current_stage": f"Processing ({job['progress']}%)",
        "estimated_time_remaining": max(0, 180 - (time.time() - job["created_at"])),
        "created_at": job["created_at"]
    }

# WebSocket endpoint for real-time progress
@app.websocket("/ws/job/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(job_id)

# Project Library endpoints
@app.get("/api/library/projects")
async def get_user_projects():
    # Mock user projects
    user_projects = []
    for pid, project in projects_db.items():
        user_projects.append(project)

    return {
        "projects": user_projects,
        "count": len(user_projects),
        "page": 1,
        "total_pages": 1
    }

@app.get("/api/library/projects/{project_id}")
async def get_project_details(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    return {
        "project": project,
        "success": True
    }

@app.put("/api/library/projects/{project_id}")
async def update_project(project_id: str, settings: CustomizationSettings):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update project settings
    projects_db[project_id]["customization"] = settings.dict()
    projects_db[project_id]["updated_at"] = time.time()

    return {
        "success": True,
        "message": "Project updated successfully",
        "project": projects_db[project_id]
    }

@app.delete("/api/library/projects/{project_id}")
async def delete_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    del projects_db[project_id]
    return {
        "success": True,
        "message": "Project deleted successfully"
    }

# Background task to simulate AI generation
async def simulate_ai_generation(job_id: str):
    """Simulate the AI generation process with progress updates"""
    stages = [
        (10, "Initializing AI agents..."),
        (25, "Curating content themes..."),
        (40, "Generating daily prompts..."),
        (60, "Creating journal structure..."),
        (80, "Formatting content..."),
        (95, "Finalizing design..."),
        (100, "Complete!")
    ]

    for progress, stage in stages:
        await asyncio.sleep(2)  # Simulate processing time

        if job_id in ai_jobs:
            ai_jobs[job_id]["progress"] = progress
            ai_jobs[job_id]["current_stage"] = stage

            # Send WebSocket update
            progress_data = {
                "type": "progress",
                "job_id": job_id,
                "progress": progress,
                "stage": stage,
                "timestamp": time.time()
            }
            await manager.send_progress(job_id, progress_data)

    # Create completed project
    if job_id in ai_jobs:
        ai_jobs[job_id]["status"] = "completed"

        # Create a mock project
        project_id = f"project_{uuid.uuid4().hex[:12]}"
        job = ai_jobs[job_id]

        projects_db[project_id] = {
            "id": project_id,
            "title": f"{job['title_style'].title()} {job['theme'].title()} Journal",
            "theme": job["theme"],
            "description": job.get("description", f"AI-generated {job['theme']} journal"),
            "status": "completed",
            "created_at": time.time(),
            "updated_at": time.time(),
            "customization": {
                "layout": "single-column",
                "font_size": "medium",
                "color_scheme": "default",
                "paper_type": "standard",
                "binding_type": "perfect"
            },
            "pages_count": 30,
            "word_count": 15000,
            "export_formats": ["pdf", "epub", "kdp"]
        }

        # Send completion notification
        completion_data = {
            "type": "completed",
            "job_id": job_id,
            "project_id": project_id,
            "message": "Journal generation completed!",
            "timestamp": time.time()
        }
        await manager.send_progress(job_id, completion_data)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Journal Craft Crew Working Backend Server")
    print("📍 Backend: http://localhost:8000")
    print("📍 Health Check: http://localhost:8000/health")
    print("📍 Frontend: http://localhost:5173")
    print("📋 Available Endpoints:")
    print("   - Authentication: /api/auth/register, /api/auth/login")
    print("   - AI Generation: /api/ai/themes, /api/ai/title-styles, /api/ai/generate-journal")
    print("   - Project Library: /api/library/projects")
    print("   - WebSocket: /ws/job/{job_id}")
    print("🎯 Frontend Integration Ready!")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )