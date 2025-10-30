#!/usr/bin/env python3
"""
Perfect Authentication Server
Clean authentication interface with settings-based API key management
No development section, no AI credits, seamless onboarding experience
"""

import asyncio
import json
import os
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr, validator
import bcrypt
import base64
from cryptography.fernet import Fernet

# OpenAI import
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_FILE = "perfect_auth_data.json"
ENCRYPTION_KEY_FILE = "perfect_encryption.key"

# Initialize encryption
def init_encryption():
    if os.path.exists(ENCRYPTION_KEY_FILE):
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
    return Fernet(key)

cipher_suite = init_encryption()

# Data Models
@dataclass
class User:
    id: str
    email: str
    username: str
    password_hash: str
    full_name: str
    created_at: float
    openai_api_key: Optional[str] = None  # Encrypted

class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 20:
            raise ValueError('Username must be between 3 and 20 characters')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class APIKeyUpdate(BaseModel):
    openai_api_key: str

    @validator('openai_api_key')
    def validate_api_key(cls, v):
        if not v.startswith("sk-"):
            raise ValueError('Invalid OpenAI API key format')
        return v

class AIGenerationRequest(BaseModel):
    theme: str
    title_style: str
    description: str

    @validator('theme')
    def validate_theme(cls, v):
        if not v.strip():
            raise ValueError('Theme is required')
        return v.strip()

    @validator('title_style')
    def validate_title_style(cls, v):
        valid_styles = ['classic', 'modern', 'creative', 'professional']
        if v not in valid_styles:
            raise ValueError(f'Invalid style. Must be one of: {valid_styles}')
        return v

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

# Rate limiting
rate_limit_store = {}

def check_rate_limit(identifier: str, max_requests: int = 5, window_seconds: int = 60) -> bool:
    now = time.time()
    if identifier not in rate_limit_store:
        rate_limit_store[identifier] = []

    # Remove old requests outside the window
    rate_limit_store[identifier] = [req_time for req_time in rate_limit_store[identifier]
                                   if now - req_time < window_seconds]

    if len(rate_limit_store[identifier]) >= max_requests:
        return False

    rate_limit_store[identifier].append(now)
    return True

# Data storage
data_store = {
    "users": {},
    "projects": {},
    "ai_jobs": {},
    "usage_stats": {}
}

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
        "ai_jobs": {},
        "usage_stats": {}
    }

def save_data(data):
    """Save data to file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info("Data saved successfully")
    except Exception as e:
        logger.error(f"Error saving data: {e}")

def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for storage"""
    return cipher_suite.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key for use"""
    return cipher_suite.decrypt(encrypted_key.encode()).decode()

# JWT Token management
def create_jwt_token(user_id: str, username: str) -> str:
    """Create a simple JWT-like token"""
    token_payload = {
        "user_id": user_id,
        "username": username,
        "exp": int(time.time()) + 24 * 3600,  # 24 hours
        "iat": int(time.time())
    }
    encoded = base64.b64encode(json.dumps(token_payload).encode()).decode()
    return f"jwt_token_{encoded}"

def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        if token.startswith("jwt_token_"):
            encoded = token.split("_")[1]
            decoded = base64.b64decode(encoded.encode()).decode()
            payload = json.loads(decoded)
            if payload.get("exp", 0) < time.time():
                return None
            return payload
    except Exception as e:
        logger.error(f"Token verification error: {e}")
    return None

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload.get("username")

# Input validation
import html
def sanitize_input(input_string: str) -> str:
    """Basic input sanitization"""
    import html
    return html.escape(input_string.strip())

async def validate_openai_api_key(api_key: str) -> bool:
    """Validate OpenAI API key by making a test request"""
    try:
        client = openai.OpenAI(api_key=api_key)
        # Test with a minimal request to check validity
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return True
    except Exception as e:
        logger.error(f"OpenAI API key validation failed: {e}")
        return False

# Initialize FastAPI app
app = FastAPI(
    title="Journal Craft Crew - Perfect Authentication",
    description="Create beautiful AI-powered journals with seamless authentication",
    version="4.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    endpoint = str(request.url.path)

    # Apply different rate limits for different endpoints
    if endpoint.startswith("/api/auth/"):
        if not check_rate_limit(f"auth:{client_ip}", 5, 300):  # 5 requests per 5 minutes
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many authentication attempts. Please try again later."}
            )
    elif endpoint.startswith("/api/ai/"):
        if not check_rate_limit(f"ai:{client_ip}", 3, 60):  # 3 requests per minute
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many AI generation requests. Please try again later."}
            )

    response = await call_next(request)
    return response

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.openai.com"
    return response

# Load initial data
data_store = load_data()

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user_data: UserRegistration, request: Request):
    try:
        # Rate limiting based on IP
        client_ip = request.client.host
        if not check_rate_limit(f"register:{client_ip}", 3, 15):
            raise HTTPException(
                status_code=429,
                detail="Too many registration attempts. Please try again later."
            )

        # Input validation and sanitization
        email = sanitize_input(user_data.email)
        username = sanitize_input(user_data.username)
        full_name = sanitize_input(user_data.full_name)

        # Check if user already exists
        if username in data_store["users"]:
            raise HTTPException(status_code=400, detail="Username already exists")

        if any(user["email"] == email for user in data_store["users"].values()):
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password
        password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create user
        user_id = f"user_{uuid.uuid4().hex[:12]}"

        user = User(
            id=user_id,
            email=email,
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            created_at=time.time()
            # No openai_api_key field - will be added in settings
        )

        data_store["users"][username] = asdict(user)
        save_data(data_store)

        logger.info(f"New user registered: {username}")

        # Create JWT token
        token = create_jwt_token(user_id, username)

        return {
            "message": "Account created successfully!",
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "full_name": full_name,
                "created_at": user.created_at,
                "has_openai_key": False
            },
            "access_token": token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin, request: Request):
    try:
        # Rate limiting based on IP
        client_ip = request.client.host
        if not check_rate_limit(f"login:{client_ip}", 5, 15):
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later."
            )

        username = sanitize_input(login_data.username)

        # Check if user exists
        if username not in data_store["users"]:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = data_store["users"][username]

        # Verify password
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), user["password_hash"].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create JWT token
        token = create_jwt_token(user["id"], username)

        logger.info(f"User logged in: {username}")

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "created_at": user["created_at"],
                "has_openai_key": bool(user.get("openai_api_key"))
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

# Settings endpoints for API key management
@app.get("/api/settings")
async def get_settings(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        stats = data_store["usage_stats"].get(current_user, {
            "total_cost": 0.0,
            "total_tokens": 0,
            "usage_history": []
        })

        return {
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "created_at": user["created_at"],
                "has_openai_key": bool(user.get("openai_api_key"))
            },
            "usage_stats": {
                "total_cost": stats["total_cost"],
                "total_tokens": stats["total_tokens"],
                "usage_history": stats["usage_history"][-10:]  # Last 10 uses
            }
        }
    except Exception as e:
        logger.error(f"Settings error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get settings")

@app.post("/api/settings/api-key")
async def update_api_key(api_key_data: APIKeyUpdate, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not api_key_data.openai_api_key.startswith("sk-"):
            raise HTTPException(status_code=400, detail="Invalid OpenAI API key format")

        # Validate the API key
        if not await validate_openai_api_key(api_key_data.openai_api_key):
            raise HTTPException(status_code=400, detail="Invalid OpenAI API key")

        # Encrypt and store the API key
        encrypted_key = encrypt_api_key(api_key_data.openai_api_key)
        data_store["users"][current_user]["openai_api_key"] = encrypted_key
        save_data(data_store)

        logger.info(f"OpenAI API key added for user: {current_user}")

        return {
            "message": "API key added successfully!",
            "has_openai_key": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API key")

@app.put("/api/settings/api-key")
async def update_existing_api_key(api_key_data: APIKeyUpdate, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not api_key_data.openai_api_key.startswith("sk-"):
            raise HTTPException(status_code=400, detail="Invalid OpenAI API key format")

        # Validate the new API key
        if not await validate_openai_api_key(api_key_data.openai_api_key):
            raise HTTPException(status_code=400, detail="Invalid OpenAI API key")

        # Encrypt and store the new API key
        encrypted_key = encrypt_api_key(api_key_data.openai_api_key)
        data_store["users"][current_user]["openai_api_key"] = encrypted_key
        save_data(data_store)

        logger.info(f"OpenAI API key updated for user: {current_user}")

        return {
            "message": "API key updated successfully!",
            "has_openai_key": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API key")

@app.delete("/api/settings/api-key")
async def delete_api_key(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data_store["users"][current_user]["openai_api_key"] = None
        save_data(data_store)

        logger.info(f"OpenAI API key deleted for user: {current_user}")

        return {
            "message": "API key deleted successfully",
            "has_openai_key": False
        }

    except Exception as e:
        logger.error(f"API key deletion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete API key")

# AI Generation endpoints
@app.post("/api/ai/generate-journal")
async def generate_journal(request: AIGenerationRequest, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user has OpenAI API key
        encrypted_key = user.get("openai_api_key")
        if not encrypted_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key required. Please add your API key in settings to start creating AI-powered journals."
            )

        # Decrypt API key
        try:
            api_key = decrypt_api_key(encrypted_key)
        except Exception as e:
            logger.error(f"API key decryption error: {e}")
            raise HTTPException(status_code=500, detail="Failed to access API key")

        # Sanitize inputs
        theme = sanitize_input(request.theme)
        title_style = sanitize_input(request.title_style)
        description = sanitize_input(request.description)

        # Create job ID
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Initialize job
        data_store["ai_jobs"][job_id] = {
            "id": job_id,
            "theme": theme,
            "title_style": title_style,
            "description": description,
            "status": "pending",
            "progress": 0,
            "created_at": time.time(),
            "user_id": current_user
        }
        save_data(data_store)

        # Start background task
        asyncio.create_task(real_openai_generation(job_id, theme, title_style, api_key, current_user))

        logger.info(f"AI generation started by user {current_user}: {job_id}")

        return {
            "success": True,
            "message": "Journal generation started",
            "job_id": job_id,
            "estimated_time": 180,
            "status": "pending"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def real_openai_generation(job_id: str, theme: str, title_style: str, api_key: str, user_id: str):
    """Real OpenAI API integration for journal generation"""
    stages = [
        (10, "🤖 Initializing AI generation..."),
        (25, "📚 Analyzing theme and style patterns..."),
        (40, "✍️ Generating journal content structure..."),
        (60, "🎨 Creating daily journal entries..."),
        (80, "📄 Formatting and organizing content..."),
        (95, "🔧 Finalizing journal design..."),
        (100, "✅ Complete!")
    ]

    client = openai.OpenAI(api_key=api_key)
    total_tokens_used = 0
    total_cost = 0.0

    try:
        for progress, stage in stages:
            if job_id not in data_store["ai_jobs"]:
                return  # Job was cancelled

            data_store["ai_jobs"][job_id]["progress"] = progress
            data_store["ai_jobs"][job_id]["current_stage"] = stage
            save_data(data_store)

            # Generate content based on stage
            if progress == 25:
                # Generate content structure
                system_prompt = f"""
                You are creating a 30-day journal focused on {theme}.
                Style: {title_style}
                Generate a structured outline for daily journal entries.
                Each entry should include:
                - Date and title
                - Main prompt/question
                - Reflection space
                - Optional creative exercise

                Return as JSON format with array of 30 entries.
                """

                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful journal content creator."},
                        {"role": "user", "content": system_prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )

                content_structure = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                total_tokens_used += tokens_used
                total_cost += tokens_used * 0.000002  # Approximate cost for gpt-3.5-turbo

                # Store structure for later use
                data_store["ai_jobs"][job_id]["content_structure"] = content_structure

            elif progress == 60:
                # Generate actual content
                content_structure = data_store["ai_jobs"][job_id].get("content_structure", "")

                content_prompt = f"""
                Based on this structure for a {theme} journal with {title_style} style:

                {content_structure}

                Expand each entry into a complete journal entry. Include:
                - Inspiring quotes related to the theme
                - Thoughtful questions
                - Creative exercises
                - Space for reflection

                Generate complete, ready-to-use content for all 30 days.
                Format as JSON with entries array containing date, title, and content.
                """

                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a creative journal content writer."},
                        {"role": "user", "content": content_prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.8
                )

                journal_content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                total_tokens_used += tokens_used
                total_cost += tokens_used * 0.000002

                data_store["ai_jobs"][job_id]["journal_content"] = journal_content

            elif progress == 100:
                # Create completed project
                project_id = f"project_{uuid.uuid4().hex[:12]}"
                data_store["ai_jobs"][job_id]["status"] = "completed"

                data_store["projects"][project_id] = {
                    "id": project_id,
                    "title": f"{title_style.title()} {theme.title()} Journal",
                    "theme": theme,
                    "description": f"AI-generated {theme} journal with {title_style} style",
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
                    "export_formats": ["pdf", "epub", "kdp"],
                    "job_id": job_id,
                    "user_id": user_id,
                    "content": data_store["ai_jobs"][job_id].get("journal_content", ""),
                    "tokens_used": total_tokens_used,
                    "cost": total_cost
                }

                # Update user usage stats
                if user_id not in data_store["usage_stats"]:
                    data_store["usage_stats"][user_id] = {
                        "total_cost": 0.0,
                        "total_tokens": 0,
                        "usage_history": []
                    }

                data_store["usage_stats"][user_id]["total_cost"] += total_cost
                data_store["usage_stats"][user_id]["total_tokens"] += total_tokens_used
                data_store["usage_stats"][user_id]["usage_history"].append({
                    "timestamp": time.time(),
                    "job_id": job_id,
                    "tokens_used": total_tokens_used,
                    "cost": total_cost,
                    "theme": theme,
                    "title_style": title_style
                })

            save_data(data_store)
            await asyncio.sleep(2)  # Realistic timing between stages

    except Exception as e:
        logger.error(f"OpenAI generation error for job {job_id}: {e}")
        if job_id in data_store["ai_jobs"]:
            data_store["ai_jobs"][job_id]["status"] = "failed"
            data_store["ai_jobs"][job_id]["error"] = str(e)
            save_data(data_store)

# Progress tracking endpoint
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
        "status": job.get("status", "unknown"),
        "progress": job.get("progress", 0),
        "current_stage": job.get("current_stage", ""),
        "created_at": job.get("created_at"),
        "error": job.get("error")
    }

# Projects endpoint
@app.get("/api/projects")
async def get_user_projects(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user_projects = []
        for project_id, project in data_store.get("projects", {}).items():
            if project.get("user_id") == current_user:
                user_projects.append(project)

        return {
            "projects": user_projects,
            "total": len(user_projects)
        }
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to get projects")

# Perfect web interface
@app.get("/", response_class=HTMLResponse)
async def web_interface():
    """Perfect authentication interface with settings-based API key management"""

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Journal Craft Crew - Perfect Authentication</title>
    <style>
        :root {
            --primary-color: #10a37f;
            --primary-hover: #0d8f6f;
            --secondary-color: #64748b;
            --success-color: #22c55e;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --background: #ffffff;
            --surface: #f8fafc;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --radius: 8px;
            --transition: all 0.2s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--background);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        header {
            background: var(--background);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
            background: rgba(255, 255, 255, 0.95);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .logo-icon {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }

        main {
            padding: 2rem 0;
            min-height: calc(100vh - 80px);
        }

        .hero {
            text-align: center;
            padding: 4rem 0;
            background: linear-gradient(135deg, var(--surface), var(--background));
            border-radius: 16px;
            margin-bottom: 3rem;
        }

        .hero h1 {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
        }

        .hero p {
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 2rem;
        }

        .value-proposition {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }

        .value-card {
            background: var(--background);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 2rem;
            text-align: center;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }

        .value-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }

        .value-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        .value-card h3 {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }

        .value-card p {
            color: var(--text-secondary);
            font-size: 0.95rem;
        }

        .auth-forms {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 3rem;
        }

        .auth-card {
            background: var(--background);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 2rem;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }

        .auth-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }

        .auth-card h2 {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }

        input, select {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            font-size: 1rem;
            transition: var(--transition);
            background: var(--background);
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1);
        }

        .btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: var(--radius);
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            text-decoration: none;
            width: 100%;
            justify-content: center;
        }

        .btn:hover {
            background: var(--primary-hover);
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn:disabled {
            background: var(--secondary-color);
            cursor: not-allowed;
            transform: none;
        }

        .dashboard {
            display: none;
        }

        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: var(--surface);
            border-radius: var(--radius);
            border: 1px solid var(--border-color);
        }

        .dashboard-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }

        .stat-card {
            background: var(--background);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            text-align: center;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.875rem;
        }

        .api-key-status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }

        .api-key-status.connected {
            background: rgba(34, 197, 94, 0.1);
            color: var(--success-color);
        }

        .api-key-status.disconnected {
            background: rgba(239, 68, 68, 0.1);
            color: var(--error-color);
        }

        .generation-form {
            background: var(--background);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 2rem;
            box-shadow: var(--shadow-sm);
            margin-bottom: 2rem;
        }

        .settings-section {
            background: var(--background);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 2rem;
            box-shadow: var(--shadow-sm);
            margin-bottom: 2rem;
        }

        .api-key-form {
            margin-bottom: 1.5rem;
        }

        .api-key-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
        }

        .api-key-help {
            margin-top: 0.5rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }

        .api-key-help a {
            color: var(--primary-color);
            text-decoration: none;
        }

        .api-key-help a:hover {
            text-decoration: underline;
        }

        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .project-card {
            background: var(--background);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }

        .project-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--border-color);
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
            border-radius: 4px;
            transition: width 0.3s ease;
        }

        .alert {
            padding: 1rem;
            border-radius: var(--radius);
            margin-bottom: 1rem;
            display: none;
        }

        .alert-success {
            background: rgba(34, 197, 94, 0.1);
            color: var(--success-color);
            border: 1px solid rgba(34, 197, 94, 0.2);
        }

        .alert-error {
            background: rgba(239, 68, 68, 0.1);
            color: var(--error-color);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .alert-warning {
            background: rgba(245, 158, 11, 0.1);
            color: var(--warning-color);
            border: 1px solid rgba(245, 158, 11, 0.2);
        }

        .hidden {
            display: none !important;
        }

        .settings-nav {
            display: flex;
            gap: 2rem;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1rem;
        }

        .settings-tab {
            padding: 0.5rem 1rem;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-weight: 500;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: var(--transition);
        }

        .settings-tab.active {
            color: var(--primary-color);
            border-bottom-color: var(--primary-color);
        }

        .settings-tab:hover {
            color: var(--text-primary);
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2rem;
            }

            .auth-forms {
                grid-template-columns: 1fr;
            }

            .dashboard-stats {
                grid-template-columns: 1fr;
            }

            .value-proposition {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <div class="logo-icon">J</div>
                    <span>Journal Craft Crew</span>
                </div>
                <div class="user-info">
                    <div id="userInfo" class="hidden">
                        <span id="username"></span>
                        <div class="user-avatar" id="userAvatar"></div>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main>
        <div class="container">
            <div id="alertContainer"></div>

            <section class="auth-section" id="authSection">
                <div class="hero">
                    <h1>Create Beautiful Journals with AI</h1>
                    <p>Transform your ideas into stunning 30-day journals using real OpenAI technology</p>
                </div>

                <div class="value-proposition">
                    <div class="value-card">
                        <div class="value-icon">🔐</div>
                        <h3>Easy Setup</h3>
                        <p>Create your account in seconds, add API key when ready</p>
                    </div>
                    <div class="value-card">
                        <div class="value-icon">🤖</div>
                        <h3>Real AI Generation</h3>
                        <p>Create authentic, high-quality journal content with advanced GPT technology</p>
                    </div>
                    <div>
                        <div class="value-icon">💰</div>
                        <h3>Transparent Costs</h3>
                        <p>Track your usage and pay only for what you use</p>
                    </div>
                </div>

                <div class="auth-forms">
                    <div class="auth-card">
                        <h2>🔐 Create Account</h2>
                        <form id="registerForm">
                            <div class="form-group">
                                <label for="regEmail">Email</label>
                                <input type="email" id="regEmail" required>
                            </div>
                            <div class="form-group">
                                <label for="regUsername">Username</label>
                                <input type="text" id="regUsername" required>
                            </div>
                            <div class="form-group">
                                <label for="regPassword">Password</label>
                                <input type="password" id="regPassword" required>
                            </div>
                            <div class="form-group">
                                <label for="regFullName">Full Name</label>
                                <input type="text" id="regFullName" required>
                            </div>
                            <button type="submit" class="btn">
                                <span>Create Account</span>
                                <span>→</span>
                            </button>
                        </form>
                    </div>

                    <div class="auth-card">
                        <h2>🚀 Login</h2>
                        <form id="loginForm">
                            <div class="form-group">
                                <label for="loginUsername">Username</label>
                                <input type="text" id="loginUsername" required>
                            </div>
                            <div class="form-group">
                                <label for="loginPassword">Password</label>
                                <input type="password" id="loginPassword" required>
                            </div>
                            <button type="submit" class="btn">
                                <span>Login</span>
                                <span>→</span>
                            </button>
                        </form>
                    </div>
                </div>
            </section>

            <section class="dashboard hidden" id="dashboardSection">
                <div class="dashboard-header">
                    <div>
                        <h1>Welcome back, <span id="username"></span>! 👋</h1>
                        <p>Ready to create your next AI-powered journal?</p>
                    </div>
                    <div>
                        <button class="btn settings-tab" onclick="showSettings()">
                            ⚙️ Settings
                        </button>
                        <button class="btn settings-tab active" onclick="showDashboard()">
                            📋 Dashboard
                        </button>
                    </div>
                </div>

                <!-- Dashboard View -->
                <div id="dashboardView">
                    <div class="dashboard-stats">
                        <div class="stat-card">
                            <div class="stat-value" id="totalProjects">0</div>
                            <div class="stat-label">Projects</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="totalTokens">0</div>
                            <div class="stat-label">Tokens Used</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="totalCost">$0.00</div>
                            <div class="stat-label">Total Cost</div>
                        </div>
                        <div class="stat-card">
                            <div class="api-key-status disconnected" id="apiKeyStatusHeader">
                                <span>❌ No API Key</span>
                            </div>
                            <div class="stat-label">Status</div>
                        </div>
                    </div>

                    <div class="generation-form">
                        <h2>🎨 Create New Journal</h2>
                        <form id="generationForm">
                            <div class="form-group">
                                <label for="journalTheme">Journal Theme</label>
                                <input type="text" id="journalTheme" required
                                       placeholder="e.g., Mindfulness, Creative Writing, Daily Reflection">
                            </div>
                            <div class="form-group">
                                <label for="titleStyle">Title Style</label>
                                <select id="titleStyle" required>
                                    <option value="">Select style...</option>
                                    <option value="classic">Classic</option>
                                    <option value="modern">Modern</option>
                                    <option value="creative">Creative</option>
                                    <option value="professional">Professional</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="journalDescription">Description (Optional)</label>
                                <input type="text" id="journalDescription"
                                       placeholder="Describe your vision for this journal">
                            </div>
                            <button type="submit" class="btn" id="generateBtn">
                                <span>⚡ Generate Journal with AI</span>
                            </button>
                        </form>
                    </div>

                    <div>
                        <h2>📚 Your Projects</h2>
                        <div class="projects-grid" id="projectsGrid">
                            <!-- Projects will be loaded here -->
                        </div>
                    </div>
                </div>

                <!-- Settings View -->
                <div id="settingsView" class="hidden">
                    <div class="settings-section">
                        <h2>⚙️ Account Settings</h2>

                        <div class="api-key-form">
                            <h3>OpenAI API Key</h3>
                            <div class="form-group">
                                <label for="apiKeyInput">Your OpenAI API Key</label>
                                <input type="password" id="apiKeyInput" class="api-key-input"
                                       placeholder="sk-...">
                                <div class="api-key-help">
                                    Add your personal OpenAI API key to enable AI journal generation.
                                    <a href="https://platform.openai.com/api-keys" target="_blank">Get your API key</a>
                                </div>
                            </div>
                            <button type="button" class="btn" id="saveApiKeyBtn">
                                <span>💾 Save API Key</span>
                            </button>
                            <button type="button" class="btn" id="deleteApiKeyBtn" style="background: var(--error-color); display: none;">
                                <span>🗑️ Remove Key</span>
                            </button>
                        </div>

                        <div class="settings-section">
                            <h3>Usage Statistics</h3>
                            <div class="dashboard-stats">
                                <div class="stat-card">
                                    <div class="stat-value" id="settingsTotalTokens">0</div>
                                    <div>
                                        <div class="stat-label">Total Tokens</div>
                                    </div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" id="settingsTotalCost">$0.00</div>
                                    <div>
                                        <div class="stat-label">Total Cost</div>
                                    </div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" id="settingsTotalProjects">0</div>
                                    <div>
                                        <div class="stat-label">Projects Created</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="settings-section">
                            <h3>Account Information</h3>
                            <p><strong>Username:</strong> <span id="settingsUsername"></span></p>
                            <p><strong>Email:</strong> <span id="settingsEmail"></span></p>
                            <p><strong>Member Since:</strong> <span id="settingsCreatedDate"></span></p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </main>

    <script>
        let authToken = localStorage.getItem('authToken');
        let currentUser = null;
        let currentView = 'dashboard'; // 'dashboard' or 'settings'

        // Check authentication on load
        document.addEventListener('DOMContentLoaded', function() {
            if (authToken) {
                loadUserProfile();
            }
        });

        // Registration
        document.getElementById('registerForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = {
                email: document.getElementById('regEmail').value,
                username: document.getElementById('regUsername').value,
                password: document.getElementById('regPassword').value,
                full_name: document.getElementById('regFullName').value
            };

            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    authToken = data.access_token;
                    localStorage.setItem('authToken', authToken);
                    showAlert('Account created successfully!', 'success');
                    loadUserProfile();
                } else {
                    showAlert(data.detail || 'Registration failed', 'error');
                }
            } catch (error) {
                showAlert('Network error. Please try again.', 'error');
            }
        });

        // Login
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = {
                username: document.getElementById('loginUsername').value,
                password: document.getElementById('loginPassword').value
            };

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    authToken = data.access_token;
                    localStorage.setItem('authToken', authToken);
                    showAlert('Login successful!', 'success');
                    loadUserProfile();
                } else {
                    showAlert(data.detail || 'Login failed', 'error');
                }
            } catch (error) {
                showAlert('Network error. Please try again.', 'error');
            }
        });

        // Load user profile
        async function loadUserProfile() {
            try {
                const response = await fetch('/api/settings', {
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    currentUser = data.user;
                    showDashboard(data);
                } else {
                    localStorage.removeItem('authToken');
                    authToken = null;
                }
            } catch (error) {
                console.error('Profile load error:', error);
            }
        }

        // Show dashboard view
        function showDashboard(userData) {
            document.getElementById('authSection').classList.add('hidden');
            document.getElementById('dashboardSection').classList.remove('hidden');

            // Update user info in header
            document.getElementById('username').textContent = userData.username;
            document.getElementById('userAvatar').textContent = userData.username[0].toUpperCase();
            document.getElementById('userInfo').classList.remove('hidden');

            // Update dashboard stats
            document.getElementById('totalProjects').textContent = userData.usage_stats.total_projects || 0;
            document.getElementById('totalTokens').textContent = userData.usage_stats.total_tokens.toLocaleString();
            document.getElementById('totalCost').textContent = `$${userData.usage_stats.total_cost.toFixed(4)}`;

            // Update API key status
            const apiKeyStatus = document.getElementById('apiKeyStatusHeader');
            if (userData.user.has_openai_key) {
                apiKeyStatus.className = 'api-key-status connected';
                apiKeyStatus.innerHTML = '<span>✅ API Key Active</span>';
            } else {
                apiKeyStatus.className = 'apiKey-status disconnected';
                apiKeyStatus.innerHTML = '<span>❌ No API Key</span>';
            }

            loadProjects();
            showDashboardView();
        }

        // Show settings view
        function showSettings() {
            document.getElementById('dashboardView').classList.add('hidden');
            document.getElementById('settingsView').classList.remove('hidden');

            // Update settings stats
            document.getElementById('settingsTotalTokens').textContent = currentUser.usage_stats.total_tokens.toLocaleString();
            document.getElementById('settingsTotalCost').textContent = `$${currentUser.usage_stats.total_cost.toFixed(4)}`;
            document.getElementById('settingsTotalProjects').textContent = (data_store.projects ? Object.values(data_store.projects).filter(p => p.user_id === currentUser.username).length : 0);

            // Update account info
            document.getElementById('settingsUsername').textContent = currentUser.username;
            document.getElementById('settingsEmail').textContent = currentUser.email;
            document.getElementById('settingsCreatedDate').textContent = new Date(currentUser.created_at * 1000).toLocaleDateString();

            // Update API key form
            const apiKeyBtn = document.getElementById('saveApiKeyBtn');
            const deleteBtn = document.getElementById('deleteApiKeyBtn');
            const apiKeyInput = document.getElementById('apiKeyInput');

            if (currentUser.user.has_openai_key) {
                apiKeyBtn.textContent = '💾 Update API Key';
                apiKeyBtn.style.background = 'var(--primary-color)';
                deleteBtn.style.display = 'inline-block';
                apiKeyInput.placeholder = '•••••••••••••••••••••••••••••••••••••••••••••';
                apiKeyInput.disabled = true;
            } else {
                apiKeyBtn.textContent = '💾 Add API Key';
                apiKeyBtn.style.background = 'var(--primary-color)';
                deleteBtn.style.display = 'none';
                apiKeyInput.placeholder = 'sk-...';
                apiKeyInput.disabled = false;
            }
        }

        // Show dashboard view
        function showDashboardView() {
            document.getElementById('dashboardView').classList.remove('hidden');
            document.getElementById('settingsView').classList.add('hidden');
        }

        // Navigation tabs
        function showDashboard() {
            currentView = 'dashboard';
            showDashboardView();
        }

        // Load projects
        async function loadProjects() {
            try {
                const response = await fetch('/api/projects', {
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    displayProjects(data.projects);
                    document.getElementById('totalProjects').textContent = data.total;
                }
            } catch (error) {
                console.error('Projects load error:', error);
            }
        }

        // Display projects
        function displayProjects(projects) {
            const grid = document.getElementById('projectsGrid');

            if (projects.length === 0) {
                grid.innerHTML = '<p>No projects yet. Create your first AI-powered journal!</p>';
                return;
            }

            grid.innerHTML = projects.map(project => `
                <div class="project-card">
                    <h3>${project.title}</h3>
                    <p><strong>Theme:</strong> ${project.theme}</p>
                    <p><strong>Style:</strong> ${project.customization?.title_style || 'N/A'}</p>
                    <p><strong>Status:</strong> ${project.status}</p>
                    <p><strong>Words:</strong> ${project.word_count?.toLocaleString() || 'N/A'}</p>
                    <p><strong>Cost:</strong> $${project.cost?.toFixed(4) || '0.0000'}</p>
                    ${project.job_id ? `
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%" id="progress-${project.job_id}"></div>
                        </div>
                        <div id="status-${project.job_id}">Loading...</div>
                    ` : ''}
                </div>
            `).join('');

            // Start progress monitoring for jobs
            projects.forEach(project => {
                if (project.job_id) {
                    monitorProgress(project.job_id);
                }
            });
        }

        // Monitor progress
        async function monitorProgress(jobId) {
            const updateProgress = async () => {
                try {
                    const response = await fetch(`/api/ai/progress/${jobId}`, {
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                        }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        const progressBar = document.getElementById(`progress-${jobId}`);
                        const statusDiv = document.getElementById(`status-${jobId}`);

                        if (progressBar) {
                            progressBar.style.width = `${data.progress}%`;
                        }

                        if (statusDiv) {
                            statusDiv.textContent = `${data.current_stage} (${data.progress}%)`;
                        }

                        if (data.status === 'completed' || data.status === 'failed') {
                            if (data.status === 'completed') {
                                loadProjects(); // Refresh projects
                            }
                            return;
                        }

                        setTimeout(updateProgress, 2000);
                    }
                } catch (error) {
                    console.error('Progress monitoring error:', error);
                }
            };

            updateProgress();
        }

        // Journal generation
        document.getElementById('generationForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            // Check if user has API key
            if (!currentUser || !currentUser.user.has_openai_key) {
                showAlert('Please add your OpenAI API key in settings to create AI-powered journals.', 'warning');
                showSettings();
                return;
            }

            const generateBtn = document.getElementById('generateBtn');
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span>⚡ Generating...</span>';

            const formData = {
                theme: document.getElementById('journalTheme').value,
                title_style: document.getElementById('titleStyle').value,
                description: document.getElementById('journalDescription').value
            };

            try {
                const response = await fetch('/api/ai/generate-journal', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`,
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert(`Journal generation started! Job ID: ${data.job_id}`, 'success');
                    document.getElementById('generationForm').reset();
                    setTimeout(() => loadProjects(), 1000);
                } else {
                    showAlert(data.detail || 'Generation failed', 'error');
                }
            } catch (error) {
                showAlert('Network error. Please try again.', 'error');
            } finally {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<span>⚡ Generate Journal with AI</span>';
            }
        });

        // Settings API Key management
        document.getElementById('saveApiKeyBtn').addEventListener('click', async function() {
            const apiKeyInput = document.getElementById('apiKeyInput');
            const apiKey = apiKeyInput.value.trim();

            if (!apiKey) {
                showAlert('Please enter your OpenAI API key.', 'error');
                return;
            }

            if (!apiKey.startsWith('sk-')) {
                showAlert('Invalid OpenAI API key format. It should start with "sk-"', 'error');
                return;
            }

            const isUpdate = currentUser && currentUser.user.has_openai_key;

            try {
                const endpoint = isUpdate ? '/api/settings/api-key' : '/api/settings/api-key';
                const method = isUpdate ? 'PUT' : 'POST';

                const response = await fetch(endpoint, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`,
                    },
                    body: JSON.stringify({
                        openai_api_key: apiKey
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert(data.message, 'success');
                    // Reload user profile to update status
                    loadUserProfile();
                } else {
                    showAlert(data.detail || 'Failed to save API key', 'error');
                }
            } catch (error) {
                showAlert('Network error. Please try again.', 'error');
            }
        });

        document.getElementById('deleteApiKeyBtn').addEventListener('click', async function() {
            if (!confirm('Are you sure you want to remove your OpenAI API key? This will disable AI journal generation.')) {
                return;
            }

            try {
                const response = await fetch('/api/settings/api-key', {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                    }
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert(data.message, 'success');
                    // Reload user profile to update status
                    loadUserProfile();
                } else {
                    showAlert(data.detail || 'Failed to remove API key', 'error');
                }
            } catch (error) {
                showAlert('Network error. Please try again.', 'error');
            }
        });

        // Show alert
        function showAlert(message, type) {
            const alertContainer = document.getElementById('alertContainer');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            alert.style.display = 'block';

            alertContainer.appendChild(alert);

            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
    </script>
</body>
</html>
    """

    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Perfect Authentication Server")
    print("📍 Perfect Authentication Interface: http://localhost:8000")
    print("🔑 Settings-Based API Key Management")
    print("📋 No Development Section, No AI Credits")
    print("📋 Users:", len(data_store.get('users', [])))
    print("📚 Projects:", len(data_store.get('projects', [])))
    print("🤖 Active AI Jobs:", len(data_store.get('ai_jobs', [])))
    print("💡 Features:")
    print("   - Clean, professional authentication interface")
    print("   - API key management in settings only")
    print("   - Seamless onboarding experience")
    print("   - Real AI journal generation")
    print("   - Transparent cost tracking")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )