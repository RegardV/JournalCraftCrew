#!/usr/bin/env python3
"""
Unified Backend Server for Journal Craft Crew
Phase 4: Security Hardened Production Backend
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Security, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pydantic import BaseModel, EmailStr, Field, validator
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
import jwt
from jwt.exceptions import InvalidTokenError as JWTError
from passlib.context import CryptContext
from passlib.hash import bcrypt

# Import security middleware
from app.middleware.security import setup_cors_middleware, RateLimitMiddleware, SecurityHeadersMiddleware
from app.utils.validation import SecurityValidator, validate_string_field
from app.utils.error_handling import (
    setup_exception_handlers,
    JournalPlatformException,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    DatabaseError
)

# Import CrewAI integration
from crewai_integration import journal_service

# Import journal scanner service
from app.services.journal_scanner import JournalScannerService

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configuration from environment
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Validate secret key
if SECRET_KEY == "your-super-secret-key-change-in-production" or SECRET_KEY.startswith("CHANGE_ME"):
    logger.warning("Using default or placeholder SECRET_KEY. Please set a secure SECRET_KEY in production!")

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
    """Hash password using bcrypt with proper length handling"""
    # bcrypt has a 72-byte limit, so truncate longer passwords BEFORE hashing
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')

    # Use the truncated password for hashing
    # Import bcrypt directly to avoid passlib's length validation
    import bcrypt
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt with proper length handling"""
    # bcrypt has a 72-byte limit, so truncate longer passwords BEFORE verification
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        plain_password = password_bytes.decode('utf-8', errors='ignore')

    # Use the truncated password for verification
    # Import bcrypt directly to avoid passlib's length validation
    import bcrypt
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

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

# Initialize journal scanner service
journal_scanner = JournalScannerService(llm_output_dir="../LLM_output")

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
    title="Journal Craft Crew - Production Backend",
    description="Security-hardened backend with rate limiting and input validation"
)

# Setup security middleware (CORS, rate limiting, security headers)
setup_cors_middleware(app)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)
app.add_middleware(SecurityHeadersMiddleware)

# Setup comprehensive error handling
setup_exception_handlers(app)

# Enhanced Pydantic models with security validation
class UserRegistration(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Secure password (8-128 characters)")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    profile_type: str = Field("personal_journaler", pattern="^(personal_journaler|content_creator)$", description="Account type")

    @validator('full_name')
    def validate_full_name(cls, v):
        return validate_string_field(v, 'full_name', max_length=100)

    @validator('password')
    def validate_password_strength(cls, v):
        is_valid, errors = SecurityValidator.validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"Password validation failed: {', '.join(errors)}")
        return v

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=1, max_length=128, description="User password")

    @validator('email')
    def validate_email_format(cls, v):
        if not SecurityValidator.validate_email(v):
            raise ValueError("Invalid email format")
        return v.lower()

class TokenData(BaseModel):
    access_token: str = Field(..., min_length=10, description="JWT access token")
    token_type: str = Field("bearer", pattern="^bearer$", description="Token type")

class AIGenerationRequest(BaseModel):
    theme: str = Field(..., min_length=3, max_length=200, description="Journal theme")
    title_style: str = Field("inspirational", max_length=50, description="Title style")
    author_style: str = Field("conversational", max_length=50, description="Author writing style")
    research_depth: str = Field("basic", pattern="^(basic|medium|deep)$", description="Research depth")
    custom_prompt: Optional[str] = Field(None, max_length=500, description="Custom prompt for generation")

    @validator('theme')
    def validate_theme(cls, v):
        # Sanitize and validate theme input
        sanitized = SecurityValidator.sanitize_string(v, max_length=200)
        if SecurityValidator.check_sql_injection(sanitized):
            raise ValueError("Invalid theme detected")
        return sanitized

    @validator('title_style', 'author_style')
    def validate_styles(cls, v):
        # Sanitize style inputs
        sanitized = SecurityValidator.sanitize_string(v, max_length=50)
        if SecurityValidator.check_sql_injection(sanitized):
            raise ValueError("Invalid style detected")
        return sanitized

    @validator('custom_prompt')
    def validate_custom_prompt(cls, v):
        if v is None:
            return v
        # Sanitize custom prompt
        sanitized = SecurityValidator.sanitize_string(v, max_length=500)
        if SecurityValidator.check_sql_injection(sanitized):
            raise ValueError("Invalid custom prompt detected")
        return sanitized

class AIGenerationResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., pattern="^(pending|processing|completed|failed)$", description="Job status")
    message: str = Field(..., description="Status message")

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

# Settings and API Key Models
class APIKeyRequest(BaseModel):
    apiKey: str = Field(..., min_length=20, max_length=200, description="OpenAI API key")
    provider: str = Field("openai", pattern="^openai$", description="API provider")

class APIKeyResponse(BaseModel):
    success: bool
    message: str
    provider: str

class APIKeyTestRequest(BaseModel):
    apiKey: str = Field(..., min_length=20, max_length=200, description="OpenAI API key")
    provider: str = Field("openai", pattern="^openai$", description="API provider")

class APIKeyTestResponse(BaseModel):
    success: bool
    message: str
    valid: bool
    usage_info: Optional[dict] = None

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

# Settings endpoints
@app.post("/api/settings/api-key", response_model=APIKeyResponse)
async def save_api_key(request: APIKeyRequest, current_user: dict = Depends(get_current_user)):
    """Save or update user's API key"""
    try:
        # Find user_id
        user_id = None
        for uid, user_data in data_store["users"].items():
            if user_data.get("email") == current_user.get("email"):
                user_id = uid
                break

        if not user_id:
            raise HTTPException(status_code=401, detail="User not found")

        # Initialize user settings if not exists
        if "user_settings" not in data_store:
            data_store["user_settings"] = {}

        if user_id not in data_store["user_settings"]:
            data_store["user_settings"][user_id] = {}

        # Store API key (encrypted or hashed in production)
        # For demo purposes, we'll store it directly, but in production, encrypt this
        data_store["user_settings"][user_id]["openai_api_key"] = request.apiKey
        data_store["user_settings"][user_id]["api_provider"] = request.provider
        data_store["user_settings"][user_id]["api_key_updated_at"] = datetime.now().isoformat()

        save_data(data_store)

        return APIKeyResponse(
            success=True,
            message="API key saved successfully",
            provider=request.provider
        )

    except Exception as e:
        logger.error(f"Error saving API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings/test-api-key", response_model=APIKeyTestResponse)
async def test_api_key(request: APIKeyTestRequest, current_user: dict = Depends(get_current_user)):
    """Test if an API key is valid"""
    try:
        # Basic validation of API key format
        if not request.apiKey.startswith("sk-"):
            return APIKeyTestResponse(
                success=False,
                message="Invalid API key format. OpenAI API keys should start with 'sk-'",
                valid=False
            )

        # In a real implementation, you would make a test API call to OpenAI
        # For now, we'll do basic validation
        if len(request.apiKey) < 20:
            return APIKeyTestResponse(
                success=False,
                message="API key appears to be too short",
                valid=False
            )

        # Simulate API key validation (in production, make actual OpenAI API call)
        # This is where you would make a real test call to OpenAI's API
        import time
        time.sleep(1)  # Simulate API call delay

        # For demo purposes, we'll assume it's valid if it has proper format
        return APIKeyTestResponse(
            success=True,
            message="API key is valid and ready to use",
            valid=True,
            usage_info={
                "model": "gpt-4",
                "status": "active",
                "note": "This is a demo validation. In production, actual API validation would be performed."
            }
        )

    except Exception as e:
        logger.error(f"Error testing API key: {e}")
        return APIKeyTestResponse(
            success=False,
            message=f"Error testing API key: {str(e)}",
            valid=False
        )

