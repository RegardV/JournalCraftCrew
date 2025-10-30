# Journal Platform Backend

Comprehensive FastAPI backend for the Journal Craft Crew journaling platform. Supports user management, project handling, theme system, and export services with modern async architecture.

## Features

- **Modern FastAPI Architecture**: Built with FastAPI 0.104+ using async/await patterns
- **Database Integration**: SQLAlchemy 2.0+ with async PostgreSQL support and migrations
- **Authentication System**: JWT-based authentication with OAuth2 integration
- **User Management**: Complete user CRUD with subscription management
- **Project System**: Multi-project support with themes and collaboration
- **Theme Engine**: 50+ customizable themes with premium options
- **Export Services**: PDF, EPUB, and KDP integration
- **API Documentation**: Auto-generated OpenAPI docs at `/docs`
- **Production Ready**: Comprehensive error handling, logging, and monitoring
- **Docker Development**: Complete containerized development environment

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with asyncpg driver
- **ORM**: SQLAlchemy 2.0+ with async support
- **Authentication**: JWT tokens with OAuth2 integration
- **Cache**: Redis for session management
- **Background Jobs**: Celery with Redis broker
- **Testing**: pytest with async support
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Monitoring**: Structured logging with Sentry integration
- **Containerization**: Docker and Docker Compose for development

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional, for containerized development)

### Automated Setup

Run the automated setup script:

```bash
cd journal-platform-backend
./scripts/setup.sh
```

This will:
- Create and activate a Python virtual environment
- Install all dependencies
- Set up Docker containers for PostgreSQL and Redis
- Run database migrations
- Create necessary directories and configuration files

### Manual Setup

1. **Clone and setup environment**
```bash
cd journal-platform-backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database and service configurations
```

3. **Set up databases**
```bash
# Using Docker (recommended for development)
docker-compose up -d postgres redis

# Or set up PostgreSQL and Redis manually
```

4. **Run migrations**
```bash
python -m app.core.migrations migrate
```

5. **Start the server**
```bash
python main.py
```

### Docker Development

Start the complete development stack:

```bash
docker-compose up -d
```

This starts:
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Adminer** (DB Admin): http://localhost:8080

## Development

### Environment Variables

See `.env.example` for all configuration options. Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT signing key (change in production)
- `DEBUG`: Enable debug mode (development only)

### Database Migrations

Create and apply migrations:

```bash
# Apply all migrations
python -m app.core.migrations migrate

# Reset database (development only)
python -m app.core.migrations reset
```

### Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_database.py
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## Health Checks

Monitor application health:

```bash
curl http://localhost:8000/health
```

Returns system status, database connectivity, and version information.

## Project Structure

```
journal-platform-backend/
├── app/
│   ├── api/              # API routes and endpoints
│   ├── core/             # Core configuration and database
│   ├── models/           # SQLAlchemy models
│   └── services/         # Business logic services
├── tests/                # Test suite
├── scripts/              # Setup and utility scripts
├── uploads/              # File upload directory
├── logs/                 # Application logs
├── docker-compose.yml    # Docker development environment
├── Dockerfile           # Application container
└── requirements.txt     # Python dependencies
```

## API Endpoints

### Authentication & Authorization
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user profile

### User Management
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/preferences` - Get user preferences
- `PUT /api/users/preferences` - Update user preferences

### Project Management
- `GET /api/projects/` - List user projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Theme Engine
- `GET /api/themes/` - List available themes
- `GET /api/themes/{id}` - Get theme details
- `POST /api/themes/` - Create theme (admin)

### Export Service
- `GET /api/export/records` - Get export history
- `POST /api/export/request/{project_id}` - Request export
- `GET /api/export/kdp/status/{export_id}` - Get KDP status
- `POST /api/export/kdp/publish/{export_id}` - Publish to KDP

## Contributing

1. Follow PEP 8 code style
2. Add tests for new features
3. Update documentation
4. Use type hints throughout
5. Run tests before submitting PRs

## License

MIT License - see LICENSE file for details.