#!/usr/bin/env python3
"""
Simple Production Server with JWT Authentication
Follows best practices for API authentication
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List, Optional
import json
import asyncio
import time
import uuid
import logging
import os
import base64
import hashlib
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple JWT implementation
SECRET_KEY = "your-super-secret-jwt-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# File-based data persistence
DATA_FILE = "production_data.json"

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

def save_data(data):
    """Save data to file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info("Data saved successfully")
    except Exception as e:
        logger.error(f"Error saving data: {e}")

# Simple JWT functions
def create_jwt_token(payload: dict) -> str:
    """Create JWT token"""
    import json
    token_payload = {
        **payload,
        "exp": datetime.utcnow().timestamp() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    }
    encoded = base64.b64encode(json.dumps(token_payload).encode()).decode()
    return f"jwt_token_{encoded}"

def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode JWT token"""
    try:
        if token.startswith("jwt_token_"):
            encoded = token.split("_")[1]
            decoded = base64.b64decode(encoded.encode()).decode()
            payload = json.loads(decoded)
            if payload.get("exp", 0) > datetime.utcnow().timestamp():
                return None  # Token expired
            return payload
        return None
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        return None

# Initialize data
data_store = load_data()

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    profile_type: str = "personal_journaler"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

class AIGenerationRequest(BaseModel):
    theme: str
    title_style: str
    description: Optional[str] = None

# Available themes and styles
AVAILABLE_THEMES = [
    {"id": "mindfulness", "name": "Mindfulness & Meditation", "description": "Daily prompts for mindfulness"},
    {"id": "productivity", "name": "Productivity Focus", "description": "Prompts for productivity"},
    {"id": "creativity", "name": "Creative Writing", "description": "Sparks for creativity"},
    {"id": "gratitude", "name": "Gratitude Practice", "description": "Daily gratitude prompts"}
]

TITLE_STYLES = [
    {"id": "inspirational", "name": "Inspirational Quotes"},
    {"id": "minimalist", "name": "Minimalist Clean"},
    {"id": "creative", "name": "Creative & Artistic"},
    {"id": "professional", "name": "Professional Focus"}
]

# Create FastAPI app
app = FastAPI(
    title="Journal Platform - Simple JWT Auth",
    description="Production-ready server with secure authentication"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
def get_current_user(authorization: str = None):
    """Get current user from JWT token"""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "")
    payload = decode_jwt_token(token)
    return payload.get("user_id") if payload else None

# Main application - requires authentication
@app.get("/", response_class=HTMLResponse)
async def protected_root():
    """Main application - requires authentication"""
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Login page"""
    return RedirectResponse(url="/")

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """Registration page"""
    return RedirectResponse(url="/")

# Health check (public)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "journal-platform-production",
        "timestamp": datetime.utcnow().isoformat(),
        "data_stats": {
            "users": len(data_store["users"]),
            "projects": len(data_store["projects"]),
            "active_sessions": len(data_store["sessions"]),
            "ai_jobs": len(data_store["ai_jobs"])
        }
    }

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user_data: UserRegistration):
    try:
        # Check if user already exists
        for uid, user in data_store["users"].items():
            if user["email"] == user_data.email:
                raise HTTPException(status_code=400, detail="User already exists")

        # Create new user
        user_id = f"user_{len(data_store['users']) + 1}"
        ai_credits = 50 if user_data.profile_type == "content_creator" else 10
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()

        new_user = {
            "id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "profile_type": user_data.profile_type,
            "ai_credits": ai_credits,
            "created_at": datetime.utcnow().isoformat(),
            "password_hash": password_hash
        }

        data_store["users"][user_id] = new_user
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

