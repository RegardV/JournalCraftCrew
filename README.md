<div align="center">

# 🚀 Journal Craft Crew

**AI-Powered Journal Creation Platform with Multi-Agent Intelligence**

[![License: Commercial](https://img.shields.io/badge/License-Commercial%20Revenue%20Share-green.svg)](./LICENSE)
[![Platform Status](https://img.shields.io/badge/Platform-Production%20Ready-green.svg)](https://github.com/RegardV/JournalCraftCrew)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![React Version](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org)

*A sophisticated AI-driven platform that transforms your ideas into beautifully crafted journals using advanced CrewAI technology and 19 specialized AI agents.*

![Journal Craft Crew Banner](https://storage.googleapis.com/msgsndr/IrMcgCngseyAip8tcgDm/media/68fb59aa9b2f636d8d1ec31b.jpeg)

## 🎯 Current Status: Production Ready & Commercial Monetization Ready

**Platform Foundation:** ✅ 100% Complete - Production-ready with enterprise-grade security
**Backend:** ✅ Fully operational with real LLM integration
**Frontend:** ✅ Professional responsive interface with Firebase authentication
**API:** ✅ All endpoints serving real data with comprehensive error handling
**Security:** ✅ Enterprise-grade security with rate limiting and validation
**Performance:** ✅ Optimized with caching and monitoring
**Monetization:** 🔄 Commercial infrastructure ready for Stripe integration

</div>

## 📖 Table of Contents

- [✨ Features](#-features)
- [🚀 Installation Guide](#-installation-guide)
- [🔧 Claude Code Setup](#-claude-code-setup)
- [👥 Development Agent Team](#-development-agent-team)
- [🔐 Firebase Authentication](#-firebase-authentication)
- [🛠️ Platform Deployment](#-platform-deployment)
- [🏗️ Architecture](#-architecture)
- [📚 API Documentation](#-api-documentation)
- [🧪 Development](#-development)
- [💰 Pricing](#-pricing)
- [📊 Platform Status](#-platform-status)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

### 🤖 AI-Powered Journal Creation
- **19-Agent AI System**: Multi-layer architecture with specialized CrewAI agents
- **3-Part Psychological Progression**: Identify → Document → Action framework
- **Real-time Progress Tracking**: WebSocket-based live progress visualization
- **Professional Themes**: Extensive collection of customizable journal themes
- **Content Library**: Secure storage and management of created journals

### 🔒 Enterprise-Grade Security & Authentication
- **Firebase Authentication**: Built-in support for Google, Apple, email/password authentication
- **JWT Token Management**: Secure session handling with refresh tokens
- **Rate Limiting**: Protection against abuse with configurable limits
- **Input Validation**: Comprehensive validation and sanitization of all inputs
- **Security Headers**: Complete security header implementation
- **XSS/SQL Injection Protection**: Advanced threat detection and prevention

### ⚡ High Performance
- **Zero Vulnerability Deployment**: 43 → 0 vulnerabilities eliminated
- **UV Dependency Management**: Modern Python dependency management
- **Optimized Caching**: Intelligent response caching with TTL support
- **Request Deduplication**: Prevent duplicate API calls
- **Performance Monitoring**: Real-time metrics and monitoring dashboard
- **Lazy Loading**: Optimized component and resource loading

### 🎨 Professional User Experience
- **Responsive Design**: Mobile-first responsive interface
- **Real-time Updates**: WebSocket-powered live updates
- **Intuitive Navigation**: Complete user flow from registration to library access
- **Error Handling**: Comprehensive error recovery and user feedback
- **Accessibility**: WCAG compliant design and navigation

---

## 🚀 Installation Guide

### 🔧 System Requirements
- **Node.js**: 18.0+ (for frontend development)
- **Python**: 3.12+ (for backend development)
- **Operating System**: Linux, macOS, or Windows (with WSL2)
- **Memory**: 8GB+ RAM recommended
- **Storage**: 10GB+ free disk space

### ⚡ Quick Setup (Recommended)

**Step 1: Clone Repository**
```bash
git clone https://github.com/RegardV/JournalCraftCrew.git
cd JournalCraftCrew
```

**Step 2: Run Universal Setup Script**
```bash
# Automatic setup for any environment
./setup-platform.sh

# Or specify environment explicitly:
./setup-platform.sh codespaces     # GitHub Codespaces
./setup-platform.sh production     # Production server
./setup-platform.sh docker         # Docker container
./setup-platform.sh development   # Local development
```

**Step 3: Start Development Servers**
```bash
./start-journal-crew.sh
```

**Step 4: Access the Application**
- **Frontend**: http://localhost:5173
- **Backend API**: https://localhost:6770 (SSL)
- **Dashboard**: http://localhost:6771
- **Agent Overview**: http://localhost:6771/agent-overview

### 🔐 Firebase Authentication Setup

**Step 1: Create Firebase Project**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" and create a new project
3. Enable Authentication from the sidebar
4. Set up your preferred sign-in methods:
   - Email/Password
   - Google
   - Apple
   - Any other OAuth providers

**Step 2: Get Firebase Configuration**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase (if not already done)
firebase login
firebase init
```

**Step 3: Update Environment Variables**
```bash
# Backend: journal-platform-backend/.env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xyz@your-project.iam.gserviceaccount.com

# Frontend: journal-platform-frontend/.env.local
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

### 🌐 Platform Deployment Options

**GitHub Codespaces (Instant Cloud Development)**
```bash
# 1. Go to GitHub repository page
# 2. Click "Code" → "Codespaces" → "Create codespace"
# 3. Setup runs automatically (2-3 minutes)
# 4. Access: https://<codespace-name>-5173.github.dev
```

**Docker Deployment**
```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

**Production Server**
```bash
# AWS, GCP, DigitalOcean, or any cloud server
./setup-platform.sh production --monitoring --backup
```

---

## 🔧 Claude Code Setup

### 📋 Prerequisites
1. **Install Claude Code**: Download from [claude.ai/code](https://claude.ai/code)
2. **GitHub Account**: Required for repository access
3. **OpenSpec Awareness**: Familiarity with OpenSpec methodology

### 🚀 Setup Process

**Step 1: Open Project in Claude Code**
```bash
# Navigate to your project directory
cd /path/to/JournalCraftCrew

# Open project in Claude Code
claude-code .
```

**Step 2: Access OpenSpec Files**
- Open `@/openspec/AGENTS.md` - Main OpenSpec instructions
- Browse `openspec/changes/` - All change proposals and specifications
- Review `openspec/changelog.md` - Complete project evolution history

**Step 3: Access Orchestrator Dashboard**
1. Start the orchestrator dashboard:
   ```bash
   cd orchestrator_dashboard
   source ../orchestrator_venv/bin/activate
   python app.py
   ```

2. Access in browser: http://localhost:6771

**Step 4: Use Development Agent Team**
- See Development Agent Team section below for available agents
- Access agents via the Dev Dashboard or directly through the development assistant API
- Use OpenSpec to propose new changes and track progress

### 🎯 Claude Code Workflow

**For Development:**
1. **Open Project**: `claude-code .`
2. **Review OpenSpec**: `@/openspec/AGENTS.md`
3. **Create Changes**: Use OpenSpec to propose new features
4. **Track Progress**: Monitor through OpenSpec changelog
5. **Run Orchestrator**: Access dev dashboard for project management

**For Proposals:**
```bash
# Create new OpenSpec change
@/openspec/changes/your-feature-name/proposal.md

# Follow OpenSpec methodology for structured proposals
# Include problem statement, solution, and implementation plan
```

---

## 👥 Development Agent Team

### 🤖 Dev Layer Agents (Specialized Development Support)

The Development Agent Team consists of 6 specialized AI agents available through the Development Assistant API and Dashboard:

| Agent | Role | Specialization | Tools & Capabilities | Usage |
|-------|------|----------------|---------------------|-------|
| **Archon Development Assistant** | Knowledge Integration | ArchonServiceClient, knowledge base search, development best practices | `GET /api/dev/archon/ask` <br> Dashboard: Archon tab |
| **File Storage Research Agent** | Storage Solutions | Google Drive, Dropbox, AWS S3, Azure Blob, Cloudinary integration research | `GET /api/dev/storage/research` <br> Dashboard: Storage tab |
| **Authentication Patterns Research Agent** | Security & Auth | Firebase, OAuth 2.0, JWT, SAML, Auth0, Passport.js authentication patterns | `GET /api/dev/auth/research` <br> Dashboard: Auth tab |
| **VPS Deployment Research Agent** | Infrastructure | AWS EC2, Google Cloud, DigitalOcean, Heroku, Netlify deployment strategies | `GET /api/dev/deployment/research` <br> Dashboard: Deployment tab |
| **Architecture Guidance Agent** | System Design | Microservices, monolith, event-driven, CQRS, hexagonal architecture patterns | `GET /api/dev/architecture/guidance` <br> Dashboard: Architecture tab |
| **Implementation Patterns Research Agent** | Code Patterns | Design patterns, SOLID principles, clean code, testing strategies | `GET /api/dev/patterns/research` <br> Dashboard: Patterns tab |

### 🚀 How to Use Development Agents

#### **Via Development Dashboard**
1. Start orchestrator: `./start-journal-crew.sh` (includes dashboard)
2. Access: http://localhost:6771
3. Navigate to "Dev Dashboard" tab
4. Select agent specialization from dropdown
5. Enter your development question or requirement

#### **Via API**
```bash
# Example API calls to development agents
curl -X POST "http://localhost:6771/api/dev/archon/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I implement caching in FastAPI applications?"}'

curl -X POST "http://localhost:6771/api/dev/auth/research" \
  -H "Content-Type: application/json" \
  -d '{"technology": "Firebase authentication best practices"}'

curl -X POST "http://localhost:6771/api/dev/deployment/research" \
  -H "Content-Type: application/json" \
  -d '{"platform": "AWS", "requirements": "scalable Node.js deployment"}'
```

#### **Via OpenSpec**
1. Access OpenSpec: `@/openspec/AGENTS.md`
2. Create new change proposal for development needs
3. Include agent consultation requirements
4. Track implementation through OpenSpec workflow

### 🎯 Agent Integration Examples

**Researching File Storage Solutions:**
```bash
# File Storage Research Agent example
curl -X POST "http://localhost:6771/api/dev/storage/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare AWS S3 vs Google Cloud Storage for user-uploaded journal files",
    "requirements": ["scalability", "cost-effectiveness", "CDN integration"]
  }'
```

**Authentication Pattern Research:**
```bash
# Authentication Patterns Research Agent example
curl -X POST "http://localhost:6771/api/dev/auth/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Implement secure OAuth2.0 with refresh tokens for React frontend",
    "current_stack": "FastAPI backend, React frontend"
  }'
```

**Architecture Guidance:**
```bash
# Architecture Guidance Agent example
curl -X POST "http://localhost:6771/api/dev/architecture/guidance" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Design microservices architecture for AI journal generation platform",
    "constraints": ["high performance", "scalable", "maintainable"]
  }'
```

---

## 🔐 Firebase Authentication

### 🎯 Built-in Authentication Support

Journal Craft Crew includes comprehensive Firebase Authentication integration out of the box:

**Supported Providers:**
- ✅ **Email/Password**: Traditional email and password authentication
- ✅ **Google**: Google OAuth2 integration
- ✅ **Apple**: Apple Sign In (iOS/macOS/web)
- ✅ **Phone**: Phone number authentication with SMS verification
- ✅ **Anonymous**: Anonymous user sessions for testing

### 🔧 Implementation Details

**Frontend Integration:**
```typescript
// Firebase configuration (frontend/src/lib/firebase.ts)
import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { GoogleAuthProvider } from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)

// Google Sign In
const googleProvider = new GoogleAuthProvider()
export const signInWithGoogle = () => signInWithPopup(auth, googleProvider)
```

**Backend Integration:**
```python
# Firebase Admin SDK integration (backend/app/services/firebase_service.py)
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException

class FirebaseService:
    def __init__(self):
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL")
        })
        firebase_admin.initialize_app(cred)
        self.auth = auth

    async def verify_token(self, token: str) -> dict:
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def create_user(self, email: str, password: str):
        user = auth.create_user(
            email=email,
            password=password
        )
        return user
```

### 📱 User Authentication Flow

**Registration Process:**
1. User chooses sign-in method (email, Google, Apple)
2. Firebase handles authentication
3. Token returned to frontend
4. Frontend sends token to backend
5. Backend validates token with Firebase Admin SDK
6. User session established with JWT tokens

**Session Management:**
- **Access Tokens**: Short-lived (1 hour) for API access
- **Refresh Tokens**: Long-lived for session renewal
- **Token Refresh**: Automatic token refresh in background
- **Logout**: Firebase sign-out + local token cleanup

### 🔧 Custom Authentication Features

**User Profile Management:**
```python
# Extended user profile with Firebase integration
class UserProfile(Base):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firebase_uid: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    provider: str  # 'email', 'google', 'apple', 'phone'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    preferences: dict = Field(default_factory=dict)
```

**Custom Claims:**
```python
# Custom Firebase claims for role-based access
async def set_custom_claims(user_id: str, claims: dict):
    auth.set_custom_user_claims(user_id, {
        'role': claims.get('role', 'user'),
        'subscription': claims.get('subscription', 'free'),
        'permissions': claims.get('permissions', [])
    })
```

---

## 🛠️ Platform Deployment

### 🌍 Universal Platform Setup Script

**One Command for Any Platform:**
```bash
./setup-platform.sh [environment] [options]

# Examples:
./setup-platform.sh codespaces          # GitHub Codespaces
./setup-platform.sh production          # Production server with monitoring
./setup-platform.sh docker              # Docker container development
./setup-platform.sh staging            # Staging environment
./setup-platform.sh development        # Local development
```

**Platform Options:**
- **--monitoring**: Enable Prometheus/Grafana monitoring
- **--backup**: Enable automated backup services
- **--skip-deps**: Skip dependency installation
- **--skip-tests**: Skip test execution
- **--verbose**: Verbose output for debugging

### 🚀 Deployment Environments

#### **GitHub Codespaces (Recommended for Quick Start)**
- **Instant Setup**: 2-3 minute automatic configuration
- **Pre-installed Tools**: Python 3.12, Node.js 18, UV, Docker
- **Port Forwarding**: Automatic HTTPS access to all services
- **VS Code Integration**: Full IDE experience with extensions

```bash
# Automatic Codespaces setup
git clone https://github.com/RegardV/JournalCraftCrew.git
cd JournalCraftCrew
./setup-platform.sh codespaces
```

#### **Docker Deployment**
- **Container Isolation**: Clean, reproducible environments
- **Multi-Service Orchestration**: Full application stack
- **Production Ready**: Optimized Dockerfiles and compose files

```bash
# Development environment
docker-compose -f docker-compose.dev.yml up -d

# Production environment
docker-compose -f docker-compose.prod.yml up -d
```

#### **Production Server Deployment**
- **Enterprise Grade**: SSL, monitoring, backups, security
- **Multi-Cloud Support**: AWS, GCP, DigitalOcean, Azure
- **High Availability**: Load balancing and redundancy

```bash
# Production setup with monitoring and backups
./setup-platform.sh production --monitoring --backup
```

### 📊 Access Information

**Development Environment:**
- **Frontend**: http://localhost:5173
- **Backend API**: https://localhost:6770 (SSL)
- **Dashboard**: http://localhost:6771
- **Agent Overview**: http://localhost:6771/agent-overview

**GitHub Codespaces:**
- **Frontend**: https://<codespace-name>-5173.github.dev
- **Backend API**: https://<codespace-name>-6770.github.dev
- **Dashboard**: https://<codespace-name>-6771.github.dev

**Production:**
- **Application**: https://yourdomain.com
- **API**: https://yourdomain.com/api
- **Dashboard**: https://yourdomain.com/admin

---

## 🏗️ Architecture

### 🤖 Multi-Layer Agent Architecture

**Application Layer (4 Active Agents):**
- **Research Specialist**: Theme and content research
- **Creative Title Writer**: Compelling journal title generation
- **Journal Content Creator**: AI-powered journal content generation
- **Content Quality Reviewer**: Quality assurance and review

**Dev Layer (6 Specialized Agents):**
- **Archon Development Assistant**: Knowledge integration and development support
- **File Storage Research Agent**: Storage solution research and recommendations
- **Authentication Patterns Research Agent**: Authentication best practices and patterns
- **VPS Deployment Research Agent**: Deployment strategies and infrastructure guidance
- **Architecture Guidance Agent**: System architecture and design patterns
- **Implementation Patterns Research Agent**: Code patterns and implementation strategies

**Legacy System (9 Archived Agents):**
- Original CrewAI implementation with migration documentation

### 🔄 Technology Stack

#### Frontend
- **React 18+**: Modern UI framework with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Firebase Client**: Authentication and real-time database
- **React Router**: Client-side routing

#### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Production-grade relational database
- **SQLAlchemy**: Python ORM with async support
- **Pydantic**: Data validation and serialization
- **JWT**: JSON Web Token authentication
- **WebSockets**: Real-time communication
- **CrewAI**: Multi-agent AI orchestration framework

#### Infrastructure
- **Docker**: Containerization and orchestration
- **Nginx**: Reverse proxy and load balancing
- **Redis**: Caching and session storage
- **Prometheus**: Monitoring and metrics collection
- **Grafana**: Visualization and dashboards
- **Firebase**: Authentication and real-time features

---

## 📚 API Documentation

### Authentication Endpoints
```http
POST   /auth/register              # User registration
POST   /auth/login                 # User login
POST   /auth/logout                # User logout
GET    /auth/me                    # Get current user
POST   /auth/forgot-password       # Password reset request
POST   /auth/verify-email          # Email verification
GET    /auth/providers             # Available auth providers
POST   /auth/token/refresh          # Refresh access token
```

### Journal Management
```http
POST   /api/journals/create        # Create new journal
GET    /api/journals/status/{id}    # Get journal creation status
GET    /api/journals/library       # Get user's journal library
GET    /api/journals/files/{id}     # Download journal files
PUT    /api/journals/{id}           # Update journal metadata
DELETE /api/journals/{id}           # Delete journal
```

### AI & Content
```http
GET    /api/themes                  # Get available themes
POST   /api/ai/generate             # Generate AI content
GET    /api/ai/progress/{jobId}     # Get generation progress
POST   /api/ai/analyze             # Analyze content
```

### Development Assistant API
```http
POST   /api/dev/archon/ask          # Archon knowledge integration
POST   /api/dev/storage/research     # File storage research
POST   /api/dev/auth/research        # Authentication patterns research
POST   /api/dev/deployment/research # VPS deployment research
POST   /api/dev/architecture/guidance # Architecture guidance
POST   /api/dev/patterns/research    # Implementation patterns research
```

### WebSocket Endpoints
```javascript
// Real-time journal progress
ws://localhost:6770/ws/journal/{jobId}

// Real-time notifications
ws://localhost:6770/ws/notifications

// Live status updates
ws://localhost:6770/ws/status
```

### API Rate Limits
- **Unauthenticated**: 50 requests per minute
- **Authenticated**: 100 requests per minute
- **Premium Users**: 500 requests per minute
- **Development**: No rate limits (local development)

---

## 🧪 Development

### 🛠️ Development Workflow

**Start Development Session:**
```bash
# Using universal setup script
./setup-platform.sh development

# Start all services
./start-journal-crew.sh
```

**Run Tests:**
```bash
# Frontend tests
npm test                    # Frontend unit tests
npm run test:watch        # Frontend watch mode
npm run test:coverage     # Frontend coverage

# Backend tests
pytest                      # Backend all tests
pytest -v                   # Backend verbose output
pytest --cov=app           # Backend coverage report

# Integration tests
pytest tests/integration/
npm run test:integration
```

**Code Quality:**
```bash
# Frontend linting and formatting
npm run lint               # ESLint check
npm run format             # Prettier formatting

# Backend linting and formatting
flake8 .                    # Flake8 linting
black .                     # Black formatting
mypy app/                   # MyPy type checking
```

**Database Migrations:**
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### 🔧 Project Structure

```
journal-platform/
├── journal-platform-frontend/     # React frontend
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # API client and Firebase
│   │   └── types/               # TypeScript types
│   ├── public/                  # Static assets
│   └── package.json
├── journal-platform-backend/      # FastAPI backend
│   ├── app/
│   │   ├── api/                 # API routes
│   │   ├── core/                # Core configuration
│   │   ├── models/              # Database models
│   │   ├── services/            # Business logic & Firebase
│   │   └── utils/               # Backend utilities
│   ├── alembic/                 # Database migrations
│   └── requirements.txt
├── orchestrator_dashboard/        # Development dashboard
│   ├── templates/               # Dashboard HTML templates
│   ├── app.py                   # Flask dashboard server
│   └── services/                # Development assistant services
├── openspec/                     # OpenSpec proposals and documentation
│   ├── changes/                  # Change proposals
│   ├── AGENTS.md                 # OpenSpec methodology
│   └── changelog.md              # Project evolution
├── .devcontainer/                # GitHub Codespaces configuration
├── .github/workflows/           # CI/CD pipelines
├── docker-compose.*.yml          # Docker orchestration
├── setup-platform.sh             # Universal setup script
├── DEPLOYMENT.md                 # Complete deployment guide
└── README.md
```

### 🔧 Environment Variables

**Backend (.env):**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/journal_platform

# Security
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-jwt-secret-key
ENVIRONMENT=development

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xyz@your-project.iam.gserviceaccount.com

# APIs
OPENAI_API_KEY=sk-your-openai-api-key

# Services
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379

# SSL (Development)
SSL_CERT_PATH=./ssl/journal_crew.crt
SSL_KEY_PATH=./ssl/journal_crew.key

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

**Frontend (.env.local):**
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:6770
VITE_WS_URL=ws://localhost:6770

# Firebase Configuration
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id

# Environment
VITE_ENVIRONMENT=development
```

---

## 💰 Pricing

### Subscription Tiers

#### 🆓 Free Tier - $0/month
**Perfect for trying out the platform**
- ✅ 1 journal per month
- ✅ 50 AI credits per month
- ✅ Basic themes (5 themes)
- ✅ Community support
- ❌ Commercial usage rights
- ❌ Premium features

#### 📈 Basic Tier - $19/month ($190/year)
**Great for regular journal creators**
- ✅ 5 journals per month
- ✅ 500 AI credits per month
- ✅ All themes + customization (25+ themes)
- ✅ Advanced formatting options
- ✅ Email support (24hr response)
- ✅ Ad-free experience
- ✅ Watermark-free downloads

#### 🚀 Premium Tier - $49/month ($490/year)
**Professional platform for power users**
- ✅ Unlimited journals
- ✅ Unlimited AI credits
- ✅ Premium exclusive themes (50+ themes)
- ✅ Commercial usage rights
- ✅ Priority support (1hr response)
- ✅ API access for integration
- ✅ Advanced analytics dashboard
- ✅ Custom branding options

### Usage Credits
- **Free**: 50 credits/month (resets monthly)
- **Basic**: 500 credits/month (resets monthly)
- **Premium**: Unlimited credits

### Payment Methods
- Credit/Debit Cards (Visa, Mastercard, American Express)
- Digital Wallets (Apple Pay, Google Pay)
- Bank Transfers (ACH, SEPA)
- Cryptocurrency (Bitcoin, Ethereum - coming soon)

### Billing Cycle
- Monthly billing with annual option (17% discount)
- Pro-rated billing for mid-cycle upgrades
- 30-day money-back guarantee for new customers
- Easy cancellation anytime

---

## 📊 Platform Status

### ✅ Completed Features (100% Complete)
- ✅ **Security Hardening**: Rate limiting, XSS protection, input validation
- ✅ **Error Handling System**: Comprehensive logging and error tracking
- ✅ **Performance Optimization**: Caching, monitoring, optimization
- ✅ **Core Features**: AI journal creation, real-time progress, content library
- ✅ **Firebase Authentication**: Complete OAuth integration with multiple providers
- ✅ **UI/UX Design**: Professional responsive interface
- ✅ **Navigation System**: Complete routing with all legal pages
- **Database Design**: PostgreSQL-ready with Firebase integration
- **API Infrastructure**: RESTful APIs with WebSocket support
- ✅ **Dev Agent System**: 6 specialized development agents with Archon integration
- ✅ **Platform Deployment**: Universal setup script for all environments
- ✅ **Docker Integration**: Complete containerization with monitoring
- ✅ **CI/CD Pipeline**: Automated testing, building, and deployment
- ✅ **Development Dashboard**: Real-time monitoring and agent management

### 🔄 Commercial Monetization (Ready for Implementation)
- 🔄 **Payment Processing**: Stripe integration ready
- 🔄 **Subscription Management**: Three-tier pricing model
- 🔄 **User Account Enhancement**: Email verification, plan selection
- 🔄 **Service Access Control**: Feature gating by subscription
- 🔄 **Usage Tracking**: Credit system and analytics
- 🔄 **Customer Portal**: Self-service management

### 📋 Next Steps (6-Week Timeline)
- **Week 1-2**: Database schema updates, Stripe setup
- **Week 3-4**: Payment flow implementation, webhooks
- **Week 5-6**: Service access control, credit system
- **Week 7-8**: Analytics dashboard, commercial launch

### 🎯 Revenue Targets
- **Month 1**: $1,200+ MRR (60 Basic + 20 Premium users)
- **Month 3**: $3,000+ MRR (150 total paid users)
- **Month 6**: $15,000+ MRR (750 total paid users)
- **Year 1**: $180,000+ Annual Revenue Run Rate

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Getting Started
1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Test** thoroughly: `npm run test && pytest`
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to your fork: `git push origin feature/amazing-feature`
8. **Create** a Pull Request

### Development Guidelines
- **Code Style**: Follow existing code style and patterns
- **Testing**: Ensure all tests pass and add new tests for new features
- **Documentation**: Update documentation for any API changes
- **Security**: Follow security best practices
- **Performance**: Consider performance implications of changes

### OpenSpec Development
- Use **OpenSpec methodology**: `@/openspec/AGENTS.md`
- **Create proposals**: `openspec/changes/feature-name/proposal.md`
- **Track progress**: Monitor through OpenSpec changelog
- **Engage with agents**: Use development agent team for research and guidance

### Areas for Contribution
- 🎨 **UI/UX Improvements**: Enhanced user experience
- 🔧 **Backend Features**: New API endpoints and services
- 📊 **Analytics**: Enhanced reporting and metrics
- 🧪 **Testing**: Additional test coverage
- 📚 **Documentation**: Improved docs and guides
- 🚀 **Performance**: Optimization improvements
- 🔒 **Security**: Security enhancements
- 🤖 **AI Agents**: New specialized agents and capabilities
- ☁️ **Deployment**: New deployment platforms and strategies

### Code of Conduct
Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors.

---

## 📄 License

**Journal Craft Crew Commercial License** - Fair Revenue Share Model

This project is licensed under a **custom commercial license** that allows you to build profitable businesses while supporting sustainable development.

### 💰 **Revenue Share Model**
- **$0 - $900/month**: 🆓 **No license fees**
- **Above $900/month**: 💰 **3.5% of revenue exceeding $900**

### 📋 **Quick Examples**
| Monthly Revenue | License Fee | Net Revenue |
|-----------------|-------------|-------------|
| $1,000 | $3.50 | $996.50 |
| $5,000 | $143.50 | $4,856.50 |
| $10,000 | $318.50 | $9,681.50 |

### ✅ **What You CAN Do**
- **Commercial Use**: Operate as a SaaS platform
- **Modification**: Full source code access and customization
- **Distribution**: Sell modified versions
- **Scaling**: Unlimited revenue potential
- **White-label**: Rebrand for your business
- **OpenSource Contributions**: Submit pull requests and improvements

### 📋 **License Requirements**
- **Revenue Reporting**: Monthly reporting when >$900/month
- **Fair Payment**: 3.5% on revenue above threshold
- **Compliance**: Maintain accurate records
- **Attribution**: Preserve copyright notices

### 📄 **License Documents**
- **[Full License Agreement](./LICENSE)** - Complete legal terms
- **[License Summary](./COMMERCIAL_LICENSE.md)** - Easy-to-understand overview

### 🎯 **Why This License?**
- **Low Risk**: Start without upfront costs
- **Fair Pricing**: Only pay when successful
- **Sustainable**: Supports continued development
- **Business Friendly**: Designed for commercial success

### 🤝 **Custom Arrangements**
For enterprise licensing, white-label agreements, or custom terms, contact:
- **Email**: contact@journalcraftcrew.com
- **GitHub**: https://github.com/RegardV/JournalCraftCrew

### 🙏 Acknowledgments

**Special Thanks**
- **CrewAI Team**: For the amazing multi-agent AI framework
- **FastAPI Community**: For the excellent web framework
- **React Team**: For the powerful UI library
- **Firebase**: For authentication and real-time services
- **OpenAI**: For the GPT API that powers our AI features
- **Stripe**: For the payment processing platform
- **All Contributors**: Everyone who has helped improve this project

### Technologies Used
- [React](https://reactjs.org/) - UI Framework
- [FastAPI](https://fastapi.tiangolo.com/) - Backend Framework
- [TypeScript](https://www.typescriptlang.org/) - Type Safety
- [Tailwind CSS](https://tailwindcss.com/) - CSS Framework
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Firebase](https://firebase.google.com/) - Authentication & Real-time Services
- [CrewAI](https://crewai.com/) - AI Agent Framework
- [OpenAI](https://openai.com/) - AI API
- [Stripe](https://stripe.com/) - Payment Processing
- [Docker](https://www.docker.com/) - Containerization

### Community
- **Discord Server**: [Join our community](https://discord.gg/journalcraftcrew)
- **Twitter**: [@JournalCraftCrew](https://twitter.com/journalcraftcrew)
- **Blog**: [Journal Craft Crew Blog](https://blog.journalcraftcrew.com)
- **Documentation**: [Complete Deployment Guide](DEPLOYMENT.md)

### Professional Support
- **Priority Support**: Available for Premium tier customers
- **Enterprise Support**: Custom solutions and dedicated support
- **Consulting Services**: Development and integration services

---

<div align="center">

**Made with ❤️ by the Journal Craft Crew Team**

*Transforming ideas into beautifully crafted journals with the power of AI and 19 specialized agents*

[🚀 Get Started Now](https://journalcraftcrew.com) • [📖 Documentation](DEPLOYMENT.md) • [💬 Discord](https://discord.gg/journalcraftcrew) • [🤖 Development Agents](#development-agent-team)

</div>