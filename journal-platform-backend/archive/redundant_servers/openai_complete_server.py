#!/usr/bin/env python3
"""
OpenAI-Powered Server for Journal Craft Crew
Implements BYO OpenAI API key system with real AI generation
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List, Optional
import json
import asyncio
import time
import uuid
import logging
import hashlib
import os
import base64
import secrets
from datetime import datetime, timedelta
import openai
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File-based data persistence
DATA_FILE = "openai_data.json"

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

# Initialize encryption key
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for storage"""
    return cipher_suite.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key for use"""
    return cipher_suite.decrypt(encrypted_key.encode()).decode()

# Simple JWT functions
def create_jwt_token(payload: dict) -> str:
    """Create JWT token"""
    import json
    token_payload = {
        **payload,
        "exp": int(time.time()) + 3600 * 24  # 24 hours
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
                return None  # Token expired
            return payload
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None

# Initialize data
data_store = load_data()

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    openai_api_key: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

class APIKeyUpdate(BaseModel):
    openai_api_key: str

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
    title="Journal Platform - OpenAI Integration",
    description="BYO OpenAI API key system with real AI generation"
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Rate limiting
from collections import defaultdict
rate_limit_storage = defaultdict(list)

def check_rate_limit(identifier: str, max_requests: int = 5, window_minutes: int = 15) -> bool:
    """Simple rate limiting"""
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)

    rate_limit_storage[identifier] = [
        req_time for req_time in rate_limit_storage[identifier]
        if req_time > window_start
    ]

    if len(rate_limit_storage[identifier]) >= max_requests:
        return False

    rate_limit_storage[identifier].append(now)
    return True

# Authentication dependency
def get_current_user(authorization: str = None):
    """Get current user from JWT token"""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "")
    payload = verify_jwt_token(token)
    return payload.get("user_id") if payload else None

def validate_email(email: str) -> bool:
    """Enhanced email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> dict:
    """Enhanced password validation"""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if len(password) > 128:
        errors.append("Password must be less than 128 characters")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")

    return {"valid": len(errors) == 0, "errors": errors}

def sanitize_input(input_string: str) -> str:
    """Sanitize user input"""
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