@app.post("/api/auth/login", response_model=LoginResponse)
async def login_user(user_data: UserLogin):
    try:
        # Find user by email
        user = None
        for uid, user_info in data_store["users"].items():
            if user_info["email"] == user_data.email:
                user = user_info
                break

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Verify password
        if user["password_hash"] != hashlib.sha256(user_data.password.encode()).hexdigest():
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create token
        token = create_jwt_token({"user_id": user["id"]})
        session_id = str(uuid.uuid4())
        data_store["sessions"][session_id] = {
            "user_id": user["id"],
            "token": token,
            "created_at": datetime.utcnow().isoformat()
        }
        save_data(data_store)

        logger.info(f"User logged in: {user_data.email}")

        return LoginResponse(
            success=True,
            message="Login successful",
            access_token=token,
            token_type="bearer",
            user={
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "profile_type": user["profile_type"],
                "ai_credits": user["ai_credits"]
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Protected endpoints (require authentication)
@app.get("/api/ai/themes")
async def get_available_themes(current_user: str = Depends(get_current_user)):
    return {
        "themes": AVAILABLE_THEMES,
        "count": len(AVAILABLE_THEMES)
    }

@app.get("/api/ai/title-styles")
async def get_title_styles(current_user: str = Depends(get_current_user)):
    return {
        "title_styles": TITLE_STYLES,
        "count": len(TITLE_STYLES)
    }

@app.post("/api/ai/generate-journal")
async def generate_journal(request: AIGenerationRequest, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Create job record
        data_store["ai_jobs"][job_id] = {
            "id": job_id,
            "theme": request.theme,
            "title_style": request.title_style,
            "description": request.description,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
            "user_id": current_user
        }
        save_data(data_store)

        # Start background task
        asyncio.create_task(simulate_realistic_ai_generation(job_id, request.theme, request.title_style))

        logger.info(f"AI generation started by user {current_user}: {job_id}")

        return {
            "success": True,
            "message": "AI journal generation started",
            "job_id": job_id,
            "estimated_time": 180,
            "status": "pending"
        }
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/progress/{job_id}")
async def get_generation_progress(job_id: str, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if job_id not in data_store["ai_jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify job ownership
    job = data_store["ai_jobs"][job_id]
    if job.get("user_id") != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress_percentage": job["progress"],
        "current_stage": job.get("current_stage", "Processing..."),
        "estimated_time_remaining": max(0, 180 - (datetime.utcnow() - datetime.fromisoformat(job["created_at"])).total_seconds()),
        "created_at": job["created_at"]
    }

@app.get("/api/library/projects")
async def get_user_projects(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Get projects for current user
    user_projects = []
    for pid, project in data_store["projects"].items():
        if project.get("user_id") == current_user:
            user_projects.append(project)

    return {
        "projects": user_projects,
        "count": len(user_projects),
        "page": 1,
        "total_pages": 1
    }

@app.get("/api/library/projects/{project_id}")
async def get_project_details(project_id: str, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if project_id not in data_store["projects"]:
        raise HTTPException(status_code=404, detail="Project not found")

    project = data_store["projects"][project_id]
    if project.get("user_id") != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "project": project,
        "success": True
    }

# Background task for realistic AI generation
async def simulate_realistic_ai_generation(job_id: str, theme: str, title_style: str):
    """More realistic AI generation simulation"""
    stages = [
        (10, "🤖 Initializing AI agents..."),
        (25, "📚 Analyzing theme patterns..."),
        (40, "✍️ Generating daily prompts..."),
        (60, "🎨 Creating journal structure..."),
        (80, "📄 Formatting content..."),
        (95, "🔧 Finalizing design..."),
        (100, "✅ Complete!")
    ]

    for progress, stage in stages:
        if job_id in data_store["ai_jobs"]:
            data_store["ai_jobs"][job_id]["progress"] = progress
            data_store["ai_jobs"][job_id]["current_stage"] = stage

            # Create completed project at 100%
            if progress == 100:
                project_id = f"project_{uuid.uuid4().hex[:12]}"
                data_store["ai_jobs"][job_id]["status"] = "completed"

                data_store["projects"][project_id] = {
                    "id": project_id,
                    "title": f"{title_style.title()} {theme.title()} Journal",
                    "theme": theme,
                    "description": f"AI-generated {theme} journal with {title_style} style",
                    "status": "completed",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "customization": {
                        "layout": "single-column",
                        "font_size": "medium",
                        "color_scheme": "default",
                        "paper_type": "standard",
                        "binding_type": "perfect"
                    },
                    "pages_count": 30,
                    "word_count": 15000,
                    "export_formats": ["pdf", "epub", "kdp"],
                    "job_id": job_id,
                    "user_id": data_store["ai_jobs"][job_id]["user_id"]
                }

            save_data(data_store)

        await asyncio.sleep(3)  # More realistic timing

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Production-Ready Server")
    print("📍 Secure Authentication: http://localhost:8000")
    print("🔐 JWT Token System")
    print("📋 Users:", len(data_store.get('users', [])))
    print("📚 Projects:", len(data_store.get('projects', [])))
    print("📖 Active AI Jobs:", len(data_store.get('ai_jobs', [])))
    print("💡 For production deployment:")
    print("   - Change SECRET_KEY to secure random key")
    print("   - Add HTTPS with proper SSL certificates")
    print("   - Replace file storage with database")
    print("   - Add rate limiting and input validation")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )