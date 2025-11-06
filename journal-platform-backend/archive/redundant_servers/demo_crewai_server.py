"""
Journal Craft Crew - Demo Integration Server
Demonstrates API structure for CrewAI integration
"""

import os
import json
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field
from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from jose import JWTError, jwt

# Configuration
SECRET_KEY = "demo-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Directory Structure
USERS_DIR = "users"
JOURNALS_DIR = "journals"
os.makedirs(USERS_DIR, exist_ok=True)
os.makedirs(JOURNALS_DIR, exist_ok=True)

# Initialize FastAPI
app = FastAPI(
    title="Journal Craft Crew - Demo API",
    description="Demo API for CrewAI integration - Shows structure without actual AI agents",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple password hashing for demo (avoiding bcrypt issues)
import hashlib
import secrets

def simple_hash_password(password: str) -> str:
    """Simple password hashing for demo purposes"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"

def simple_verify_password(plain_password: str, hashed_password: str) -> bool:
    """Simple password verification for demo purposes"""
    try:
        salt, stored_hash = hashed_password.split('$')
        pwd_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000)
        return pwd_hash.hex() == stored_hash
    except:
        return False

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory storage (for demo)
job_storage: Dict[str, Dict] = {}
websocket_connections: Dict[str, WebSocket] = {}

# Data Models
class User(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str
    openai_api_key: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class JournalCreationRequest(BaseModel):
    theme: str
    title: str
    title_style: str = "Professional"
    author_style: str = "Direct actionable"
    research_depth: str = "medium"

class UserChoice(BaseModel):
    choice: str
    choice_type: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    current_agent: Optional[str] = None
    progress: Optional[int] = None
    message: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

# Helper Functions
def verify_password(plain_password, hashed_password):
    return simple_verify_password(plain_password, hashed_password)

def get_password_hash(password):
    return simple_hash_password(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Job Management Functions
def create_job(user_id: str, job_type: str = "journal_generation") -> str:
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "user_id": user_id,
        "job_type": job_type,
        "status": "queued",
        "progress": 0,
        "current_agent": None,
        "message": "Job queued - waiting for CrewAI integration",
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }

    job_storage[job_id] = job_data
    return job_id

def update_job_status(job_id: str, status: str, current_agent: str = None,
                     progress: int = None, message: str = None, result: Dict = None, error: str = None):
    if job_id in job_storage:
        job_data = job_storage[job_id]
        job_data.update({
            "status": status,
            "current_agent": current_agent,
            "progress": progress,
            "message": message,
            "result": result,
            "error": error,
            "updated_at": datetime.now().isoformat()
        })

        # Send WebSocket update if connected
        if job_id in websocket_connections:
            asyncio.create_task(send_websocket_update(job_id, job_data))

def get_job_status(job_id: str) -> Optional[Dict]:
    return job_storage.get(job_id)

async def send_websocket_update(job_id: str, job_data: Dict):
    if job_id in websocket_connections:
        try:
            websocket = websocket_connections[job_id]
            await websocket.send_text(json.dumps(job_data))
        except:
            # Connection broken, remove it
            del websocket_connections[job_id]

# Demo CrewAI Integration (Simulated)
async def simulate_crewai_workflow(job_id: str, user_preferences: Dict):
    """Simulate the CrewAI workflow for demonstration"""
    try:
        # Simulate different phases of CrewAI workflow
        phases = [
            {"agent": "onboarding", "progress": 10, "message": "Gathering user preferences"},
            {"agent": "discovery", "progress": 20, "message": "Generating title ideas"},
            {"agent": "research", "progress": 35, "message": "Researching content"},
            {"agent": "content_curator", "progress": 55, "message": "Creating journal content"},
            {"agent": "editor", "progress": 75, "message": "Polishing content"},
            {"agent": "media", "progress": 90, "message": "Generating media"},
            {"agent": "pdf_builder", "progress": 100, "message": "Creating PDFs"}
        ]

        for phase in phases:
            await asyncio.sleep(2)  # Simulate work being done
            update_job_status(
                job_id,
                "running",
                current_agent=phase["agent"],
                progress=phase["progress"],
                message=phase["message"]
            )

        # Simulate completion
        update_job_status(
            job_id,
            "completed",
            progress=100,
            message="Journal generation completed!",
            result={
                "journal_path": f"/journals/{user_preferences['user_id']}/demo_journal.pdf",
                "lead_magnet_path": f"/journals/{user_preferences['user_id']}/demo_lead_magnet.pdf",
                "theme": user_preferences["theme"],
                "title": user_preferences["title"]
            }
        )

    except Exception as e:
        update_job_status(job_id, "failed", error=str(e), message=f"Error: {str(e)}")

# Sample user database
fake_users_db = {
    "johndoe": {
        "email": "johndoe@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "hashed_password": get_password_hash("secret"),
        "disabled": False,
        "openai_api_key": os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
    }
}

# API Routes
@app.post("/register", response_model=Token)
async def register_user(user: UserRegistration):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    hashed_password = get_password_hash(user.password)
    fake_users_db[user.username] = {
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "disabled": False,
        "openai_api_key": None,
        "created_at": datetime.now().isoformat()
    }

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user

@app.post("/api/journals/create")
async def create_journal(
    request: JournalCreationRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_active_user)
):
    if not current_user.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured. Please add it in settings."
        )

    # Create job
    job_id = create_job(current_user.username, "journal_generation")

    # Prepare user preferences
    user_preferences = {
        "user_id": current_user.username,
        "theme": request.theme,
        "title": request.title,
        "title_style": request.title_style,
        "author_style": request.author_style,
        "research_depth": request.research_depth
    }

    # Start background task (simulated CrewAI workflow)
    background_tasks.add_task(
        simulate_crewai_workflow,
        job_id,
        user_preferences
    )

    return {"job_id": job_id, "status": "started"}

@app.get("/api/journals/status/{job_id}")
async def get_job_status_endpoint(
    job_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    job_status = get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_status["user_id"] != current_user.username:
        raise HTTPException(status_code=403, detail="Access denied")

    return JobStatus(**job_status)

@app.post("/api/journals/choices/{job_id}")
async def submit_user_choice(
    job_id: str,
    choice: UserChoice,
    current_user: UserInDB = Depends(get_current_active_user)
):
    job_status = get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_status["user_id"] != current_user.username:
        raise HTTPException(status_code=403, detail="Access denied")

    # In a real implementation, this would handle user decisions like title selection
    update_job_status(
        job_id,
        "running",
        message=f"User choice received: {choice.choice} ({choice.choice_type})"
    )

    return {"status": "choice_submitted"}

@app.get("/api/journals/projects/{user_id}")
async def get_user_projects(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    if user_id != current_user.username:
        raise HTTPException(status_code=403, detail="Access denied")

    user_dir = os.path.join(JOURNALS_DIR, user_id)
    projects = []

    if os.path.exists(user_dir):
        for project_name in os.listdir(user_dir):
            project_path = os.path.join(user_dir, project_name)
            if os.path.isdir(project_path):
                project_info = {
                    "name": project_name,
                    "path": project_path,
                    "created": datetime.fromtimestamp(os.path.getctime(project_path)).isoformat(),
                    "has_pdfs": False,
                    "has_media": False
                }
                projects.append(project_info)

    return {"projects": projects}

@app.get("/api/journals/download/{project_id}")
async def download_project_file(
    project_id: str,
    file_type: str = "journal",
    current_user: UserInDB = Depends(get_current_active_user)
):
    # This is a demo version - in production, validate project ownership
    project_path = os.path.join(JOURNALS_DIR, current_user.username, project_id)

    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project not found")

    # Return demo file info
    return {
        "message": f"Download request for {file_type} from project {project_id}",
        "file_path": f"{project_path}/{file_type}.pdf",
        "demo": True
    }

@app.websocket("/ws/journals/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()
    websocket_connections[job_id] = websocket

    try:
        # Send current status immediately
        job_status = get_job_status(job_id)
        if job_status:
            await websocket.send_text(json.dumps(job_status))

        # Keep connection alive
        while True:
            try:
                await websocket.receive_text()  # Keep connection open
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    finally:
        if job_id in websocket_connections:
            del websocket_connections[job_id]

# Settings endpoints
@app.get("/api/settings")
async def get_settings(current_user: UserInDB = Depends(get_current_active_user)):
    return {
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "openai_api_key_configured": bool(current_user.openai_api_key),
        "created_at": current_user.created_at.isoformat()
    }

@app.post("/api/settings/api-key")
async def add_api_key(
    api_key: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    # Validate API key (basic validation)
    if not api_key.startswith("sk-") or len(api_key) < 20:
        raise HTTPException(status_code=400, detail="Invalid OpenAI API key format")

    # Update user's API key
    fake_users_db[current_user.username]["openai_api_key"] = api_key
    current_user.openai_api_key = api_key

    return {"message": "API key configured successfully"}

@app.delete("/api/settings/api-key")
async def delete_api_key(current_user: UserInDB = Depends(get_current_active_user)):
    fake_users_db[current_user.username]["openai_api_key"] = None
    current_user.openai_api_key = None

    return {"message": "API key removed successfully"}

# Demo endpoints to show CrewAI integration structure
@app.get("/api/demo/crewai-agents")
async def get_crewai_agents():
    """Demo endpoint showing available CrewAI agents"""
    return {
        "agents": [
            {
                "name": "Manager Agent",
                "role": "Orchestrates the entire journal creation workflow",
                "status": "Ready for integration"
            },
            {
                "name": "Onboarding Agent",
                "role": "Gathers user preferences and handles project setup",
                "status": "Ready for integration"
            },
            {
                "name": "Discovery Agent",
                "role": "Generates title ideas based on themes and styles",
                "status": "Ready for integration"
            },
            {
                "name": "Research Agent",
                "role": "Gathers theme-specific insights with configurable depth",
                "status": "Ready for integration"
            },
            {
                "name": "Content Curator Agent",
                "role": "Creates 30-day journals and 6-day lead magnets",
                "status": "Ready for integration"
            },
            {
                "name": "Editor Agent",
                "role": "Polishes content with sentiment analysis",
                "status": "Ready for integration"
            },
            {
                "name": "Media Agent",
                "role": "Generates images based on content requirements",
                "status": "Ready for integration"
            },
            {
                "name": "PDF Builder Agent",
                "role": "Creates professional PDFs with media support",
                "status": "Ready for integration"
            }
        ],
        "integration_status": "API structure ready, requires CrewAI package installation"
    }

@app.get("/api/demo/workflow-steps")
async def get_workflow_steps():
    """Demo endpoint showing workflow steps"""
    return {
        "workflow_steps": [
            {"step": 1, "agent": "onboarding", "description": "Gather user preferences"},
            {"step": 2, "agent": "discovery", "description": "Generate title ideas"},
            {"step": 3, "agent": "research", "description": "Research content"},
            {"step": 4, "agent": "content_curator", "description": "Create journal content"},
            {"step": 5, "agent": "editor", "description": "Polish content"},
            {"step": 6, "agent": "media", "description": "Generate media"},
            {"step": 7, "agent": "pdf_builder", "description": "Create PDFs"}
        ],
        "total_steps": 7,
        "estimated_time": "5-10 minutes"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Journal Craft Crew - Demo Integration Server")
    print("📍 API Structure Demo - Shows how CrewAI agents will integrate")
    print("🔗 API Documentation: http://localhost:8000/docs")
    print("💡 Note: This is a demo showing API structure. Actual CrewAI integration requires:")
    print("   - pip install crewai fpdf2")
    print("   - OpenAI API key configuration")
    print("   - Redis for job management (optional)")
    uvicorn.run(app, host="0.0.0.0", port=8000)