## ADDED Requirements

### Requirement: Frontend Authentication API Integration
The system SHALL provide React frontend components that integrate with FastAPI authentication endpoints for secure user access.

#### Scenario: Frontend login and registration
- GIVEN users accessing the login page
- WHEN users submit credentials through React forms
- THEN the frontend SHALL call FastAPI authentication endpoints
- AND the system SHALL manage JWT tokens in frontend state
- AND users SHALL be redirected to dashboard upon successful authentication
- AND the frontend SHALL handle authentication errors with user-friendly messages

#### Scenario: API key management in frontend
- GIVEN authenticated users accessing settings
- WHEN users configure OpenAI API keys
- THEN the frontend SHALL provide secure API key input forms
- AND the system SHALL validate API keys through backend endpoints
- AND users SHALL receive real-time API key status updates
- AND the interface SHALL guide users through API key setup process

### Requirement: Frontend Journal Generation API Integration
The system SHALL provide React frontend interfaces that connect to FastAPI AI generation endpoints for complete journal creation workflows.

#### Scenario: Journal creation request through frontend
- GIVEN users initiating journal creation through web interface
- WHEN users provide preferences and submit requests
- THEN the frontend SHALL call FastAPI AI generation endpoints
- AND the system SHALL create background jobs for AI processing
- AND users SHALL receive job IDs for progress tracking
- AND the frontend SHALL initiate WebSocket connections for real-time updates

#### Scenario: Real-time progress tracking in frontend
- GIVEN active AI generation jobs
- WHEN jobs progress through different agent phases
- THEN the frontend SHALL display real-time progress via WebSocket
- AND users SHALL see current agent status and completion percentages
- AND the system SHALL provide estimated time remaining
- AND users SHALL receive notifications for job completion or errors

### Requirement: Frontend Project Management API Integration
The system SHALL provide React frontend components that integrate with FastAPI project management endpoints for complete project lifecycle.

#### Scenario: Project dashboard and listing
- GIVEN users accessing their project dashboard
- WHEN the dashboard loads user projects
- THEN the frontend SHALL call FastAPI project listing endpoints
- AND the system SHALL display projects with status indicators
- AND users SHALL filter and search projects through web interface
- AND the frontend SHALL provide project creation and management options

#### Scenario: Project export and download
- GIVEN completed journal projects
- WHEN users request downloads in different formats
- THEN the frontend SHALL call FastAPI export endpoints
- AND the system SHALL provide download links for PDF, EPUB, and KDP formats
- AND users SHALL track export job progress through interface
- AND the frontend SHALL handle export errors and retry options

### Requirement: Frontend WebSocket Integration
The system SHALL provide comprehensive WebSocket client implementation in React frontend for real-time communication with backend services.

#### Scenario: WebSocket connection management
- GIVEN users accessing pages requiring real-time updates
- WHEN the frontend initializes WebSocket connections
- THEN the system SHALL establish secure WebSocket connections
- AND the frontend SHALL handle connection drops and reconnection
- AND users SHALL receive seamless real-time updates
- AND the system SHALL maintain connection state across page navigation

#### Scenario: Real-time user interaction through WebSocket
- GIVEN AI workflows requiring user decisions
- WHEN the backend requests user input
- THEN the frontend SHALL display interactive decision interfaces
- AND users SHALL submit choices through web forms
- AND the WebSocket SHALL communicate decisions back to backend
- AND the system SHALL resume AI workflows based on user responses