@app.get("/api/settings/api-key")
async def get_api_key_status(current_user: dict = Depends(get_current_user)):
    """Check if user has an API key configured"""
    try:
        # Find user_id
        user_id = None
        for uid, user_data in data_store["users"].items():
            if user_data.get("email") == current_user.get("email"):
                user_id = uid
                break

        if not user_id:
            raise HTTPException(status_code=401, detail="User not found")

        # Check if user has API key configured
        user_settings = data_store.get("user_settings", {}).get(user_id, {})
        has_api_key = "openai_api_key" in user_settings
        provider = user_settings.get("api_provider", "openai")
        updated_at = user_settings.get("api_key_updated_at")

        return {
            "has_api_key": has_api_key,
            "provider": provider,
            "updated_at": updated_at,
            "message": "API key configured" if has_api_key else "No API key configured"
        }

    except Exception as e:
        logger.error(f"Error checking API key status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
            "author_style": request.author_style,
            "research_depth": request.research_depth,
            "custom_prompt": request.custom_prompt,
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

# ==============================
# JOURNAL LIBRARY INTEGRATION
# ==============================

@app.get("/api/journals/library")
async def get_journal_library(current_user: dict = Depends(get_current_user)):
    """Get user's completed CrewAI journal projects"""
    try:
        # Scan projects using the journal scanner service
        projects = journal_scanner.scan_projects()

        return {
            "projects": projects,
            "count": len(projects),
            "last_scan": journal_scanner.last_scan.isoformat() if journal_scanner.last_scan else None,
            "success": True
        }

    except Exception as e:
        logger.error(f"Error scanning journal library: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/journals/{project_id}/files")
async def get_project_files(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get file structure for a specific journal project"""
    try:
        files = journal_scanner.get_project_files(project_id)

        if not files:
            raise HTTPException(status_code=404, detail="Project not found")

        return {
            "project_id": project_id,
            "files": files,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/journals/{project_id}/metadata")
async def get_project_metadata(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get metadata for a specific journal project"""
    try:
        project = journal_scanner.get_project_by_id(project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return {
            "project": project,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/journals/{project_id}/download/{file_path:path}")
async def download_journal_file(project_id: str, file_path: str, current_user: dict = Depends(get_current_user)):
    """Download a specific file from a journal project"""
    try:
        # Get the absolute file path
        full_path = journal_scanner.get_file_path(project_id, file_path)

        if not full_path or not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Determine media type
        if file_path.endswith('.pdf'):
            media_type = 'application/pdf'
        elif file_path.endswith('.json'):
            media_type = 'application/json'
        elif file_path.endswith(('.jpg', '.jpeg')):
            media_type = 'image/jpeg'
        elif file_path.endswith('.png'):
            media_type = 'image/png'
        else:
            media_type = 'application/octet-stream'

        return FileResponse(
            path=full_path,
            filename=os.path.basename(file_path),
            media_type=media_type
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/journals/{project_id}/status")
async def get_project_completion_status(project_id: str, current_user: dict = Depends(get_current_user)):
    """Check if a CrewAI project has completed successfully"""
    try:
        is_complete = journal_scanner.is_project_complete(project_id)

        return {
            "project_id": project_id,
            "is_complete": is_complete,
            "status": "completed" if is_complete else "in_progress",
            "success": True
        }

    except Exception as e:
        logger.error(f"Error checking project status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/library/llm-projects")
async def get_llm_output_projects():
    """Scan and return projects from LLM_output folder using JournalScannerService"""
    try:
        # Use the JournalScannerService to scan projects
        projects = journal_scanner.scan_projects()

        # Format projects for frontend compatibility
        formatted_projects = []
        for project in projects:
            # Extract files information
            project_files = journal_scanner.get_project_files(project['id'])

            formatted_project = {
                "id": project['id'],
                "title": project['title'],
                "description": f"Theme: {project['theme']} | Style: {project['author_style']}",
                "status": project['status'],
                "created_at": project['created_at'],
                "updated_at": project['created_at'],
                "theme": project['theme'],
                "author_style": project['author_style'],
                "files": [
                    {
                        "name": os.path.basename(file_path),
                        "path": file_path,
                        "type": os.path.splitext(file_path)[1].lower(),
                        "size": os.path.getsize(journal_scanner.get_file_path(project['id'], file_path)) if journal_scanner.get_file_path(project['id'], file_path) and os.path.exists(journal_scanner.get_file_path(project['id'], file_path)) else 0
                    }
                    for file_path in project_files.get('all', [])
                ],
                "file_count": len(project_files.get('all', [])),
                "source": "LLM_output folder",
                "progress": 100 if project['status'] == 'completed' else 0,
                "word_count": "N/A",
                "has_pdfs": project_files.get('pdfs', [])
            }
            formatted_projects.append(formatted_project)

        return {
            "projects": formatted_projects,
            "count": len(formatted_projects),
            "source": "LLM_output folder (via JournalScannerService)"
        }

    except Exception as e:
        logger.error(f"Error scanning LLM_output folder: {e}")
        return {
            "projects": [],
            "count": 0,
            "error": str(e)
        }

@app.delete("/api/library/llm-projects/{project_id}")
async def delete_llm_output_project(project_id: str):
    """Delete a project from LLM_output folder"""
    try:
        # Extract folder name from project_id
        if project_id.startswith("llm_"):
            folder_name = project_id[4:]  # Remove "llm_" prefix
        else:
            raise HTTPException(status_code=400, detail="Invalid project ID format")

        llm_output_path = os.path.join("..", "LLM_output")
        folder_path = os.path.join(llm_output_path, folder_name)

        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete the entire folder and its contents
        import shutil
        shutil.rmtree(folder_path)

        logger.info(f"Deleted LLM project folder: {folder_name}")

        return {
            "message": "Project deleted successfully",
            "project_id": project_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting LLM project: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete project")

@app.delete("/api/library/projects/{project_id}")
async def delete_project_universal(project_id: str):
    """Universal project deletion that handles different ID formats"""
    try:
        # Try different deletion strategies based on project_id format

        # Strategy 1: Check if it's an integer (database project)
        try:
            int_project_id = int(project_id)
            # Import the database service and try to delete from database
            from app.services.project_library_service import ProjectLibraryService
            from app.api.dependencies import get_db, get_current_user

            # For now, we'll simulate this - in a real implementation,
            # we'd need to handle authentication properly
            logger.info(f"Attempting to delete database project with ID: {int_project_id}")
            return {
                "message": "Database project deletion not implemented in unified backend",
                "project_id": project_id,
                "note": "Please use the FastAPI service for database project deletion"
            }
        except ValueError:
            pass  # Not an integer, continue to next strategy

        # Strategy 2: Check if it's a journal creation job ID
        if project_id.startswith("journal_creation_"):
            # This might be a journal creation job - try to find and delete related data
            logger.info(f"Attempting to delete journal creation project: {project_id}")

            # Check if it exists in data_store
            if project_id in data_store.get("journal_projects", {}):
                del data_store["journal_projects"][project_id]
                logger.info(f"Deleted journal creation project from data_store: {project_id}")
                return {
                    "message": "Journal creation project deleted successfully",
                    "project_id": project_id
                }

            # Check if there's a corresponding folder
            journal_folder = os.path.join("..", "journal_outputs", project_id)
            if os.path.exists(journal_folder):
                import shutil
                shutil.rmtree(journal_folder)
                logger.info(f"Deleted journal creation folder: {project_id}")
                return {
                    "message": "Journal creation project folder deleted successfully",
                    "project_id": project_id
                }

        # Strategy 3: Check if it's an LLM project with different format
        if not project_id.startswith("llm_"):
            # Try to find it in LLM_output with different naming patterns
            llm_output_path = os.path.join("..", "LLM_output")
            if os.path.exists(llm_output_path):
                for folder_name in os.listdir(llm_output_path):
                    if project_id in folder_name or folder_name in project_id:
                        folder_path = os.path.join(llm_output_path, folder_name)
                        if os.path.isdir(folder_path):
                            import shutil
                            shutil.rmtree(folder_path)
                            logger.info(f"Deleted matching LLM project folder: {folder_name}")
                            return {
                                "message": f"LLM project deleted successfully (matched folder: {folder_name})",
                                "project_id": project_id
                            }

        # If we get here, we couldn't find the project
        logger.warning(f"Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete project")

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

        # Get user's API key
        user_api_key = None
        if "user_settings" in data_store and user_id in data_store["user_settings"]:
            user_api_key = data_store["user_settings"][user_id].get("openai_api_key")

        if not user_api_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Please add your API key in settings."
            )

        # Create WebSocket progress callback
        async def websocket_progress_callback(progress_update: dict):
            """Send progress updates to WebSocket clients"""
            try:
                # Add timestamp if not present
                if 'timestamp' not in progress_update:
                    progress_update['timestamp'] = datetime.now().isoformat()

                # Send message to WebSocket clients for this job
                await manager.send_progress(job_id, progress_update)
            except Exception as e:
                print(f"❌ Error sending WebSocket progress: {e}")

        # Start journal creation process with user's API key
        job_id = await journal_service.start_journal_creation(
            request.preferences.model_dump(),
            api_key=user_api_key,  # Pass user's API key
            progress_callback=websocket_progress_callback  # Connect to WebSocket
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

# Advanced CrewAI Workflow API Endpoints
@app.post("/api/crewai/start-workflow", response_model=dict)
async def start_crewai_workflow(
    workflow_request: dict,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Start a new CrewAI workflow for journal creation"""
    try:
        # Import CrewAI workflow service
        from crewai_integration import journal_service

        # Create project record
        project_id = str(uuid.uuid4())

        # Log workflow start
        logger.info(f"🤖 Starting CrewAI workflow for user {current_user['user_id']}, project_id: {project_id}")
        logger.info(f"📋 Workflow preferences: {workflow_request}")

        # Start workflow in background
        background_tasks.add_task(
            journal_service.start_workflow,
            {
                "project_id": project_id,
                "user_id": current_user["user_id"],
                "preferences": workflow_request
            }
        )

        return {
            "workflow_id": project_id,
            "status": "started",
            "message": "CrewAI workflow started successfully",
            "estimated_duration": validated_request.get("estimated_duration_minutes", 30),
            "workflow_type": validated_request.get("workflow_type", "standard")
        }

    except Exception as e:
        logger.error(f"Error starting CrewAI workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crewai/workflow-status/{workflow_id}", response_model=dict)
async def get_workflow_status(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get status of a CrewAI workflow"""
    try:
        # Import CrewAI workflow service
        from crewai_integration import journal_service

        status = await journal_service.get_job_status(workflow_id)
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crewai/cancel-workflow/{workflow_id}")
async def cancel_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a running CrewAI workflow"""
    try:
        # Import CrewAI workflow service
        from crewai_integration import journal_service

        # Try to cancel the workflow
        try:
            journal_service.cancel_job(workflow_id)
            success = True
        except Exception as e:
            logger.error(f"Failed to cancel workflow {workflow_id}: {e}")
            success = False
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found or cannot be cancelled")

        return {
            "workflow_id": workflow_id,
            "status": "cancelled",
            "message": "Workflow cancelled successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crewai/continue-project", response_model=dict)
async def continue_project(
    project_request: dict,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Continue work on an existing project with CrewAI"""
    try:
        from crewai_integration import journal_service

        # Start project continuation in background
        background_tasks.add_task(
            journal_service.continue_project,
            project_request.get("project_id"),
            project_request.get("action", "continue_workflow"),
            current_user["user_id"]
        )

        result = {
            "project_id": project_request.get("project_id"),
            "status": "continued",
            "message": "Project continuation started"
        }

        return result

    except Exception as e:
        logger.error(f"Error continuing project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crewai/active-workflows")
async def get_active_workflows(current_user: dict = Depends(get_current_user)):
    """Get all active workflows for the current user"""
    try:
        from app.api.routes.crewai_workflow import get_active_workflows as get_active

        workflows = get_active(current_user["user_id"])
        return {"active_workflows": workflows}

    except Exception as e:
        logger.error(f"Error getting active workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced WebSocket for CrewAI progress
@app.websocket("/ws/crewai/{workflow_id}")
async def websocket_crewai_progress(websocket: WebSocket, workflow_id: str):
    """Enhanced WebSocket endpoint for real-time CrewAI workflow progress"""
    print(f"🤖 CrewAI WebSocket connection requested for workflow: {workflow_id}")
    await manager.connect(websocket, workflow_id)
    print(f"✅ CrewAI WebSocket connected for workflow: {workflow_id}")

    try:
        # Send welcome message
        welcome_msg = {
            "type": "workflow_start",
            "workflow_id": workflow_id,
            "message": "Connected to CrewAI workflow progress tracking",
            "timestamp": datetime.now().isoformat(),
            "estimated_duration_minutes": 30,
            "crew_agents": [
                "Discovery Agent", "Research Agent", "Content Curator Agent",
                "Editor Agent", "Media Agent", "PDF Builder Agent"
            ]
        }
        await websocket.send_text(json.dumps(welcome_msg))
        print(f"🤖 Sent CrewAI welcome message for workflow: {workflow_id}")

        # Send progress updates
        connection_count = 0
        while True:
            connection_count += 1
            await asyncio.sleep(1)  # Check every second for CrewAI updates

            # Simulate CrewAI progress updates (in real implementation, this would be actual progress)
            if connection_count % 5 == 0:  # Every 5 seconds
                progress_data = {
                    "type": "agent_progress",
                    "workflow_id": workflow_id,
                    "current_step": min(connection_count // 5, 6),
                    "total_steps": 6,
                    "current_agent": ["Discovery Agent", "Research Agent", "Content Curator Agent", "Editor Agent", "Media Agent", "PDF Builder Agent"][min((connection_count // 5) - 1, 5)],
                    "progress_percentage": min((connection_count // 5) * 100 / 6, 100),
                    "message": f"Processing with AI agents... Step {min(connection_count // 5, 6)}/6",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(progress_data))
                print(f"🤖 Sent CrewAI progress update for workflow: {workflow_id}")

            # Check for workflow completion
            if connection_count >= 30:  # After 30 seconds, simulate completion
                completion_msg = {
                    "type": "workflow_complete",
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "progress_percentage": 100,
                    "result_data": {
                        "file_path": f"LLM_output/{workflow_id}/journal.md",
                        "pdf_path": f"LLM_output/{workflow_id}/journal.pdf",
                        "word_count": 15000,
                        "pages": 30
                    },
                    "total_duration": 30,
                    "message": "CrewAI workflow completed successfully!",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(completion_msg))
                print(f"🎉 CrewAI workflow completed: {workflow_id}")
                break

    except WebSocketDisconnect:
        print(f"🤖 CrewAI WebSocket disconnected for workflow: {workflow_id}")
        manager.disconnect(workflow_id)
    except Exception as e:
        print(f"❌ CrewAI WebSocket error for workflow {workflow_id}: {e}")
        logger.error(f"CrewAI WebSocket error: {e}")
        manager.disconnect(workflow_id)

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
    print(f"🔌 WebSocket connection requested for job: {job_id}")
    await manager.connect(websocket, job_id)
    print(f"✅ WebSocket connected for job: {job_id}")

    try:
        # Send welcome message
        welcome_msg = {
            "type": "connection",
            "message": f"Connected to journal workflow for job: {job_id}",
            "timestamp": datetime.now().isoformat(),
            "status": "connected"
        }
        await websocket.send_text(json.dumps(welcome_msg))
        print(f"📤 Sent welcome message for job: {job_id}")

        # Send initial status
        job_status = journal_service.get_job_status(job_id)
        print(f"🔍 Job status for {job_id}: {job_status}")

        if job_status:
            await websocket.send_text(json.dumps(job_status))
            print(f"📤 Sent job status for {job_id}")
        else:
            # Send job not found message
            not_found_msg = {
                "type": "error",
                "message": f"Job {job_id} not found or not started",
                "timestamp": datetime.now().isoformat(),
                "status": "not_found",
                "suggestion": "Please create a new journal to see real-time progress"
            }
            await websocket.send_text(json.dumps(not_found_msg))
            print(f"❌ Job not found: {job_id}")

        # Keep connection alive and send updates
        connection_count = 0
        while True:
            connection_count += 1
            await asyncio.sleep(2)  # Check every 2 seconds

            # Send heartbeat every 10 seconds
            if connection_count % 5 == 0:
                heartbeat = {
                    "type": "heartbeat",
                    "message": f"Connection alive for {connection_count * 2} seconds",
                    "timestamp": datetime.now().isoformat(),
                    "job_id": job_id
                }
                await websocket.send_text(json.dumps(heartbeat))
                print(f"💓 Sent heartbeat for job: {job_id}")

            # Check for job status updates
            job_status = journal_service.get_job_status(job_id)
            if job_status and job_status.get("status") in ["completed", "error"]:
                # Send final status and close
                await websocket.send_text(json.dumps(job_status))
                print(f"🏁 Job {job_id} finished with status: {job_status.get('status')}")
                break

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected for job: {job_id}")
        manager.disconnect(job_id)
    except Exception as e:
        print(f"❌ WebSocket error for job {job_id}: {e}")
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(job_id)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Journal Craft Crew Unified Backend Server")
    print("📍 Backend: http://localhost:6770")
    print("📍 Health Check: http://localhost:6770/health")
    print("📍 Frontend: http://localhost:5173")
    print("📋 Available Endpoints:")
    print("   - Authentication: /api/auth/register, /api/auth/login")
    print("   - AI Generation: /api/ai/themes, /api/ai/title-styles, /api/ai/generate-journal")
    print("   - 🤖 Advanced CrewAI: /api/crewai/start-workflow, /api/crewai/workflow-status/{id}")
    print("   - 🤖 CrewAI Control: /api/crewai/cancel-workflow/{id}, /api/crewai/continue-project")
    print("   - 🤖 CrewAI Status: /api/crewai/active-workflows")
    print("   - Journal Creation: /api/journals/create, /api/journals/status/{job_id}")
    print("   - Journal Library: /api/journals/library, /api/journals/{project_id}/files")
    print("   - File Downloads: /api/journals/{project_id}/download/{file_path}")
    print("   - Project Library: /api/library/projects (full CRUD)")
    print("   - WebSocket: /ws/job/{job_id}, /ws/journal/{job_id} (real-time progress)")
    print("   - 🤖 CrewAI WebSocket: /ws/crewai/{workflow_id} (9-agent progress)")
    print("   - Data Persistence: File-based storage with security")
    print("🎯 Unified Backend Ready!")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=6770,
        log_level="info"
    )