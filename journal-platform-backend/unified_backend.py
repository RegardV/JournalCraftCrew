#!/usr/bin/env python3
"""
Unified Backend Server for Journal Craft Crew
Combines the complete functionality of working_server.py with production-grade security
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, List, Optional
import json
import asyncio
import time
import uuid
import logging
import os
import secrets
import glob
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

# Import CrewAI integration
from crewai_integration import journal_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# File-based data persistence
DATA_FILE = "unified_data.json"

def load_data():
    """Load data from file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {
                "users": {},
                "projects": {},
                "sessions": {},
                "ai_jobs": {}
            }
    return {
        "users": {},
        "projects": {},
        "sessions": {},
        "ai_jobs": {}
    }

def save_data(data):
    """Save data to file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info("Data saved successfully")
    except Exception as e:
        logger.error(f"Error saving data: {e}")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    return bcrypt.verify(plain_password, hashed_password)

# JWT functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Initialize data
data_store = load_data()

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        user_id = payload.get("user_id")
        if user_id is None or user_id not in data_store["users"]:
            raise credentials_exception
        return data_store["users"][user_id]
    except JWTError:
        raise credentials_exception

# Create FastAPI app
app = FastAPI(
    title="Journal Platform - Unified Backend",
    description="Complete backend with all functionality and production-grade security"
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
    email: EmailStr
    password: str
    full_name: str
    profile_type: str = "personal_journaler"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"

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

# Journal Creation Models
class JournalPreferences(BaseModel):
    theme: str = Field(..., description="Journal theme (e.g., 'Journaling for Anxiety')")
    title: str = Field(..., description="Journal title")
    titleStyle: str = Field(..., description="Title style preference")
    authorStyle: str = Field(..., description="Author writing style")
    researchDepth: str = Field(..., description="Research depth: 'light', 'medium', or 'deep'")

class JournalCreationRequest(BaseModel):
    preferences: JournalPreferences

class JournalProgress(BaseModel):
    jobId: str
    status: str  # 'starting', 'research', 'curation', 'editing', 'pdf', 'completed', 'error'
    progress: int  # 0-100
    currentAgent: str
    message: str
    estimatedTimeRemaining: int

# Available themes and styles
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
        "message": "Journal Craft Crew Unified Backend API",
        "version": "2.0.0",
        "status": "running",
        "features": ["Authentication", "AI Generation", "Real-time Progress", "Project Management"]
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "journal-platform-unified-api",
        "timestamp": "2025-10-29T10:15:00Z",
        "data_file": DATA_FILE,
        "users_count": len(data_store["users"]),
        "projects_count": len(data_store["projects"])
    }

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user_data: UserRegistration):
    try:
        # Check if user already exists
        for uid, existing_user in data_store["users"].items():
            if existing_user["email"] == user_data.email:
                raise HTTPException(status_code=400, detail="Email already registered")

        # Generate user ID
        user_id = f"user_{uuid.uuid4().hex[:12]}"

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Determine AI credits based on profile type
        ai_credits = 50 if user_data.profile_type == "content_creator" else 10

        # Create user
        user = {
            "id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "profile_type": user_data.profile_type,
            "ai_credits": ai_credits,
            "hashed_password": hashed_password,
            "created_at": time.time()
        }

        data_store["users"][user_id] = user
        save_data(data_store)

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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=TokenData)
async def login_user(login_data: UserLogin):
    # Find user by email
    user = None
    for uid, user_data in data_store["users"].items():
        if user_data["email"] == login_data.email:
            user = user_data
            break

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user["id"]}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
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
async def generate_journal(request: AIGenerationRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Check user credits
        if current_user["ai_credits"] <= 0:
            raise HTTPException(status_code=402, detail="Insufficient AI credits")

        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Create AI generation job
        ai_job = {
            "id": job_id,
            "user_id": current_user["id"],
            "status": "pending",
            "theme": request.theme,
            "title_style": request.title_style,
            "description": request.description,
            "progress": 0,
            "created_at": time.time()
        }

        data_store["ai_jobs"][job_id] = ai_job
        save_data(data_store)

        # Start background task to simulate AI generation
        asyncio.create_task(simulate_ai_generation(job_id))

        logger.info(f"AI generation started: {job_id} by user {current_user['id']}")

        return {
            "success": True,
            "message": "AI journal generation started",
            "job_id": job_id,
            "estimated_time": 180,  # 3 minutes
            "status": "pending"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/progress/{job_id}")
async def get_generation_progress(job_id: str, current_user: dict = Depends(get_current_user)):
    if job_id not in data_store["ai_jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")

    job = data_store["ai_jobs"][job_id]

    # Verify job belongs to current user
    if job["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress_percentage": job["progress"],
        "current_stage": job.get("current_stage", f"Processing ({job['progress']}%)"),
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
async def get_user_projects(current_user: dict = Depends(get_current_user)):
    # Get user's projects
    user_projects = []
    for pid, project in data_store["projects"].items():
        if project.get("user_id") == current_user["id"]:
            user_projects.append(project)

    return {
        "projects": user_projects,
        "count": len(user_projects),
        "page": 1,
        "total_pages": 1
    }

@app.get("/api/library/projects/{project_id}")
async def get_project_details(project_id: str, current_user: dict = Depends(get_current_user)):
    if project_id not in data_store["projects"]:
        raise HTTPException(status_code=404, detail="Project not found")

    project = data_store["projects"][project_id]

    # Verify project belongs to current user
    if project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "project": project,
        "success": True
    }

@app.put("/api/library/projects/{project_id}")
async def update_project(project_id: str, settings: CustomizationSettings, current_user: dict = Depends(get_current_user)):
    if project_id not in data_store["projects"]:
        raise HTTPException(status_code=404, detail="Project not found")

    project = data_store["projects"][project_id]

    # Verify project belongs to current user
    if project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update project settings
    project["customization"] = settings.dict()
    project["updated_at"] = time.time()

    data_store["projects"][project_id] = project
    save_data(data_store)

    return {
        "success": True,
        "message": "Project updated successfully",
        "project": project
    }

@app.delete("/api/library/projects/{project_id}")
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    if project_id not in data_store["projects"]:
        raise HTTPException(status_code=404, detail="Project not found")

    project = data_store["projects"][project_id]

    # Verify project belongs to current user
    if project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    del data_store["projects"][project_id]
    save_data(data_store)

    return {
        "success": True,
        "message": "Project deleted successfully"
    }

@app.get("/api/library/llm-projects")
async def get_llm_output_projects():
    """Scan and return projects from LLM_output folder"""
    try:
        # Look for LLM_output folder in parent directory (project-relative path)
        llm_output_path = os.path.join("..", "LLM_output")

        if not os.path.exists(llm_output_path):
            return {
                "projects": [],
                "count": 0,
                "message": "LLM_output folder not found"
            }

        projects = []

        # Scan each timestamped folder
        for folder_name in os.listdir(llm_output_path):
            folder_path = os.path.join(llm_output_path, folder_name)
            if os.path.isdir(folder_path):
                project_files = []

                # Find all PDF, JSON, and TXT files in this folder
                for ext in ["*.pdf", "*.json", "*.txt"]:
                    files = glob.glob(os.path.join(folder_path, ext))
                    project_files.extend(files)

                if project_files:
                    # Extract project info from folder name and files
                    try:
                        # Parse timestamp from folder name if possible
                        timestamp_str = folder_name.replace("_", "-").replace(" ", ":")
                        created_time = datetime.strptime(timestamp_str, "%Y-%m-%d-%H-%M-%S").isoformat()
                    except:
                        created_time = datetime.now().isoformat()

                    project = {
                        "id": f"llm_{folder_name}",
                        "title": f"Generated Journal ({folder_name})",
                        "description": f"AI-generated journal from {folder_name}",
                        "status": "completed",
                        "created_at": created_time,
                        "updated_at": created_time,
                        "files": [
                            {
                                "name": os.path.basename(f),
                                "path": f,
                                "type": os.path.splitext(f)[1].lower(),
                                "size": os.path.getsize(f) if os.path.exists(f) else 0
                            }
                            for f in project_files
                        ],
                        "file_count": len(project_files),
                        "source": "llm_output",
                        "progress": 100,
                        "word_count": "N/A"
                    }
                    projects.append(project)

        # Sort by creation time (newest first)
        projects.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "projects": projects,
            "count": len(projects),
            "source": "LLM_output folder"
        }

    except Exception as e:
        logger.error(f"Error scanning LLM_output folder: {e}")
        return {
            "projects": [],
            "count": 0,
            "error": str(e)
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

        if job_id in data_store["ai_jobs"]:
            data_store["ai_jobs"][job_id]["progress"] = progress
            data_store["ai_jobs"][job_id]["current_stage"] = stage
            save_data(data_store)

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
    if job_id in data_store["ai_jobs"]:
        data_store["ai_jobs"][job_id]["status"] = "completed"

        # Deduct AI credit from user
        job = data_store["ai_jobs"][job_id]
        user_id = job["user_id"]
        if user_id in data_store["users"]:
            data_store["users"][user_id]["ai_credits"] -= 1
            save_data(data_store)

        # Create a mock project
        project_id = f"project_{uuid.uuid4().hex[:12]}"

        project = {
            "id": project_id,
            "user_id": user_id,
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

        data_store["projects"][project_id] = project
        save_data(data_store)

        # Send completion notification
        completion_data = {
            "type": "completed",
            "job_id": job_id,
            "project_id": project_id,
            "message": "Journal generation completed!",
            "timestamp": time.time()
        }
        await manager.send_progress(job_id, completion_data)

# ==============================
# JOURNAL CREATION ENDPOINTS
# ==============================

@app.post("/api/journals/create", response_model=dict)
async def create_journal(request: JournalCreationRequest, current_user: dict = Depends(get_current_user)):
    """Create a new journal using CrewAI agents"""
    try:
        # Find user_id by searching through users data store
        user_id = None
        for uid, user_data in data_store.get("users", {}).items():
            if user_data.get("email") == current_user.get("email"):
                user_id = uid
                break

        if not user_id:
            raise HTTPException(status_code=401, detail="User not found in data store")

        # Start journal creation process
        job_id = await journal_service.start_journal_creation(
            request.preferences.model_dump(),
            progress_callback=None  # We'll handle progress via WebSocket
        )

        # Store job with user association
        if "ai_jobs" not in data_store:
            data_store["ai_jobs"] = {}

        data_store["ai_jobs"][job_id] = {
            "user_id": user_id,
            "preferences": request.preferences.model_dump(),
            "status": "started",
            "created_at": datetime.now().isoformat()
        }
        save_data(data_store)

        return {
            "success": True,
            "jobId": job_id,
            "message": "Journal creation started successfully"
        }

    except Exception as e:
        logger.error(f"Error creating journal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/journals/status/{job_id}", response_model=JournalProgress)
async def get_journal_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """Get the status of a journal creation job"""
    try:
        # Check if job exists and belongs to user
        if job_id not in data_store.get("ai_jobs", {}):
            raise HTTPException(status_code=404, detail="Job not found")

        job_data = data_store["ai_jobs"][job_id]

        # Find user_id by searching through users data store (same as creation endpoint)
        user_id = None
        for uid, user_data in data_store.get("users", {}).items():
            if user_data.get("email") == current_user.get("email"):
                user_id = uid
                break

        if not user_id or job_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get status from journal service
        job_status = journal_service.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job status not found")

        return JournalProgress(**job_status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/journals/author-suggestions")
async def get_author_suggestions(theme: str = ""):
    """Get author style suggestions for a given theme"""
    try:
        suggestions = journal_service.get_author_suggestions(theme)
        return suggestions
    except Exception as e:
        logger.error(f"Error getting author suggestions: {e}")
        # Return fallback suggestions
        return {
            "authors": [
                {"name": "James Clear", "style": "direct actionable"},
                {"name": "Mark Manson", "style": "blunt irreverent"},
                {"name": "Brené Brown", "style": "empathetic research-driven"},
                {"name": "Robin Sharma", "style": "inspirational narrative"},
                {"name": "Mel Robbins", "style": "direct motivational"}
            ],
            "theme": theme
        }

@app.get("/api/journals/{job_id}/download")
async def download_journal(job_id: str, current_user: dict = Depends(get_current_user)):
    """Download a completed journal"""
    try:
        # Check if job exists and belongs to user
        if job_id not in data_store.get("ai_jobs", {}):
            raise HTTPException(status_code=404, detail="Job not found")

        job_data = data_store["ai_jobs"][job_id]
        if job_data["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get job result
        job_status = journal_service.get_job_status(job_id)
        if not job_status or job_status.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Journal not ready for download")

        result = job_status.get("result")
        if not result:
            raise HTTPException(status_code=404, detail="Journal file not found")

        # Check if file exists
        file_path = result.get("file_path") or result.get("pdf_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Journal file not found")

        # Return file
        filename = f"{job_data['preferences']['title']}.md"
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="text/markdown"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading journal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket for real-time progress updates
class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_progress(self, job_id: str, data: dict):
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_text(json.dumps(data))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                # Remove broken connection
                self.disconnect(job_id)

manager = WebSocketManager()

@app.websocket("/ws/journal/{job_id}")
async def websocket_journal_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time journal creation progress"""
    await manager.connect(websocket, job_id)
    try:
        # Send initial status
        job_status = journal_service.get_job_status(job_id)
        if job_status:
            await websocket.send_text(json.dumps(job_status))

        # Keep connection alive and send updates
        while True:
            # Check for updates and send them
            await asyncio.sleep(1)  # Check every second

            # This would normally be triggered by the journal service
            # For now, we'll just keep the connection alive
            job_status = journal_service.get_job_status(job_id)
            if job_status and job_status.get("status") in ["completed", "error"]:
                # Send final status and close
                await websocket.send_text(json.dumps(job_status))
                break

    except WebSocketDisconnect:
        manager.disconnect(job_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(job_id)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Journal Craft Crew Unified Backend Server")
    print("📍 Backend: http://localhost:8000")
    print("📍 Health Check: http://localhost:8000/health")
    print("📍 Frontend: http://localhost:5173")
    print("📋 Available Endpoints:")
    print("   - Authentication: /api/auth/register, /api/auth/login")
    print("   - AI Generation: /api/ai/themes, /api/ai/title-styles, /api/ai/generate-journal")
    print("   - Project Library: /api/library/projects (full CRUD)")
    print("   - WebSocket: /ws/job/{job_id} (real-time progress)")
    print("   - Data Persistence: File-based storage with security")
    print("🎯 Unified Backend Ready!")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )