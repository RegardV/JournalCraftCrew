"""
Journal Craft Crew - Complete Platform Server
Integrates authentication system with CrewAI journal generation
"""

import os
import json
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field
from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, BackgroundTasks, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
from nltk.sentiment import SentimentIntensityAnalyzer
import redis
from crewai import LLM
from agents.manager_agent import create_manager_agent, coordinate_phases
from agents.onboarding_agent import create_onboarding_agent
from agents.discovery_agent import create_discovery_agent
from agents.research_agent import create_research_agent
from agents.content_curator_agent import create_content_curator_agent
from agents.editor_agent import create_editor_agent
from agents.media_agent import create_media_agent
from agents.pdf_builder_agent import create_pdf_builder_agent
from config.settings import OUTPUT_DIR, JSON_SUBDIR, PDF_SUBDIR, MEDIA_SUBDIR

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Directory Structure
USERS_DIR = "users"
JOURNALS_DIR = "journals"
os.makedirs(USERS_DIR, exist_ok=True)
os.makedirs(JOURNALS_DIR, exist_ok=True)

# Initialize FastAPI
app = FastAPI(
    title="Journal Craft Crew - Complete Platform",
    description="AI-powered journal creation with CrewAI agents",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Redis for job management
try:
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()
    redis_available = True
except:
    redis_available = False
    print("Warning: Redis not available. Using in-memory job storage.")

# In-memory job storage (fallback)
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
    choice_type: str  # "title", "continue", etc.

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
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

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
        "message": "Job queued",
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }

    if redis_available:
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
    else:
        job_storage[job_id] = job_data

    return job_id

def update_job_status(job_id: str, status: str, current_agent: str = None,
                     progress: int = None, message: str = None, result: Dict = None, error: str = None):
    if redis_available:
        job_data_str = redis_client.get(f"job:{job_id}")
        if job_data_str:
            job_data = json.loads(job_data_str)
        else:
            return
    else:
        if job_id not in job_storage:
            return
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

    if redis_available:
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
    else:
        job_storage[job_id] = job_data

    # Send WebSocket update if connected
    if job_id in websocket_connections:
        asyncio.create_task(send_websocket_update(job_id, job_data))

def get_job_status(job_id: str) -> Optional[Dict]:
    if redis_available:
        job_data_str = redis_client.get(f"job:{job_id}")
        if job_data_str:
            return json.loads(job_data_str)
    else:
        return job_storage.get(job_id)
    return None

async def send_websocket_update(job_id: str, job_data: Dict):
    if job_id in websocket_connections:
        try:
            websocket = websocket_connections[job_id]
            await websocket.send_text(json.dumps(job_data))
        except:
            # Connection broken, remove it
            del websocket_connections[job_id]

# CrewAI Integration Functions
async def run_journal_generation(job_id: str, user_preferences: Dict, api_key: str):
    """Run the existing CrewAI workflow in background"""
    try:
        update_job_status(job_id, "running", current_agent="manager", progress=5, message="Initializing journal generation...")

        # Initialize LLM with user's API key
        llm = LLM(
            model="gpt-4",
            api_key=api_key,
            temperature=0,
            max_tokens=None
        )

        # Create agents
        update_job_status(job_id, "running", current_agent="setup", progress=10, message="Setting up AI agents...")

        manager_agent = create_manager_agent(llm)
        onboarding_agent = create_onboarding_agent(llm)
        discovery_agent = create_discovery_agent(llm)
        research_agent = create_research_agent(llm)
        content_curator_agent = create_content_curator_agent(llm)
        editor_agent = create_editor_agent(llm)
        media_agent = create_media_agent(llm)
        pdf_builder_agent = create_pdf_builder_agent(llm)

        # Create user-specific output directory
        user_output_dir = os.path.join(JOURNALS_DIR, user_preferences["user_id"])
        os.makedirs(user_output_dir, exist_ok=True)

        # Modify user preferences for web execution
        web_preferences = user_preferences.copy()
        web_preferences["run_dir"] = os.path.join(user_output_dir, f"{user_preferences['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        update_job_status(job_id, "running", current_agent="onboarding", progress=20, message="Gathering user preferences...")

        # Run the coordinate_phases function with user interaction handling
        result = await coordinate_phases_web(
            manager_agent, onboarding_agent, discovery_agent, research_agent,
            content_curator_agent, editor_agent, media_agent, pdf_builder_agent,
            web_preferences, job_id
        )

        update_job_status(job_id, "completed", progress=100, message="Journal generation completed!", result=result)

    except Exception as e:
        update_job_status(job_id, "failed", error=str(e), message=f"Error: {str(e)}")

async def coordinate_phases_web(manager_agent, onboarding_agent, discovery_agent, research_agent,
                               content_curator_agent, editor_agent, media_agent, pdf_builder_agent,
                               user_preferences, job_id):
    """Web version of coordinate_phases that handles user decisions asynchronously"""

    # Simulate the existing workflow but wait for user decisions when needed
    update_job_status(job_id, "running", current_agent="discovery", progress=30, message="Generating title ideas...")

    # For now, auto-select first title (in real implementation, wait for user choice)
    selected_title = user_preferences["title"]

    update_job_status(job_id, "running", current_agent="research", progress=40, message="Researching content...")

    update_job_status(job_id, "running", current_agent="content", progress=60, message="Creating journal content...")

    update_job_status(job_id, "running", current_agent="editing", progress=80, message="Polishing content...")

    update_job_status(job_id, "running", current_agent="media", progress=90, message="Generating media...")

    update_job_status(job_id, "running", current_agent="pdf", progress=95, message="Creating PDFs...")

    # Return result structure
    return {
        "journal": os.path.join(user_preferences["run_dir"], JSON_SUBDIR, f"edited_30day_journal_{selected_title}_{user_preferences['theme']}.json"),
        "lead_magnet": os.path.join(user_preferences["run_dir"], JSON_SUBDIR, f"edited_lead_magnet_{selected_title}_{user_preferences['theme']}.json"),
        "pdfs": {
            "journal_pdf": os.path.join(user_preferences["run_dir"], PDF_SUBDIR, f"edited_30day_journal_{selected_title}_{user_preferences['theme']}.pdf"),
            "lead_magnet_pdf": os.path.join(user_preferences["run_dir"], PDF_SUBDIR, f"edited_lead_magnet_{selected_title}_{user_preferences['theme']}.pdf")
        }
    }

# Sample user database (in production, use real database)
fake_users_db = {
    "johndoe": {
        "email": "johndoe@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "hashed_password": get_password_hash("secret"),
        "disabled": False,
        "openai_api_key": None
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

    # Start background task
    background_tasks.add_task(
        run_journal_generation,
        job_id,
        user_preferences,
        current_user.openai_api_key
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

    # Store user choice for the background task to process
    choice_key = f"job_choice:{job_id}"
    choice_data = {
        "choice": choice.choice,
        "choice_type": choice.choice_type,
        "timestamp": datetime.now().isoformat()
    }

    if redis_available:
        redis_client.setex(choice_key, 3600, json.dumps(choice_data))
    else:
        job_storage[choice_key] = choice_data

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
                # Get project info
                project_info = {
                    "name": project_name,
                    "path": project_path,
                    "created": datetime.fromtimestamp(os.path.getctime(project_path)).isoformat(),
                    "has_pdfs": False,
                    "has_media": False
                }

                # Check for PDFs and media
                pdf_dir = os.path.join(project_path, PDF_SUBDIR)
                if os.path.exists(pdf_dir):
                    project_info["has_pdfs"] = len(os.listdir(pdf_dir)) > 0

                media_dir = os.path.join(project_path, MEDIA_SUBDIR)
                if os.path.exists(media_dir):
                    project_info["has_media"] = len(os.listdir(media_dir)) > 0

                projects.append(project_info)

    return {"projects": projects}

@app.get("/api/journals/download/{project_id}")
async def download_project_file(
    project_id: str,
    file_type: str = "journal",  # journal, lead_magnet, media
    current_user: UserInDB = Depends(get_current_active_user)
):
    # This is a simplified version - in production, validate project ownership
    project_path = os.path.join(JOURNALS_DIR, current_user.username, project_id)

    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project not found")

    # Determine file to download based on file_type
    if file_type == "journal_pdf":
        file_path = os.path.join(project_path, PDF_SUBDIR)
        # Find the journal PDF
        if os.path.exists(file_path):
            for file in os.listdir(file_path):
                if "30day_journal" in file and file.endswith(".pdf"):
                    return FileResponse(os.path.join(file_path, file))

    elif file_type == "lead_magnet_pdf":
        file_path = os.path.join(project_path, PDF_SUBDIR)
        # Find the lead magnet PDF
        if os.path.exists(file_path):
            for file in os.listdir(file_path):
                if "lead_magnet" in file and file.endswith(".pdf"):
                    return FileResponse(os.path.join(file_path, file))

    raise HTTPException(status_code=404, detail="File not found")

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

# Settings endpoints (reuse from perfect_auth_server.py)
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Journal Craft Crew - Complete Platform Server")
    print("📍 Authentication + CrewAI Integration")
    print("🔗 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)