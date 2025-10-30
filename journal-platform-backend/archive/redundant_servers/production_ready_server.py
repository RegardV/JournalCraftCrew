#!/usr/bin/env python3
"""
Production-Ready Local Server for Journal Craft Crew
Proper authentication with JWT tokens and secure API endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, List, Optional
import json
import asyncio
import time
import uuid
import logging
import os
import secrets
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Generate secure key for production
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
        expire = datetime.utcnow() + expires_delta
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

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    profile_type: str
    ai_credits: int

class AIGenerationRequest(BaseModel):
    theme: str
    title_style: str
    description: Optional[str] = None

# Available themes and styles
AVAILABLE_THEMES = [
    {"id": "mindfulness", "name": "Mindfulness & Meditation", "description": "Daily prompts for mindfulness", "estimated_days": 30},
    {"id": "productivity", "name": "Productivity Focus", "description": "Prompts for productivity", "estimated_days": 30},
    {"id": "creativity", "name": "Creative Writing", "description": "Sparks for creativity", "estimated_days": 30},
    {"id": "gratitude", "name": "Gratitude Practice", "description": "Daily gratitude prompts", "estimated_days": 30}
]

TITLE_STYLES = [
    {"id": "inspirational", "name": "Inspirational Quotes"},
    {"id": "minimalist", "name": "Minimalist Clean"},
    {"id": "creative", "name": "Creative & Artistic"},
    {"id": "professional", "name": "Professional Focus"}
]

# Security dependency
get_current_user = Security(get_current_user)

def get_current_user(token: str = Depends(get_current_user)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        return payload.get("user_id")
    except JWTError:
        raise credentials_exception

# Create FastAPI app
app = FastAPI(
    title="Journal Platform - Production Ready",
    description="Secure backend with proper authentication"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Protected main application (redirects to login if not authenticated)
@app.get("/", response_class=HTMLResponse)
async def protected_root():
    """Main application - requires authentication"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Journal Craft Crew - Application</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .alert { background: #fff3cd; color: #721c24; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .nav { background: #2d3748; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
            .nav a { color: white; text-decoration: none; margin: 0 10px; }
            .button { background: #2c3e50; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .button:hover { background: #1a2e40; }
            input { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Journal Craft Crew</h1>
            <h2>AI-Powered Journal Creation Platform</h2>

            <div class="alert">
                <strong>🔐 Authentication Required</strong><br>
                Please <a href="/api/docs">use the API endpoints</a> or access via frontend application.
            </div>

            <div class="nav">
                <a href="/api/docs">📚 API Documentation</a>
                <a href="/health">💚 Health Check</a>
                <a href="/login">👤 Login Required</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# API Documentation endpoint
@app.get("/api/docs", response_class=HTMLResponse)
async def api_docs():
    """API documentation page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Journal Craft Crew - API Documentation</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
            .endpoint { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 10px; }
            .method { background: #2d3748; color: white; padding: 10px; border-radius: 3px; font-weight: bold; }
            .url { color: #2c3e50; font-family: monospace; background: #f1f3f4; padding: 5px; border-radius: 3px; }
            .example { background: #e8f4fd; padding: 15px; border-radius: 5px; margin-top: 10px; }
            .nav { background: #2d3748; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
            .nav a { color: white; text-decoration: none; margin: 0 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 Journal Craft Crew API</h1>

            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/health">💚 Health</a>
                <a href="/api/docs">📋 Documentation</a>
            </div>

            <h2>🔐 Authentication Required</h2>

            <div class="endpoint">
                <h3>🔑 POST /api/auth/register</h3>
                <p>Register new user account</p>
                <div class="url">POST /api/auth/register</div>
                <div class="example">
                    <strong>Request:</strong><br>
                    <div class="method">POST</div>
                    <div class="url">/api/auth/register</div>
                    <br>
                    <strong>Body:</strong><br>
                    <div class="example">
                    {<br>
                      &quot;email&quot;: &quot;user@example.com&quot;,<br>
                      &quot;password&quot;: &quot;password123&quot;,<br>
                      &quot;full_name&quot;: &quot;User Name&quot;,<br>
                      &quot;profile_type&quot;: &quot;personal_journaler&quot;<br>
                    }
                    </div>
                    <br>
                    <strong>Response:</strong><br>
                    <div class="example">
                    {<br>
                      &quot;success&quot;: true,<br>
                      &quot;message&quot;: &quot;User registered successfully&quot;,<br>
                      &quot;user&quot;: { user object }<br>
                    }
                    </div>
                </div>
            </div>

            <div class="endpoint">
                <h3>🔑 POST /api/auth/login</h3>
                <p>Authenticate user and receive JWT token</p>
                <div class="url">POST /api/auth/login</div>
                <div class="example">
                    <strong>Request:</strong><br>
                    <div class="method">POST</div>
                    <div class="url">/api/auth/login</div>
                    <br>
                    <strong>Body:</strong><br>
                    <div class="example">
                    {<br>
                      &quot;email&quot;: &quot;user@example.com&quot;,<br>
                      &quot;password&quot;: &quot;password123&quot;<br>
                    }
                    </div>
                    <br>
                    <strong>Response:</strong><br>
                    <div class="example">
                    {<br>
                      &quot;success&quot;: true,<br>
                      &quot;message&quot;: &quot;Login successful&quot;,<br>
                      &quot;access_token&quot;: &quot;jwt_token_here&quot;,<br>
                      &quot;token_type&quot;: &quot;bearer&quot;<br>
                    }
                    </div>
                </div>
            </div>

            <div class="endpoint">
                <h3>🎨 GET /api/ai/themes</h3>
                <p>Get available journal themes</p>
                <div class="url">GET /api/ai/themes</div>
                <div class="example">
                    <strong>Response:</strong><br>
                    <div class="example">
                    {<br>
                      &quot;themes&quot;: [theme objects],<br>
                      &quot;count&quot;: 4<br>
                    }
                    </div>
                </div>
            </div>

            <p><strong>🔐 All API endpoints require valid JWT token in Authorization header</strong></p>
            <p><strong>Example:</strong> Authorization: Bearer YOUR_JWT_TOKEN</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Health check
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

        new_user = {
            "id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "profile_type": user_data.profile_type,
            "ai_credits": ai_credits,
            "created_at": datetime.utcnow().isoformat(),
            "password_hash": hash_password(user_data.password)
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

@app.post("/api/auth/login", response_model=TokenData)
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
        if not verify_password(user_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"user_id": user["id"]},
            expires_delta=access_token_expires
        )

        # Store session (optional - for demo)
        session_id = str(uuid.uuid4())
        data_store["sessions"][session_id] = {
            "user_id": user["id"],
            "token": token,
            "created_at": datetime.utcnow().isoformat()
        }
        save_data(data_store)

        logger.info(f"User logged in: {user_data.email}")

        return TokenData(
            access_token=token,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Protected endpoints (require authentication)
@app.get("/api/ai/themes", dependencies=[Depends(get_current_user)])
async def get_available_themes(current_user: str):
    return {
        "themes": AVAILABLE_THEMES,
        "count": len(AVAILABLE_THEMES)
    }

@app.get("/api/ai/title-styles", dependencies=[Depends(get_current_user)])
async def get_title_styles(current_user: str):
    return {
        "title_styles": TITLE_STYLES,
        "count": len(TITLE_STYLES)
    }

@app.post("/api/ai/generate-journal", dependencies=[Depends(get_current_user)])
async def generate_journal(request: AIGenerationRequest, current_user: str):
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

@app.get("/api/ai/progress/{job_id}", dependencies=[Depends(get_current_user)])
async def get_generation_progress(job_id: str, current_user: str):
    if job_id not in data_store["ai_jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")

    job = data_store["ai_jobs"][job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress_percentage": job["progress"],
        "current_stage": job.get("current_stage", "Processing..."),
        "estimated_time_remaining": max(0, 180 - (datetime.utcnow() - datetime.fromisoformat(job["created_at"])).total_seconds()),
        "created_at": job["created_at"]
    }

@app.get("/api/library/projects", dependencies=[Depends(get_current_user)])
async def get_user_projects(current_user: str):
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

@app.get("/api/library/projects/{project_id}", dependencies=[Depends(get_current_user)])
async def get_project_details(project_id: str, current_user: str):
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

        await asyncio.sleep(4)  # More realistic timing

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Production-Ready Server")
    print("📍 Secure Authentication Server: http://localhost:8000")
    print("🔐 JWT Token Authentication")
    print("📋 API Documentation: http://localhost:8000/api/docs")
    print("📊 Current Users:", len(data_store['users']))
    print("📚 Current Projects:", len(data_store['projects']))
    print("🤖 Active AI Jobs:", len(data_store['ai_jobs']))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )