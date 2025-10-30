#!/usr/bin/env python3
"""
Simplified FastAPI Test Server
Minimal dependencies to avoid installation issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create minimal FastAPI app
app = FastAPI(
    title="Journal Platform Test Server",
    description="Minimal server for testing API endpoints"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic test endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "journal-platform-api-test",
        "timestamp": "2025-10-27T10:15:00Z"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Journal Platform API Test Server is running",
        "test_mode": True,
        "available_endpoints": {
            "health": "/health",
            "register_test": "/test/register",
            "echo_test": "/test/echo"
        }
    }

@app.post("/test/register")
async def test_register():
    """Test registration endpoint"""
    return {
        "success": True,
        "message": "Test registration endpoint working"
    }

@app.post("/test/echo")
async def test_echo():
    """Test echo endpoint"""
    return {"message": "Test endpoint working"}

if __name__ == "__main__":
    import uvicorn
    print("🧪 Starting Minimal FastAPI Test Server")
    print("📍 Server: http://localhost:8001")
    print("📋 Health Check: http://localhost:8001/health")
    print("📋 Frontend should connect to: http://localhost:5173")
    print("🚀 Test with: curl http://localhost:8001/test/echo -X POST -d '{\"test\": \"hello\"}'")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )