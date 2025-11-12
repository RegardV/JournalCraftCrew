## Why
The Journal Craft Crew platform currently has three conflicting journal creation workflows that create user confusion and technical debt. The primary CrewAI workflow is properly implemented, but duplicate mock implementations and inconsistent user experiences prevent users from accessing the full power of the 9-agent CrewAI system.

## What Changes
- **BREAKING**: Remove mock AI generation system (`JournalCreator.tsx`, `ai_generation.py`)
- **BREAKING**: Consolidate three journal creation workflows into single CrewAI-powered flow
- **BREAKING**: Unify project management and progress tracking systems
- Enhance onboarding to clearly present CrewAI agent capabilities
- Add project continuation interface for incomplete workflows
- Implement unified export system across all journal types
- Add workflow selection based on user needs and complexity

## Impact
- **Affected specs**: journal-creation, crewai-agents, project-management, user-interface
- **Affected code**:
  - Frontend: `JournalCreator.tsx`, `NewAIWorkflowPage.tsx`, `JournalCreationModal.tsx`, `CrewAIProjectDetail.tsx`
  - Backend: `ai_generation.py`, `crewai_workflow.py`, onboarding and project APIs
  - Database: Project models, workflow tracking schemas
- **User Impact**: Simplified, consistent experience with full CrewAI agent capabilities
- **Technical Impact**: Reduced complexity, unified codebase, improved maintainability

## Success Metrics
- Reduce journal creation pathways from 3 to 1 unified CrewAI workflow
- Eliminate mock implementations and duplicate code
- Improve project continuation rate from 0% to 80%+
- Achieve 100% user access to all 9 CrewAI agents
- Unified progress tracking and export system for all journals