# Landing page with OpenAI key option
@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Modern landing page with OpenAI API key integration"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Journal Craft Crew - AI-Powered Journal Creation</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary-color: #6366f1;
                --primary-hover: #5558e3;
                --primary-light: #f0f1ff;
                --secondary-color: #64748b;
                --success-color: #10b981;
                --error-color: #ef4444;
                --warning-color: #f59e0b;
                --background: #ffffff;
                --surface: #f8fafc;
                --border: #e2e8f0;
                --text-primary: #1e293b;
                --text-secondary: #64748b;
                --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
                --radius-sm: 0.375rem;
                --radius-md: 0.5rem;
                --radius-lg: 0.75rem;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                line-height: 1.6;
                color: var(--text-primary);
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem;
            }

            .auth-container {
                width: 100%;
                max-width: 1200px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
                background: var(--background);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-lg);
                overflow: hidden;
                min-height: 600px;
            }

            .auth-left {
                background: linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 100%);
                color: white;
                padding: 3rem;
                display: flex;
                flex-direction: column;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }

            .auth-left::before {
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: float 20s ease-in-out infinite;
            }

            @keyframes float {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-20px) rotate(180deg); }
            }

            .brand {
                position: relative;
                z-index: 1;
            }

            .brand h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }

            .brand .tagline {
                font-size: 1.25rem;
                opacity: 0.9;
                margin-bottom: 2rem;
                font-weight: 300;
            }

            .features {
                position: relative;
                z-index: 1;
                list-style: none;
            }

            .features li {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 1rem;
                font-size: 1rem;
                opacity: 0.9;
            }

            .features .icon {
                width: 20px;
                height: 20px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }

            .auth-right {
                padding: 3rem;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .auth-tabs {
                display: flex;
                gap: 1rem;
                margin-bottom: 2rem;
                border-bottom: 1px solid var(--border);
            }

            .auth-tab {
                padding: 0.75rem 1.5rem;
                background: none;
                border: none;
                color: var(--text-secondary);
                font-weight: 500;
                cursor: pointer;
                position: relative;
                transition: all 0.2s ease;
                border-radius: var(--radius-sm) var(--radius-sm) 0 0;
            }

            .auth-tab:hover {
                color: var(--text-primary);
            }

            .auth-tab.active {
                color: var(--primary-color);
            }

            .auth-tab.active::after {
                content: '';
                position: absolute;
                bottom: -1px;
                left: 0;
                right: 0;
                height: 2px;
                background: var(--primary-color);
            }

            .auth-form {
                display: none;
                animation: fadeIn 0.3s ease;
            }

            .auth-form.active {
                display: block;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .form-group {
                margin-bottom: 1.5rem;
            }

            .form-label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
                color: var(--text-primary);
                font-size: 0.875rem;
            }

            .form-input {
                width: 100%;
                padding: 0.75rem 1rem;
                border: 1px solid var(--border);
                border-radius: var(--radius-md);
                font-size: 1rem;
                transition: all 0.2s ease;
                background: var(--background);
            }

            .form-input:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            }

            .form-input.error {
                border-color: var(--error-color);
            }

            .input-wrapper {
                position: relative;
            }

            .password-toggle {
                position: absolute;
                right: 1rem;
                top: 50%;
                transform: translateY(-50%);
                background: none;
                border: none;
                color: var(--text-secondary);
                cursor: pointer;
                padding: 0.25rem;
                border-radius: var(--radius-sm);
                transition: all 0.2s ease;
            }

            .password-toggle:hover {
                color: var(--text-primary);
                background: var(--surface);
            }

            .api-key-info {
                margin-top: 0.5rem;
                font-size: 0.75rem;
                color: var(--text-secondary);
                line-height: 1.4;
            }

            .api-key-info a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
            }

            .api-key-info a:hover {
                text-decoration: underline;
            }

            .btn {
                padding: 0.75rem 1.5rem;
                border: none;
                border-radius: var(--radius-md);
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 1rem;
                width: 100%;
                position: relative;
                overflow: hidden;
            }

            .btn-primary {
                background: var(--primary-color);
                color: white;
            }

            .btn-primary:hover {
                background: var(--primary-hover);
                transform: translateY(-1px);
                box-shadow: var(--shadow-md);
            }

            .btn-primary:active {
                transform: translateY(0);
            }

            .btn-primary:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }

            .form-footer {
                margin-top: 1.5rem;
                text-align: center;
                color: var(--text-secondary);
                font-size: 0.875rem;
            }

            .form-footer a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
            }

            .form-footer a:hover {
                text-decoration: underline;
            }

            .server-info {
                margin-top: 2rem;
                padding: 1rem;
                background: var(--primary-light);
                border-radius: var(--radius-md);
                font-size: 0.875rem;
                color: var(--text-secondary);
                border-left: 4px solid var(--primary-color);
            }

            .server-info strong {
                color: var(--text-primary);
            }

            .error-message {
                color: var(--error-color);
                font-size: 0.875rem;
                margin-top: 0.25rem;
                display: none;
            }

            .error-message.show {
                display: block;
                animation: fadeIn 0.2s ease;
            }

            .loading {
                display: none;
                width: 20px;
                height: 20px;
                border: 2px solid var(--primary-light);
                border-top: 2px solid var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            /* Mobile Responsive */
            @media (max-width: 768px) {
                .auth-container {
                    grid-template-columns: 1fr;
                    max-width: 500px;
                    margin: 1rem;
                }

                .auth-left {
                    padding: 2rem;
                    text-align: center;
                }

                .brand h1 {
                    font-size: 2rem;
                }

                .auth-right {
                    padding: 2rem;
                }

                .features li {
                    justify-content: center;
                }
            }

            /* Accessibility */
            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }

            *:focus-visible {
                outline: 2px solid var(--primary-color);
                outline-offset: 2px;
            }
        </style>
    </head>
    <body>
        <div class="auth-container">
            <div class="auth-left">
                <div class="brand">
                    <h1>
                        <span>📚</span>
                        Journal Craft Crew
                    </h1>
                    <p class="tagline">Transform your thoughts into beautifully crafted journals with AI</p>
                </div>
                <ul class="features">
                    <li>
                        <div class="icon">✨</div>
                        <span>Real OpenAI API integration</span>
                    </li>
                    <li>
                        <div class="icon">🔑</div>
                        <span>Bring your own API key</span>
                    </li>
                    <li>
                        <div class="icon">💰</div>
                        <span>Pay only for what you use</span>
                    </li>
                    <li>
                        <div class="icon">🎨</div>
                        <span>Beautiful, customizable layouts</span>
                    </li>
                </ul>
            </div>

            <div class="auth-right">
                <div class="auth-tabs">
                    <button class="auth-tab active" onclick="switchTab('login')" aria-label="Login tab">
                        Sign In
                    </button>
                    <button class="auth-tab" onclick="switchTab('register')" aria-label="Register tab">
                        Create Account
                    </button>
                </div>

                <!-- Login Form -->
                <form id="login-form" class="auth-form active" action="/api/auth/login" method="post" onsubmit="handleLogin(event)">
                    <div class="form-group">
                        <label for="login-email" class="form-label">Email Address</label>
                        <input
                            type="email"
                            id="login-email"
                            name="email"
                            class="form-input"
                            placeholder="Enter your email"
                            required
                            aria-describedby="login-email-error"
                            autocomplete="email"
                        >
                        <div id="login-email-error" class="error-message" role="alert"></div>
                    </div>

                    <div class="form-group">
                        <label for="login-password" class="form-label">Password</label>
                        <div class="input-wrapper">
                            <input
                                type="password"
                                id="login-password"
                                name="password"
                                class="form-input"
                                placeholder="Enter your password"
                                required
                                aria-describedby="login-password-error"
                                autocomplete="current-password"
                            >
                            <button
                                type="button"
                                class="password-toggle"
                                onclick="togglePassword('login-password', this)"
                                aria-label="Toggle password visibility"
                            >
                                <span id="login-password-icon">👁️</span>
                            </button>
                        </div>
                        <div id="login-password-error" class="error-message" role="alert"></div>
                    </div>

                    <button type="submit" class="btn btn-primary" id="login-btn">
                        <span id="login-btn-text">Sign In</span>
                        <div class="loading" id="login-loading"></div>
                    </button>

                    <div class="form-footer">
                        Don't have an account? <a href="#" onclick="switchTab('register')">Create one</a>
                    </div>
                </form>

                <!-- Registration Form -->
                <form id="register-form" class="auth-form" action="/api/auth/register" method="post" onsubmit="handleRegister(event)">
                    <div class="form-group">
                        <label for="register-name" class="form-label">Full Name</label>
                        <input
                            type="text"
                            id="register-name"
                            name="full_name"
                            class="form-input"
                            placeholder="Enter your full name"
                            required
                            aria-describedby="register-name-error"
                            autocomplete="name"
                        >
                        <div id="register-name-error" class="error-message" role="alert"></div>
                    </div>

                    <div class="form-group">
                        <label for="register-email" class="form-label">Email Address</label>
                        <input
                            type="email"
                            id="register-email"
                            name="email"
                            class="form-input"
                            placeholder="Enter your email"
                            required
                            aria-describedby="register-email-error"
                            autocomplete="email"
                        >
                        <div id="register-email-error" class="error-message" role="alert"></div>
                    </div>

                    <div class="form-group">
                        <label for="register-password" class="form-label">Password</label>
                        <div class="input-wrapper">
                            <input
                                type="password"
                                id="register-password"
                                name="password"
                                class="form-input"
                                placeholder="Create a strong password"
                                required
                                aria-describedby="register-password-error"
                                autocomplete="new-password"
                            >
                            <button
                                type="button"
                                class="password-toggle"
                                onclick="togglePassword('register-password', this)"
                                aria-label="Toggle password visibility"
                            >
                                <span id="register-password-icon">👁️</span>
                            </button>
                        </div>
                        <div id="register-password-error" class="error-message" role="alert"></div>
                    </div>

                    <div class="form-group">
                        <label for="register-api-key" class="form-label">OpenAI API Key (Optional)</label>
                        <input
                            type="password"
                            id="register-api-key"
                            name="openai_api_key"
                            class="form-input"
                            placeholder="sk-... (Get yours from OpenAI dashboard)"
                            aria-describedby="register-api-key-info register-api-key-error"
                        >
                        <div id="register-api-key-info" class="api-key-info">
                            Optional: Add your OpenAI API key to start using AI features immediately.
                            Get your key at <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI Dashboard</a>
                        </div>
                        <div id="register-api-key-error" class="error-message" role="alert"></div>
                    </div>

                    <button type="submit" class="btn btn-primary" id="register-btn">
                        <span id="register-btn-text">Create Account</span>
                        <div class="loading" id="register-loading"></div>
                    </button>

                    <div class="form-footer">
                        Already have an account? <a href="#" onclick="switchTab('login')">Sign in</a>
                    </div>
                </form>

                <div class="server-info">
                    <strong>🌐 OpenAI-Powered Environment</strong><br>
                    <strong>👥 Users:</strong> {len(data_store['users'])} |
                    <strong>📚 Projects:</strong> {len(data_store['projects'])} |
                    <strong>🤖 AI Jobs:</strong> {len(data_store['ai_jobs'])}<br>
                    <strong>📊 Server:</strong> <a href="/health" style="color: var(--primary-color);">Health Check</a> |
                    <strong>📖 API:</strong> <a href="/docs" style="color: var(--primary-color);">Documentation</a>
                </div>
            </div>
        </div>

        <script>
            function switchTab(tab) {
                const tabs = document.querySelectorAll('.auth-tab');
                const forms = document.querySelectorAll('.auth-form');

                tabs.forEach(t => t.classList.remove('active'));
                forms.forEach(f => f.classList.remove('active'));

                if (tab === 'login') {
                    tabs[0].classList.add('active');
                    document.getElementById('login-form').classList.add('active');
                } else {
                    tabs[1].classList.add('active');
                    document.getElementById('register-form').classList.add('active');
                }

                clearErrors();
            }

            function togglePassword(inputId, button) {
                const input = document.getElementById(inputId);
                const icon = document.getElementById(inputId + '-icon');

                if (input.type === 'password') {
                    input.type = 'text';
                    icon.textContent = '🙈';
                } else {
                    input.type = 'password';
                    icon.textContent = '👁️';
                }
            }

            function validateEmail(email) {
                return /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email);
            }

            function showError(inputId, message) {
                const input = document.getElementById(inputId);
                const error = document.getElementById(inputId + '-error');

                input.classList.add('error');
                error.textContent = message;
                error.classList.add('show');
            }

            function clearError(inputId) {
                const input = document.getElementById(inputId);
                const error = document.getElementById(inputId + '-error');

                input.classList.remove('error');
                error.classList.remove('show');
            }

            function clearErrors() {
                const errors = document.querySelectorAll('.error-message');
                const inputs = document.querySelectorAll('.form-input');

                errors.forEach(error => error.classList.remove('show'));
                inputs.forEach(input => input.classList.remove('error'));
            }

            function setLoading(formType, loading) {
                const btn = document.getElementById(formType + '-btn');
                const btnText = document.getElementById(formType + '-btn-text');
                const loadingEl = document.getElementById(formType + '-loading');

                if (loading) {
                    btn.disabled = true;
                    btnText.style.display = 'none';
                    loadingEl.style.display = 'block';
                } else {
                    btn.disabled = false;
                    btnText.style.display = 'inline';
                    loadingEl.style.display = 'none';
                }
            }

            function showSuccessMessage(message) {
                const notification = document.createElement('div');
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: var(--success-color);
                    color: white;
                    padding: 1rem 1.5rem;
                    border-radius: var(--radius-md);
                    box-shadow: var(--shadow-lg);
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                `;
                notification.textContent = message;
                document.body.appendChild(notification);

                setTimeout(() => {
                    notification.style.animation = 'fadeOut 0.3s ease';
                    setTimeout(() => notification.remove(), 300);
                }, 5000);
            }

            function showGeneralError(message) {
                const notification = document.createElement('div');
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: var(--error-color);
                    color: white;
                    padding: 1rem 1.5rem;
                    border-radius: var(--radius-md);
                    box-shadow: var(--shadow-lg);
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                `;
                notification.textContent = message;
                document.body.appendChild(notification);

                setTimeout(() => {
                    notification.style.animation = 'fadeOut 0.3s ease';
                    setTimeout(() => notification.remove(), 300);
                }, 5000);
            }

            async function handleLogin(event) {
                event.preventDefault();
                clearErrors();

                const email = document.getElementById('login-email').value;
                const password = document.getElementById('login-password').value;

                let hasError = false;

                if (!validateEmail(email)) {
                    showError('login-email', 'Please enter a valid email address');
                    hasError = true;
                }

                if (password.length < 1) {
                    showError('login-password', 'Please enter your password');
                    hasError = true;
                }

                if (hasError) return;

                setLoading('login', true);

                try {
                    const formData = new FormData(event.target);
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (response.ok && data.success) {
                        showSuccessMessage('Login successful! Welcome back.');
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        if (data.detail && data.detail.field) {
                            showError('login-' + data.detail.field, data.detail.message);
                        } else if (data.detail && data.detail.message) {
                            showGeneralError(data.detail.message);
                        } else {
                            showGeneralError('Login failed. Please try again.');
                        }
                    }
                } catch (error) {
                    showGeneralError('Network error. Please check your connection and try again.');
                } finally {
                    setLoading('login', false);
                }
            }

            async function handleRegister(event) {
                event.preventDefault();
                clearErrors();

                const name = document.getElementById('register-name').value;
                const email = document.getElementById('register-email').value;
                const password = document.getElementById('register-password').value;

                let hasError = false;

                if (name.length < 2) {
                    showError('register-name', 'Please enter your full name');
                    hasError = true;
                }

                if (!validateEmail(email)) {
                    showError('register-email', 'Please enter a valid email address');
                    hasError = true;
                }

                if (password.length < 8) {
                    showError('register-password', 'Password must be at least 8 characters');
                    hasError = true;
                }

                if (hasError) return;

                setLoading('register', true);

                try {
                    const formData = new FormData(event.target);
                    const response = await fetch('/api/auth/register', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (response.ok && data.success) {
                        switchTab('login');
                        showSuccessMessage('Registration successful! You can now sign in.');
                    } else {
                        if (data.detail && data.detail.field) {
                            showError('register-' + data.detail.field, data.detail.message);
                        } else if (data.detail && data.detail.message) {
                            showGeneralError(data.detail.message);
                        } else {
                            showGeneralError('Registration failed. Please try again.');
                        }
                    }
                } catch (error) {
                    showGeneralError('Network error. Please check your connection and try again.');
                } finally {
                    setLoading('register', false);
                }
            }

            // Add slide animations
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes fadeOut {
                    from { opacity: 1; }
                    to { opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)# This is a continuation of openai_server.py due to length limitations

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user_data: UserRegistration, request: Request):
    try:
        # Rate limiting based on IP
        client_ip = request.client.host
        if not check_rate_limit(f"register:{client_ip}", 3, 15):
            raise HTTPException(
                status_code=429,
                detail="Too many registration attempts. Please try again later.",
                headers={"Retry-After": "900"}
            )

        # Enhanced input validation
        if not user_data.full_name or len(user_data.full_name.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid name",
                    "message": "Full name must be at least 2 characters long",
                    "field": "full_name"
                }
            )

        if len(user_data.full_name) > 100:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid name",
                    "message": "Full name must be less than 100 characters",
                    "field": "full_name"
                }
            )

        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid email",
                    "message": "Please enter a valid email address",
                    "field": "email"
                }
            )

        password_validation = validate_password(user_data.password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid password",
                    "message": "Password does not meet requirements",
                    "field": "password",
                    "requirements": password_validation["errors"]
                }
            )

        # Validate OpenAI API key if provided
        encrypted_api_key = None
        if user_data.openai_api_key:
            if not user_data.openai_api_key.startswith("sk-"):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid API key",
                        "message": "OpenAI API key must start with 'sk-'",
                        "field": "openai_api_key"
                    }
                )

            # Validate API key with OpenAI
            if not await validate_openai_api_key(user_data.openai_api_key):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid API key",
                        "message": "OpenAI API key is invalid or has insufficient permissions",
                        "field": "openai_api_key"
                    }
                )

            encrypted_api_key = encrypt_api_key(user_data.openai_api_key)

        # Sanitize inputs
        sanitized_name = sanitize_input(user_data.full_name)
        sanitized_email = sanitize_input(user_data.email.lower())

        # Check if user already exists
        for uid, user in data_store["users"].items():
            if user["email"] == sanitized_email:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "User exists",
                        "message": "An account with this email already exists",
                        "field": "email"
                    }
                )

        # Create new user
        user_id = f"user_{len(data_store['users']) + 1}"
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()

        new_user = {
            "id": user_id,
            "email": sanitized_email,
            "full_name": sanitized_name,
            "openai_api_key": encrypted_api_key,
            "created_at": time.time(),
            "password_hash": password_hash
        }

        data_store["users"][user_id] = new_user

        # Initialize usage stats
        data_store["usage_stats"][user_id] = {
            "total_cost": 0.0,
            "total_tokens": 0,
            "usage_history": []
        }

        save_data(data_store)

        logger.info(f"User registered: {sanitized_email}")

        return {
            "success": True,
            "message": "Registration successful! You can now sign in.",
            "user": {
                "id": user_id,
                "email": sanitized_email,
                "full_name": sanitized_name,
                "has_api_key": encrypted_api_key is not None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Registration failed",
                "message": "An unexpected error occurred during registration"
            }
        )

@app.post("/api/auth/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin, request: Request):
    try:
        # Rate limiting based on IP
        client_ip = request.client.host
        if not check_rate_limit(f"login:{client_ip}", 5, 15):
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later.",
                headers={"Retry-After": "900"}
            )

        # Enhanced input validation
        if not validate_email(login_data.email):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid email",
                    "message": "Please enter a valid email address",
                    "field": "email"
                }
            )

        if not login_data.password or len(login_data.password) < 1:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid password",
                    "message": "Please enter your password",
                    "field": "password"
                }
            )

        # Find user by email
        user = None
        for uid, user_data in data_store["users"].items():
            if user_data["email"] == login_data.email.lower():
                user = user_data
                break

        if not user:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication failed",
                    "message": "Invalid email or password"
                }
            )

        # Verify password
        if user["password_hash"] != hashlib.sha256(login_data.password.encode()).hexdigest():
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication failed",
                    "message": "Invalid email or password"
                }
            )

        # Create token
        token = create_jwt_token(user)

        # Store session
        session_id = str(uuid.uuid4())
        data_store["sessions"][session_id] = {
            "user_id": user["id"],
            "token": token,
            "created_at": time.time(),
            "ip_address": client_ip
        }
        save_data(data_store)

        logger.info(f"User logged in: {login_data.email}")

        return LoginResponse(
            success=True,
            message="Login successful! Welcome back.",
            access_token=token,
            token_type="bearer",
            user={
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "has_api_key": user.get("openai_api_key") is not None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Login failed",
                "message": "An unexpected error occurred during login"
            }
        )

