# CrewAI Web Integration

## Purpose
Integrate the existing CrewAI multi-agent system with the web interface to enable real AI-powered journal generation, starting with the onboarding agent as the critical entry point for the entire workflow.

## Why
**CRITICAL GAP IDENTIFIED**: The system has a sophisticated CrewAI implementation with 9 specialized agents, but the web interface currently only provides mock AI simulation. The onboarding agent is the key orchestrator that gathers user preferences and initiates the entire agent workflow.

**Current State Analysis:**
- ✅ **Complete CrewAI Implementation**: 9 agents fully implemented (onboarding, manager, discovery, research, content_curator, editor, media, pdf_builder, platform_setup)
- ✅ **Functional Web Interface**: React frontend connected to FastAPI backend
- ✅ **WebSocket Infrastructure**: Real-time progress tracking capability exists
- ❌ **CRITICAL MISSING PIECE**: Web interface cannot access real CrewAI agents
- ❌ **Mock Implementation Only**: Current AI generation is simulated, not real

**The Onboarding Agent is the KEY**: It serves as the primary entry point that:
1. Collects user preferences (theme, title, style, research depth)
2. Fetches dynamic author styles via LLM
3. Sets up project directories and configuration
4. Orchestrates the entire CrewAI workflow
5. Returns structured preferences for downstream agents

## What Changes
- **Onboarding Agent Web Interface**: Create web form for onboarding agent preference collection
- **CrewAI Workflow Integration**: Connect web interface to real CrewAI agent execution
- **Real-time Progress Tracking**: Integrate WebSocket updates for actual agent progress
- **API Endpoint Enhancement**: Replace mock endpoints with real CrewAI execution
- **User Preference Management**: Store and manage onboarding preferences in web interface

## Impact
- **Affected specs**: api (real CrewAI endpoints), integration (web-agent communication), workflows (real AI generation workflows)
- **Affected code**: Frontend components, backend API routes, CrewAI agent integration
- **Breaking changes**: None - enhances existing mock functionality with real AI
- **Dependencies**: Requires unified backend and frontend integration (completed)

## Technical Changes
- Create onboarding agent web interface matching CLI functionality
- Implement CrewAI agent execution through FastAPI endpoints
- Integrate real-time WebSocket progress updates for agent workflows
- Replace mock AI generation with actual CrewAI agent orchestration
- Store user preferences and project data from onboarding process

## Success Metrics
- Web interface successfully initiates real CrewAI workflows
- Onboarding agent collects preferences through web interface
- Real-time progress tracking shows actual agent execution status
- Users receive AI-generated journals from real CrewAI agents
- Complete journal creation workflow functions end-to-end through web interface