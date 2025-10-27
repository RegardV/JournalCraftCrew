# Journal Craft Crew - Project Context

## Purpose
AI-powered journal creation platform that combines multi-agent AI coordination with modern web interfaces. Users can create personalized journals through AI-guided workflows, with CrewAI agents handling content generation, analysis, and formatting.

## Tech Stack
- **Backend**: FastAPI (Python), JWT authentication, file-based data persistence
- **Frontend**: React/JavaScript, Vite development server
- **AI Framework**: CrewAI (multi-agent coordination)
- **Authentication**: JWT tokens, secure password hashing (SHA-256)
- **Data**: JSON file storage (development), designed for database migration
- **Deployment**: Uvicorn server, CORS-enabled for local development

## Project Conventions

### Code Style
- **Python**: FastAPI patterns, async/await, type hints with Pydantic models
- **Frontend**: Modern JavaScript, component-based structure
- **Security**: Industry-standard JWT implementation, Authorization header protection
- **Naming**: kebab-case for file names, camelCase for JavaScript, snake_case for Python

### Architecture Patterns
- **Multi-Agent System**: CrewAI-based specialized agents with manager orchestration
- **API Design**: RESTful endpoints with JWT middleware protection
- **Frontend**: Single-page application with authentication flows
- **Data Flow**: Agent-coordinated processing pipeline with user authentication

### Testing Strategy
- **Authentication**: User registration/login testing with JWT validation
- **API Testing**: Endpoint protection verification
- **Integration**: Frontend-backend authentication flow testing
- **Agent Testing**: CrewAI workflow validation (planned)

### Git Workflow
- **Feature Branches**: Separate branches for major capabilities
- **OpenSpec Integration**: Specs drive development, changes tracked via OpenSpec
- **Commit Convention**: Conventional commits with clear feature descriptions

## Domain Context

### Core Concepts
- **Journal Creation**: AI-assisted generation of personalized journal content
- **Multi-Agent Processing**: Specialized AI agents for different aspects (content, analysis, formatting)
- **User Profiles**: Personal journaler vs content creator with different AI credit allocations
- **Themed Journals**: Predefined themes (mindfulness, productivity, creativity, gratitude)

### User Journey
1. **Authentication**: Secure JWT-based login/registration
2. **Theme Selection**: Choose journal theme and style preferences
3. **AI Generation**: CrewAI agents coordinate to create personalized content
4. **Customization**: Format and export options (PDF, EPUB, KDP)

## Important Constraints
- **Security**: JWT authentication required for all protected endpoints
- **Local Development**: File-based persistence, designed for migration to database
- **Agent Coordination**: CrewAI agents must work collaboratively, not independently
- **User Experience**: Seamless authentication flow with industry-standard UX patterns
- **Performance**: AI generation with realistic progress tracking and background processing

## External Dependencies
- **CrewAI**: Multi-agent AI coordination framework
- **FastAPI**: Backend API framework with automatic OpenAPI documentation
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and serialization
- **Node.js/npm**: Frontend build tooling and development server