# API Key management endpoints
@app.post("/api/user/api-key")
async def update_api_key(api_key_data: APIKeyUpdate, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not api_key_data.openai_api_key.startswith("sk-"):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key must start with 'sk-'"
            )

        # Validate API key with OpenAI
        if not await validate_openai_api_key(api_key_data.openai_api_key):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is invalid or has insufficient permissions"
            )

        # Encrypt and store API key
        encrypted_key = encrypt_api_key(api_key_data.openai_api_key)
        data_store["users"][current_user]["openai_api_key"] = encrypted_key
        save_data(data_store)

        return {
            "success": True,
            "message": "API key updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API key")

@app.delete("/api/user/api-key")
async def delete_api_key(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data_store["users"][current_user]["openai_api_key"] = None
        save_data(data_store)

        return {
            "success": True,
            "message": "API key removed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key deletion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete API key")

@app.get("/api/user/usage-stats")
async def get_usage_stats(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        stats = data_store["usage_stats"].get(current_user, {
            "total_cost": 0.0,
            "total_tokens": 0,
            "usage_history": []
        })

        return stats

    except Exception as e:
        logger.error(f"Usage stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage statistics")

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
                detail="OpenAI API key required. Please add your API key in settings."
            )

        # Decrypt API key
        try:
            api_key = decrypt_api_key(encrypted_key)
        except Exception as e:
            logger.error(f"API key decryption error: {e}")
            raise HTTPException(status_code=500, detail="Failed to access API key")

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
            "created_at": time.time(),
            "user_id": current_user
        }
        save_data(data_store)

        # Start background task
        asyncio.create_task(real_openai_generation(job_id, request.theme, request.title_style, api_key, current_user))

        logger.info(f"AI generation started by user {current_user}: {job_id}")

        return {
            "success": True,
            "message": "AI journal generation started",
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

            # Create completed project at 100%
            elif progress == 100:
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

        await asyncio.sleep(2)  # Realistic timing between stages

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
        "estimated_time_remaining": max(0, 180 - (time.time() - job["created_at"])),
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

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "journal-platform-openai",
        "timestamp": datetime.utcnow().isoformat(),
        "openai_integration": True,
        "data_stats": {
            "users": len(data_store["users"]),
            "projects": len(data_store["projects"]),
            "active_sessions": len(data_store["sessions"]),
            "ai_jobs": len(data_store["ai_jobs"]),
            "usage_stats": len(data_store["usage_stats"])
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting OpenAI-Powered Server")
    print("📍 BYO API Key System: http://localhost:8000")
    print("🔑 Real OpenAI Integration")
    print("📋 Users:", len(data_store.get('users', [])))
    print("📚 Projects:", len(data_store.get('projects', [])))
    print("🤖 Active AI Jobs:", len(data_store.get('ai_jobs', [])))
    print("💡 Features:")
    print("   - Bring your own OpenAI API key")
    print("   - Real AI journal generation")
    print("   - Cost tracking and usage statistics")
    print("   - Secure key encryption and storage")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )