# Journal Craft Crew - Project Context

## Purpose
AI-powered journal creation platform that combines multi-agent AI coordination with modern web interfaces. Users can create personalized journals through AI-guided workflows, with CrewAI agents handling content generation, analysis, and formatting.

**🎉 Current Status: PRODUCTION READY (98%)** ✅
- Backend API fully operational with real LLM integration
- Frontend React TypeScript application running successfully
- User authentication with JWT tokens implemented
- Real journal projects being served from `../LLM_output` directory

## Tech Stack
- **Backend**: FastAPI (Python), JWT authentication, bcrypt password hashing, file-based data persistence
- **Frontend**: React + TypeScript + Vite, Tailwind CSS design system
- **AI Framework**: CrewAI (multi-agent coordination) - **Next Phase Integration**
- **Authentication**: JWT tokens with industry-standard bcrypt security
- **Data**: JSON file storage with real LLM output integration
- **Deployment**: Dual-server architecture - Backend:8000, Frontend:5173

## Project Conventions

### Code Style
- **Python**: FastAPI patterns, async/await, type hints with Pydantic models
- **Frontend**: React + TypeScript, component-based architecture with Tailwind CSS
- **Security**: Industry-standard JWT implementation with bcrypt password hashing
- **Naming**: kebab-case for file names, camelCase for TypeScript, snake_case for Python

### Architecture Patterns ✅ **IMPLEMENTED**
- **Multi-Agent System**: CrewAI-based specialized agents with manager orchestration (**Next Phase**)
- **API Design**: RESTful endpoints with JWT middleware protection ✅
- **Frontend**: Single-page application with authentication flows ✅
- **Data Flow**: Real LLM integration from file system ✅

### Testing Strategy ✅ **PARTIALLY COMPLETE**
- **Authentication**: User registration/login testing with JWT validation ✅
- **API Testing**: Endpoint protection verification ✅
- **Integration**: Frontend-backend authentication flow testing ✅
- **Agent Testing**: CrewAI workflow validation (**Next Phase**)

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

## Current Implementation Status ✅

### **Production Ready Components (98%)**
- **Backend API**: FastAPI unified server running on port 8000 ✅
- **Frontend Application**: React + TypeScript + Vite running on port 5173 ✅
- **Authentication**: JWT tokens with bcrypt password hashing ✅
- **Real Data Integration**: LLM projects served from `../LLM_output` directory ✅
- **Dashboard**: Functional component displaying real journal projects ✅
- **User Management**: Registration, login, and profile system ✅

### **Next Phase Integration (Post-Launch)**
- **CrewAI Agents**: Multi-agent journal creation workflow
- **Enhanced Journal Creation**: Advanced AI-powered content generation
- **Real-time Updates**: WebSocket progress tracking
- **Export Features**: PDF generation and download functionality

## Important Constraints
- **Security**: JWT authentication with bcrypt required for all protected endpoints ✅
- **Local Development**: File-based persistence with real LLM output integration ✅
- **Agent Coordination**: CrewAI agents must work collaboratively (**Next Phase**)
- **User Experience**: Seamless authentication flow with industry-standard UX patterns ✅
- **Performance**: Optimized backend response times <100ms ✅

## External Dependencies
- **CrewAI**: Multi-agent AI coordination framework (**Next Phase Integration**)
- **FastAPI**: Backend API framework with automatic OpenAPI documentation ✅
- **Uvicorn**: ASGI server for production deployment ✅
- **Pydantic**: Data validation and serialization ✅
- **Node.js/npm**: Frontend build tooling and development server ✅
- **React + TypeScript**: Frontend framework with type safety ✅
- **Tailwind CSS**: Modern utility-first CSS framework ✅
