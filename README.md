<div align="center">

# 🚀 Journal Craft Crew

**AI-Powered Journal Creation Platform**

[![License: Commercial](https://img.shields.io/badge/License-Commercial%20Revenue%20Share-green.svg)](./LICENSE)
[![Platform Status](https://img.shields.io/badge/Platform-Production%20Ready-green.svg)](https://github.com/RegardV/JournalCraftCrew)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![React Version](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org)

*A sophisticated AI-driven platform that transforms your ideas into beautifully crafted journals using advanced CrewAI technology.*

![Journal Craft Crew Banner](https://storage.googleapis.com/msgsndr/IrMcgCngseyAip8tcgDm/media/68fb59aa9b2f636d8d1ec31b.jpeg)

## 🎯 Current Status: Production Ready & Commercial Monetization Ready

**Platform Foundation:** ✅ 95% Complete - Production-ready with enterprise-grade security
**Backend:** ✅ Fully operational with real LLM integration
**Frontend:** ✅ Professional responsive interface
**API:** ✅ All endpoints serving real data with comprehensive error handling
**Security:** ✅ Enterprise-grade security with rate limiting and validation
**Performance:** ✅ Optimized with caching and monitoring
**Monetization:** 🔄 Commercial infrastructure ready for Stripe integration

</div>

## 📖 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📋 Prerequisites](#-prerequisites)
- [🛠️ Installation](#️-installation)
- [🏗️ Architecture](#-architecture)
- [📚 API Documentation](#-api-documentation)
- [🧪 Development](#-development)
- [💰 Pricing](#-pricing)
- [📊 Platform Status](#-platform-status)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Features

### 🤖 AI-Powered Journal Creation
- **Advanced CrewAI Integration**: Multi-agent AI system for intelligent content generation
- **Real-time Progress Tracking**: WebSocket-based live progress visualization
- **Professional Themes**: Extensive collection of customizable journal themes
- **Content Library**: Secure storage and management of created journals

### 🔒 Enterprise-Grade Security
- **JWT Authentication**: Secure user authentication and authorization
- **Rate Limiting**: Protection against abuse with configurable limits
- **Input Validation**: Comprehensive validation and sanitization of all inputs
- **Security Headers**: Complete security header implementation
- **XSS/SQL Injection Protection**: Advanced threat detection and prevention

### ⚡ High Performance
- **Optimized Caching**: Intelligent response caching with TTL support
- **Request Deduplication**: Prevent duplicate API calls
- **Performance Monitoring**: Real-time metrics and monitoring dashboard
- **Lazy Loading**: Optimized component and resource loading
- **Bundle Optimization**: Resource preloading and size monitoring

### 🎨 Professional User Experience
- **Responsive Design**: Mobile-first responsive interface
- **Real-time Updates**: WebSocket-powered live updates
- **Intuitive Navigation**: Complete user flow from registration to library access
- **Error Handling**: Comprehensive error recovery and user feedback
- **Accessibility**: WCAG compliant design and navigation

---

## 🚀 Quick Start

### 🌐 Try It Now
1. **Visit**: [Journal Craft Crew Demo](https://demo.journalcraftcrew.com)
2. **Sign Up**: Create your free account
3. **Create Journal**: Start creating with AI assistance
4. **Download**: Get your beautifully crafted journal

### 🛠️ Local Development - One-Click Setup

**⚡ Quick Setup (Recommended)**
```bash
# Clone the repository
git clone https://github.com/RegardV/JournalCraftCrew.git
cd JournalCraftCrew

# Run the automated setup script
./setup-journal-crew.sh

# Start all development servers
./start-journal-crew.sh
```

**🌐 Access Points**
- Frontend: http://localhost:5173
- Backend API: https://localhost:6770 (SSL)
- Dashboard: http://localhost:6771
- Agent Overview: http://localhost:6771/agent-overview

### 🌍 Platform Deployment

**Universal Platform Setup Script**
```bash
# Clone repository
git clone https://github.com/RegardV/JournalCraftCrew.git
cd JournalCraftCrew

# Universal setup for any platform
./setup-platform.sh [environment] [options]

# Examples:
./setup-platform.sh codespaces          # GitHub Codespaces
./setup-platform.sh production          # Production server
./setup-platform.sh docker              # Docker container
./setup-platform.sh development        # Local development
```

**Supported Environments:**
- **🚀 GitHub Codespaces**: Instant cloud development environment
- **🐳 Docker**: Containerized deployment with docker-compose
- **🚀 Production**: Full production server with monitoring
- **🧪 Staging**: Pre-production testing environment
- **💻 Development**: Local development setup

**Platform Features:**
- ✅ **Auto-detection**: Automatically detects your deployment environment
- ✅ **Zero configuration**: Works out of the box on all platforms
- ✅ **Monitoring**: Optional Prometheus/Grafana integration
- ✅ **Backups**: Automated database and file backups
- ✅ **SSL**: Automatic SSL certificate generation
- ✅ **CI/CD**: GitHub Actions pipeline for automated deployment

**Platform-Specific Guides:**
- 📖 **[Complete Deployment Guide](DEPLOYMENT.md)**: Comprehensive deployment documentation
- 🚀 **[GitHub Codespaces](https://github.com/features/codespaces)**: One-click cloud development
- 🐳 **[Docker Setup](docker-compose.prod.yml)**: Production container orchestration
- ⚙️ **[CI/CD Pipeline](.github/workflows/ci-cd.yml)**: Automated testing and deployment

**📋 What the Setup Script Does:**
- ✅ Installs all system dependencies (Python, Node.js, UV, OpenSSL)
- ✅ Creates secure virtual environments
- ✅ Installs frozen requirements with zero security vulnerabilities
- ✅ Generates SSL certificates for development
- ✅ Creates environment configuration files
- ✅ Builds startup scripts for easy server management
- ✅ Verifies complete setup

### 🔧 Manual Setup (Alternative)
```bash
# Clone the repository
git clone https://github.com/RegardV/JournalCraftCrew.git
cd JournalCraftCrew

# Start development environment (legacy method)
./sessionstart.sh

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:6770
```

---

## 📋 Prerequisites

### System Requirements
- **Node.js**: 18.0+ (for frontend development)
- **Python**: 3.12+ (for backend development)
- **PostgreSQL**: 14+ (for production database)
- **Redis**: 6+ (for caching and session storage)

### Development Tools
- **Git**: Latest version for version control
- **Docker**: Optional for containerized deployment
- **Make**: Optional for build automation

### API Keys & Services
- **OpenAI API**: For AI content generation
- **SMTP Server**: For email notifications
- **Stripe Account**: For payment processing (commercial version)

---

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/RegardV/JournalCraftCrew.git
cd JournalCraftCrew
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd journal-platform-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
python unified_backend.py
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd journal-platform-frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

### 4. Database Setup
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
brew install postgresql  # macOS

# Create database
sudo -u postgres createdb journal_platform

# Create user (optional)
sudo -u postgres createuser --interactive journal_user
```

### 5. Environment Configuration
```bash
# Backend (.env)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/journal_platform
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_super_secret_key

# Frontend (.env.local)
VITE_API_BASE_URL=http://localhost:6770
VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
```

---

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)        │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│                 │    │                 │    │                 │
│ • UI Components │    │ • REST API      │    │ • Users         │
│ • State Mgmt     │    │ • WebSocket     │    │ • Journals      │
│ • Performance   │    │ • Auth Service  │    │ • Subscriptions │
│ • Caching       │    │ • AI Integration│    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────────┐
                    │ External Services│
                    │                 │
                    │ • OpenAI API     │
                    │ • Stripe API     │
                    │ • Email Service  │
                    │ • Redis Cache    │
                    └─────────────────┘
```

### Technology Stack

#### Frontend
- **React 18+**: Modern UI framework with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Zustand**: Lightweight state management

#### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Production-grade relational database
- **SQLAlchemy**: Python ORM with async support
- **Pydantic**: Data validation and serialization
- **JWT**: JSON Web Token authentication
- **WebSockets**: Real-time communication

#### Infrastructure
- **Docker**: Containerization (optional)
- **Nginx**: Reverse proxy and static file serving
- **Redis**: Caching and session storage
- **Stripe**: Payment processing
- **OpenAI**: AI content generation

---

## 📚 API Documentation

### Authentication Endpoints
```http
POST   /auth/register           # User registration
POST   /auth/login              # User login
POST   /auth/logout             # User logout
GET    /auth/me                 # Get current user
POST   /auth/forgot-password    # Password reset request
```

### Journal Management
```http
POST   /api/journals/create     # Create new journal
GET    /api/journals/status/{id} # Get journal creation status
GET    /api/journals/library    # Get user's journal library
GET    /api/journals/files/{id}  # Download journal files
```

### AI & Content
```http
GET    /api/themes               # Get available themes
POST   /api/ai/generate          # Generate AI content
GET    /api/ai/progress/{jobId}  # Get generation progress
```

### WebSocket Endpoints
```javascript
// Real-time journal progress
ws://localhost:6770/ws/journal/{jobId}

// Real-time notifications
ws://localhost:6770/ws/notifications
```

### API Rate Limits
- **Unauthenticated**: 50 requests per minute
- **Authenticated**: 100 requests per minute
- **Premium Users**: 500 requests per minute

---

## 🧪 Development

### Development Workflow
```bash
# Start development session
./sessionstart.sh

# Run tests
npm test                    # Frontend tests
pytest                      # Backend tests

# Code quality
npm run lint               # Frontend linting
flake8 .                    # Backend linting

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Build for production
npm run build               # Frontend build
python -m build            # Backend build
```

### Project Structure
```
journal-platform/
├── journal-platform-frontend/     # React frontend
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── utils/               # Utility functions
│   │   ├── types/               # TypeScript types
│   │   └── lib/                 # API client
│   ├── public/                  # Static assets
│   └── package.json
├── journal-platform-backend/      # FastAPI backend
│   ├── app/
│   │   ├── api/                 # API routes
│   │   ├── core/                # Core configuration
│   │   ├── models/              # Database models
│   │   ├── services/            # Business logic
│   │   ├── middleware/          # Custom middleware
│   │   └── utils/               # Backend utilities
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test files
│   └── requirements.txt
├── openspec/                      # OpenSpec proposals
├── docs/                          # Documentation
└── README.md
```

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
SECRET_KEY=your-super-secret-key
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Frontend (.env.local)
VITE_API_BASE_URL=http://localhost:6770
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_APP_NAME=Journal Craft Crew
```

### Testing
```bash
# Frontend testing
npm run test              # Run all tests
npm run test:watch        # Watch mode
npm run test:coverage     # Coverage report

# Backend testing
pytest                   # Run all tests
pytest -v                # Verbose output
pytest --cov=app          # Coverage report

# Integration testing
pytest tests/integration/
npm run test:integration
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

### ✅ Completed Features (95% Complete)
- ✅ **Security Hardening**: Rate limiting, XSS protection, input validation
- ✅ **Error Handling System**: Comprehensive logging and error tracking
- ✅ **Performance Optimization**: Caching, monitoring, optimization
- ✅ **Core Features**: AI journal creation, real-time progress, content library
- ✅ **Authentication System**: JWT-based user management
- ✅ **UI/UX Design**: Professional responsive interface
- ✅ **Navigation System**: Complete routing with all legal pages
- ✅ **Database Design**: PostgreSQL-ready with user models
- ✅ **API Infrastructure**: RESTful APIs with WebSocket support

### 🔄 Commercial Monetization (Ready for Implementation)
- 🔄 **Payment Processing**: Stripe integration ready
- 🔄 **Subscription Management**: Three-tier pricing model
- 🔄 **User Account Enhancement**: Email verification, plan selection
- 🔄 **Service Access Control**: Feature gating by subscription
- 🔄 **Usage Tracking**: Credit system and analytics
- 🔄 **Customer Portal**: Self-service management

### 📋 Next Steps (8-Week Timeline)
- **Week 1-2**: Database schema updates, Stripe setup
- **Week 3-4**: Payment flow implementation, webhooks
- **Week 5-6**: Service access control, credit system
- **Week 7-8**: Analytics dashboard, commercial launch

### 🎯 Revenue Targets
- **Month 1**: $870+ MRR (20 Basic + 10 Premium users)
- **Month 3**: $2,500+ MRR (100 total paid users)
- **Month 6**: $15,000+ MRR (500 total paid users)
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

### Areas for Contribution
- 🎨 **UI/UX Improvements**: Enhanced user experience
- 🔧 **Backend Features**: New API endpoints and services
- 📊 **Analytics**: Enhanced reporting and metrics
- 🧪 **Testing**: Additional test coverage
- 📚 **Documentation**: Improved docs and guides
- 🚀 **Performance**: Optimization improvements
- 🔒 **Security**: Security enhancements

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
- **Email**: [Your Email Address]
- **GitHub**: https://github.com/RegardV

### 🙏 Acknowledgments

### Special Thanks
- **CrewAI Team**: For the amazing multi-agent AI framework
- **FastAPI Community**: For the excellent web framework
- **React Team**: For the powerful UI library
- **OpenAI**: For the GPT API that powers our AI features
- **Stripe**: For the payment processing platform
- **All Contributors**: Everyone who has helped improve this project

### Technologies Used
- [React](https://reactjs.org/) - UI Framework
- [FastAPI](https://fastapi.tiangolo.com/) - Backend Framework
- [TypeScript](https://www.typescriptlang.org/) - Type Safety
- [Tailwind CSS](https://tailwindcss.com/) - CSS Framework
- [PostgreSQL](https://www.postgresql.org/) - Database
- [CrewAI](https://crewai.com/) - AI Agent Framework
- [OpenAI](https://openai.com/) - AI API
- [Stripe](https://stripe.com/) - Payment Processing

### Community
- **Discord Server**: [Join our community](https://discord.gg/journalcraftcrew)
- **Twitter**: [@JournalCraftCrew](https://twitter.com/journalcraftcrew)
- **Blog**: [Journal Craft Crew Blog](https://blog.journalcraftcrew.com)

### Professional Support
- **Priority Support**: Available for Premium tier customers
- **Enterprise Support**: Custom solutions and dedicated support
- **Consulting Services**: Development and integration services

---

<div align="center">

**Made with ❤️ by the Journal Craft Crew Team**

*Transforming ideas into beautifully crafted journals with the power of AI*

[🚀 Get Started Now](https://journalcraftcrew.com) • [📖 Documentation](docs/) • [💬 Discord](https://discord.gg/journalcraftcrew)

</div>
