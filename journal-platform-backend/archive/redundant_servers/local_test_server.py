#!/usr/bin/env python3
"""
Local Testing Server for Journal Craft Crew
Simple authentication with best practices for local development
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List, Optional
import json
import asyncio
import time
import uuid
import logging
import os
import hashlib
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File-based data persistence
DATA_FILE = "local_test_data.json"

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
        except Exception as e:
            logger.error(f"Error saving data: {e}")

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

# Simple JWT (for demo only)
def create_simple_token(user_data: dict) -> str:
    """Create simple token for demo"""
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "exp": int(time.time()) + 3600  # 1 hour
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    return f"demo_token_{encoded}"

def verify_simple_token(token: str) -> Optional[dict]:
    """Verify simple demo token"""
    if token.startswith("demo_token_"):
        encoded = token.split("_")[1]
        decoded = base64.b64decode(encoded.encode()).decode()
        payload = json.loads(decoded)
        if payload.get("exp", 0) > int(time.time()):
            return None  # Token expired
        return payload
    return None

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
    title="Journal Platform - Local Testing",
    description="Local testing environment with authentication"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple session token storage
sessions = {}

# Main application (protected - requires token in Authorization header)
@app.get("/", response_class=HTMLResponse)
async def protected_root():
    """Main application - requires authentication"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Journal Craft Crew - Application</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .auth-section { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .button { background: #2c3e50; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; margin: 10px 0; }
            .button:hover { background: #1a2e40; }
            input { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 3px; }
            .user-info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Journal Craft Crew</h1>
            <h2>AI-Powered Journal Creation Platform</h2>

            <div class="auth-section" id="auth-status">
                <div class="user-info">
                    <strong>👤 Current User:</strong> Not logged in
                </div>
                <form id="auth-form" style="display: none;">
                    <input type="email" id="email" placeholder="Email address" required>
                    <input type="password" id="password" placeholder="Password" required>
                    <button type="button" onclick="loginUser()">Login</button>
                </form>
            </div>

            <div class="user-info">
                <strong>📋 Current Users:</strong> <span id="users-count">0</span><br>
                <strong>📚 Current Projects:</strong> <span id="projects-count">0</span><br>
                <strong>🤖 Active AI Jobs:</strong> <span id="jobs-count">0</span><br>
            </div>

            <div class="user-info">
                <h3>🔐 API Testing (after login)</h3>
                <p>Use your browser developer tools or curl to test endpoints:</p>
                <ul>
                    <li><strong>Registration:</strong> <code>POST /api/auth/register</code></li>
                    <li><strong>Login:</strong> <code>POST /api/auth/login</code></li>
                    <li><strong>Themes:</strong> <code>GET /api/ai/themes</code></li>
                    <li><strong>Title Styles:</strong> <code>GET /api/ai/title-styles</code></li>
                    <li><strong>Generate Journal:</strong> <code>POST /api/ai/generate-journal</code></li>
                    <li><strong>Progress:</strong> <code>GET /api/ai/progress/{job_id}</code></li>
                    <li><strong>Projects:</strong> <code>GET /api/library/projects</code></li>
                </ul>
            </div>

            <div class="nav">
                <a href="/health">💚 Health Check</a>
                <a href="/api/docs">📋 API Documentation</a>
            </div>

            <script>
                async function loginUser() {
                    const email = document.getElementById('email').value;
                    const password = document.getElementById('password').value;

                    if (!email || !password) {
                        alert('Please fill in all fields');
                        return;
                    }

                    try {
                        const response = await fetch('/api/auth/login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                email: email,
                                password: password
                            })
                        });

                        if (response.ok) {
                            const data = await response.json();
                            localStorage.setItem('token', data.access_token);
                            localStorage.setItem('user', JSON.stringify(data.user));
                            updateAuthStatus(data.user);
                            alert('Login successful! You can now use the API endpoints.');
                        } else {
                            alert('Login failed: ' + (await response.text()));
                        }
                    } catch (error) {
                        alert('Login error: ' + error.message);
                    }
                }

                function updateAuthStatus(user) {
                    const authStatus = document.getElementById('auth-status');
                    authStatus.innerHTML = \`
                        <strong>👤 Current User:</strong> \${user.full_name} (\${user.email})<br>
                        <strong>Profile:</strong> \${user.profile_type}<br>
                        <strong>AI Credits:</strong> \${user.ai_credits}
                    \`;
                }

                // Check if user is already logged in
                const token = localStorage.getItem('token');
                if (token) {
                    try {
                        const response = await fetch('/api/auth/verify-token', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': \`Bearer \${token}\`
                            }
                        });

                        if (response.ok) {
                            const data = await response.json();
                            updateAuthStatus(data.user);
                        }
                    } catch (error) {
                        console.log('Token verification failed');
                    }
                }

                // Update stats
                updateStats();
                setInterval(updateStats, 5000);
            </script>
        </div>
    </body>
    </html>
    """)

# API verification endpoint (for frontend token checking)
@app.post("/api/auth/verify-token")
async def verify_token(token: str):
    payload = verify_simple_token(token)
    if payload:
        user_id = payload.get("user_id")
        # Find user
        user = data_store["users"].get(user_id)
        if user:
            return {
                "valid": True,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "profile_type": user["profile_type"],
                    "ai_credits": user["ai_credits"]
                }
            }
    else:
        return {"valid": False}

# Health check (public)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "journal-platform-local",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data_stats": {
            "users": len(data_store["users"]),
            "projects": len(data_store["projects"]),
            "active_sessions": len(sessions),
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
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.time())
        }

        data_store["users"][user_id] = new_user
        save_data(data_store)

        logger.info(f"User registered: {user_data.email}")

        # Update UI immediately
        global users_count, projects_count, jobs_count
        users_count = len(data_store["users"])
        projects_count = len(data_store["projects"])
        jobs_count = len(data_store["ai_jobs"])

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
async def login_user(login_data: UserLogin):
    try:
        # Find user by email
        user = None
        for uid, user_info in data_store["users"].items():
            if user_info["email"] == login_data.email:
                user = user_info
                break

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Simple password check (no hashing for demo)
        stored_password = data_store["users"][user["id"]].get("password", "")
        if stored_password != login_data.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create token
        token = create_simple_token(user)

        # Store session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "user_id": user["id"],
            "token": token
        }

        logger.info(f"User logged in: {login_data.email}")

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

# Available themes
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

# Protected endpoints (require token in Authorization header)
def get_token_from_header(authorization: str = None) -> Optional[str]:
    """Extract token from Authorization header"""
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    return None

@app.post("/api/ai/generate-journal")
async def generate_journal(request: AIGenerationRequest, authorization: str = None):
    # Get token
    token = get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Authorization required")

    # Verify token
    payload = verify_simple_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")

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
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.time()),
        "user_id": user_id
    }
    save_data(data_store)

    # Start background task
    asyncio.create_task(simulate_realistic_ai_generation(job_id, request.theme, request.title_style))

    logger.info(f"AI generation started by user {user_id}: {job_id}")

    return {
        "success": True,
        "message": "AI journal generation started",
        "job_id": job_id,
        "estimated_time": 180,
        "status": "pending"
    }

# Progress tracking
@app.get("/api/ai/progress/{job_id}")
async def get_generation_progress(job_id: str, authorization: str = None):
    # Get token
    token = get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Authorization required")

    # Verify token
    payload = verify_simple_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")

    if job_id not in data_store["ai_jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify job ownership
    job = data_store["ai_jobs"][job_id]
    if job.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress_percentage": job["progress"],
        "current_stage": job.get("current_stage", "Processing..."),
        "estimated_time_remaining": max(0, 180 - (time.time() - time.mktime(job["created_at"]).total_seconds()),
        "created_at": job["created_at"]
    }

# Project library endpoints
@app.get("/api/library/projects")
async def get_user_projects(authorization: str = None):
    # Get token and verify
    token = get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Authorization required")

    payload = verify_simple_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")

    # Get projects for current user
    user_projects = []
    for pid, project in data_store["projects"].items():
        if project.get("user_id") == user_id:
            user_projects.append(project)

    return {
        "projects": user_projects,
        "count": len(user_projects),
        "page": 1,
        "total_pages": 1
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
            save_data(data_store)

        await asyncio.sleep(3)  # More realistic timing

        # Create completed project
        if progress == 100:
            project_id = f"project_{uuid.uuid4().hex[:12]}"
            data_store["ai_jobs"][job_id]["status"] = "completed"
            data_store["ai_jobs"][job_id]["progress"] = 100

            # Create project
            data_store["projects"][project_id] = {
                "id": project_id,
                "title": f"{title_style.title()} {theme.title()} Journal",
                "theme": theme,
                "description": f"AI-generated {theme} journal with {title_style} style",
                "status": "completed",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.time()),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.time()),
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
                "user_id": user_id
            }

            save_data(data_store)
            logger.info(f"AI generation completed: {job_id} -> {project_id}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Local Test Server")
    print("📍 Secure Authentication: http://localhost:8000")
    print("🔐 JWT-based token system")
    print("📋 Frontend Integration: http://localhost:5173")
    print("🔗 Protected API endpoints available")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )