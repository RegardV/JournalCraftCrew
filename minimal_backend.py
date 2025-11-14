#!/usr/bin/env python3
"""
Minimal Backend for Journal Craft Crew
Provides basic API endpoints to support frontend functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from datetime import datetime
from typing import Dict, List, Any
import os

app = FastAPI(title="Journal Craft Crew - Minimal API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000", "http://localhost:5100"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load existing data
DATA_FILE = "unified_data.json"
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"users": [], "projects": [], "journals": []}

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass

# Global data store
data_store = load_data()

@app.get("/")
async def root():
    return {"message": "Journal Craft Crew API", "status": "running", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "journal-platform-unified-api",
        "timestamp": datetime.now().isoformat(),
        "data_file": DATA_FILE,
        "users_count": len(data_store.get("users", [])),
        "projects_count": len(data_store.get("projects", []))
    }

@app.get("/api/library/llm-projects")
async def get_llm_projects():
    """Return list of LLM projects"""
    return {
        "projects": [
            {
                "id": "mindfulness-journal-1",
                "title": "30-Day Mindfulness Journey",
                "description": "A comprehensive mindfulness journal with daily prompts and reflections",
                "status": "completed",
                "progress": 100,
                "created_at": "2025-11-14T10:00:00Z",
                "word_count": "15,000",
                "files": []
            },
            {
                "id": "productivity-mastery-2",
                "title": "Productivity Mastery Journal",
                "description": "Boost your productivity with proven strategies and daily tracking",
                "status": "in_progress",
                "progress": 65,
                "created_at": "2025-11-14T09:30:00Z",
                "word_count": "8,500",
                "files": []
            }
        ]
    }

@app.get("/api/settings/api-key")
async def get_api_key():
    """Return API key status"""
    return {
        "has_key": False,
        "masked_key": None,
        "status": "no_key"
    }

@app.post("/api/settings/api-key")
async def save_api_key(request: dict):
    """Save API key"""
    return {
        "status": "success",
        "message": "API key saved successfully"
    }

@app.get("/api/ai/themes")
async def get_themes():
    """Return available journal themes"""
    return {
        "themes": [
            {"id": "mindfulness", "name": "Mindfulness", "description": "Daily mindfulness and meditation"},
            {"id": "productivity", "name": "Productivity", "description": "Boost productivity and focus"},
            {"id": "creativity", "name": "Creativity", "description": "Unlock creative potential"},
            {"id": "gratitude", "name": "Gratitude", "description": "Practice daily gratitude"},
            {"id": "fitness", "name": "Fitness", "description": "Track health and wellness goals"},
            {"id": "learning", "name": "Learning", "description": "Document learning journey"},
            {"id": "relationships", "name": "Relationships", "description": "Improve personal connections"},
            {"id": "finance", "name": "Finance", "description": "Financial goals and tracking"}
        ]
    }

@app.get("/api/ai/title-styles")
async def get_title_styles():
    """Return title styles"""
    return {
        "styles": [
            {"id": "professional", "name": "Professional", "examples": ["Executive Daily Planner", "Professional Growth Journal"]},
            {"id": "creative", "name": "Creative", "examples": ["Canvas of Thoughts", "Creative Unfolding"]},
            {"id": "minimalist", "name": "Minimalist", "examples": ["Daily", "Simply", "Focus"]},
            {"id": "inspirational", "name": "Inspirational", "examples": ["Rise & Shine", "Dream Catcher", "Aspire"]}
        ]
    }

@app.post("/api/journals/create")
async def create_journal(request: dict):
    """Create a new journal"""
    journal_id = f"journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return {
        "id": journal_id,
        "status": "started",
        "message": "Journal creation started successfully",
        "job_id": f"job_{journal_id}"
    }

@app.post("/api/crewai/start-workflow")
async def start_crewai_workflow(request: dict):
    """Start CrewAI workflow"""
    workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return {
        "workflow_id": workflow_id,
        "status": "started",
        "message": "CrewAI workflow started",
        "agents": ["Onboarding Agent", "Research Agent", "Content Curator", "Media Generator"]
    }

# Authentication endpoints - CRITICAL FOR FRONTEND FUNCTIONALITY
@app.post("/api/auth/login")
async def login_user(credentials: dict):
    """Handle user login - Development mode"""
    email = credentials.get("email", "dev@example.com")
    password = credentials.get("password", "devpassword")

    # Development mode - accept any credentials
    # Create a proper JWT-like token for frontend compatibility
    import base64
    import json

    # Create JWT-like token with proper structure (header.payload.signature)
    header = base64.b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode()
    payload_data = {
        "sub": "dev_user_123",
        "user_id": "dev_user_123",
        "email": email,
        "full_name": "Development User",
        "profile_type": "personal_journaler",
        "subscription": "free",
        "library_access": True,
        "is_verified": True,
        "has_openai_key": False,
        "exp": int((datetime.now().timestamp() + 3600 * 24))  # 24 hours from now
    }
    payload = base64.b64encode(json.dumps(payload_data).encode()).decode()
    signature = "dev_signature_12345"  # Fake signature for development

    jwt_token = f"{header}.{payload}.{signature}"

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "refresh_token": "dev_refresh_token_12345",
        "user": {
            "id": "dev_user_123",
            "email": email,
            "full_name": "Development User",
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
    }

@app.post("/api/auth/register")
async def register_user(user_data: dict):
    """Handle user registration - Development mode"""
    email = user_data.get("email", "newuser@example.com")
    password = user_data.get("password", "newpassword")
    full_name = user_data.get("full_name", "New User")

    # Development mode - accept any registration
    user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Create JWT-like token for frontend compatibility
    import base64
    import json

    header = base64.b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode()
    payload_data = {
        "sub": user_id,
        "user_id": user_id,
        "email": email,
        "full_name": full_name,
        "profile_type": "personal_journaler",
        "subscription": "free",
        "library_access": True,
        "is_verified": True,
        "has_openai_key": False,
        "exp": int((datetime.now().timestamp() + 3600 * 24))  # 24 hours from now
    }
    payload = base64.b64encode(json.dumps(payload_data).encode()).decode()
    signature = "dev_signature_12345"

    jwt_token = f"{header}.{payload}.{signature}"

    return {
        "message": "User registered successfully",
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
    }

@app.get("/api/auth/me")
async def get_current_user():
    """Get current user info - Development mode"""
    return {
        "id": "dev_user_123",
        "email": "dev@example.com",
        "full_name": "Development User",
        "created_at": datetime.now().isoformat(),
        "is_active": True,
        "preferences": {}
    }

@app.post("/api/auth/logout")
async def logout_user():
    """Handle user logout - Development mode"""
    return {
        "message": "Logged out successfully"
    }

@app.post("/api/auth/refresh")
async def refresh_token(request: dict):
    """Refresh access token - Development mode"""
    return {
        "access_token": "new_dev_token_12345",
        "token_type": "bearer",
        "expires_in": 3600
    }

@app.get("/api/auth/providers")
async def get_auth_providers():
    """Get available authentication providers"""
    return {
        "providers": [
            {"id": "email", "name": "Email/Password", "enabled": True},
            {"id": "google", "name": "Google", "enabled": False},
            {"id": "apple", "name": "Apple", "enabled": False}
        ]
    }

@app.get("/api/crewai/active-workflows")
async def get_active_workflows():
    """Get active CrewAI workflows"""
    return {
        "workflows": [],
        "total": 0
    }

# WebSocket support for progress tracking
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

    async def send_message(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except:
                # Connection probably closed
                self.disconnect(connection_id)

manager = ConnectionManager()

@app.websocket("/ws/job/{job_id}")
async def websocket_job_updates(websocket: WebSocket, job_id: str):
    connection_id = f"job_{job_id}"
    await manager.connect(websocket, connection_id)

    try:
        # Send initial message
        await manager.send_message(connection_id, {
            "type": "connection",
            "status": "connected",
            "job_id": job_id,
            "message": "Connected to job progress updates"
        })

        # Simulate progress updates
        progress_messages = [
            {"type": "agent_start", "agent": "Onboarding Agent", "progress": 10, "message": "Processing your preferences"},
            {"type": "agent_thinking", "agent": "Research Agent", "thinking": "Researching best content for your theme"},
            {"type": "agent_output", "agent": "Content Curator", "progress": 45, "output": "Curated journal structure ready"},
            {"type": "sequence_update", "current_stage": "Media Generation", "progress": 75, "message": "Creating visual elements"},
            {"type": "completion", "status": "completed", "progress": 100, "message": "Journal created successfully!"}
        ]

        for i, msg in enumerate(progress_messages):
            await asyncio.sleep(2)  # Simulate work
            await manager.send_message(connection_id, msg)

        # Keep connection alive for a bit
        await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(connection_id)

@app.websocket("/ws/journal/{journal_id}")
async def websocket_journal_updates(websocket: WebSocket, journal_id: str):
    connection_id = f"journal_{journal_id}"
    await manager.connect(websocket, connection_id)

    try:
        await manager.send_message(connection_id, {
            "type": "connection",
            "status": "connected",
            "journal_id": journal_id,
            "message": "Connected to journal progress updates"
        })

        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            await manager.send_message(connection_id, {
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            })

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(connection_id)

if __name__ == "__main__":
    import uvicorn
    import sys

    # Allow port to be specified as command line argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    print(f"🚀 Starting Minimal Backend for Journal Craft Crew")
    print(f"📍 Server will be available at: http://localhost:{port}")
    print(f"📖 API docs: http://localhost:{port}/docs")
    print(f"🔍 Health check: http://localhost:{port}/health")

    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)