## ADDED Requirements

### Requirement: React Frontend Architecture Integration
The system SHALL integrate the complete React/Vite frontend from the forked directory into the main project structure to enable full-stack development.

#### Scenario: Frontend rescue and integration
- GIVEN the complete React frontend in the forked directory
- WHEN the consolidation operation moves frontend to main directory
- THEN the system SHALL preserve all frontend components and functionality
- AND the frontend SHALL maintain its modern React/Vite architecture
- AND the integration SHALL include all dependencies and build configurations
- AND the system SHALL update frontend configuration for new project structure

#### Scenario: Frontend component architecture preservation
- GIVEN the existing React component structure
- WHEN frontend is integrated with main project
- THEN the system SHALL maintain all existing components and their relationships
- AND the component architecture SHALL support the CrewAI agent workflows
- AND the frontend SHALL preserve current routing and state management
- AND the integration SHALL maintain all styling and UI/UX patterns

### Requirement: Frontend-Backend API Integration
The system SHALL establish comprehensive API integration between the React frontend and FastAPI backend to enable complete journal creation workflows.

#### Scenario: Authentication flow integration
- GIVEN the React frontend authentication components
- WHEN users attempt login or registration
- THEN the frontend SHALL authenticate with FastAPI backend endpoints
- AND the system SHALL maintain JWT token management in frontend state
- AND the authentication SHALL support API key configuration in settings
- AND the integration SHALL handle authentication errors and token refresh

#### Scenario: Journal creation workflow integration
- GIVEN users accessing journal creation features
- WHEN frontend initiates AI journal generation
- THEN the system SHALL connect to FastAPI AI generation endpoints
- AND the frontend SHALL provide real-time progress tracking via WebSocket
- AND the integration SHALL handle CrewAI agent coordination
- AND users SHALL interact with title selection and decision points through UI

### Requirement: Real-time Communication Integration
The system SHALL integrate WebSocket communication between React frontend and backend to provide live progress tracking and user interaction.

#### Scenario: WebSocket progress tracking
- GIVEN active AI generation jobs with multiple agent phases
- WHEN users view generation progress
- THEN the frontend SHALL establish WebSocket connections for real-time updates
- AND the system SHALL display current agent status and completion percentages
- AND users SHALL receive estimated time remaining and current stage descriptions
- AND the integration SHALL handle connection drops with automatic reconnection

#### Scenario: Interactive user decision handling
- GIVEN workflow stages requiring user input
- WHEN the system reaches decision points
- THEN the frontend SHALL present interactive options to users
- AND users SHALL select titles or make decisions through web interface
- AND the WebSocket integration SHALL communicate choices back to backend
- AND the system SHALL resume AI workflows based on user decisions

### Requirement: Frontend Development Environment
The system SHALL provide a unified development environment that supports both frontend and backend development with hot reloading and debugging.

#### Scenario: Development server integration
- GIVEN developers working on the unified project
- WHEN the development environment is started
- THEN the system SHALL provide hot reloading for both frontend and backend
- AND the development server SHALL support concurrent frontend and backend processes
- AND the environment SHALL include debugging tools for React components
- AND the integration SHALL enable seamless frontend-backend development workflow

#### Scenario: Build and deployment integration
- GIVEN the unified project requiring production deployment
- WHEN build processes are executed
- THEN the system SHALL build frontend assets and integrate with backend deployment
- AND the build process SHALL optimize frontend assets for production
- AND the deployment SHALL include both frontend and backend services
- AND the system SHALL provide health checks for both frontend and backend

### Requirement: User Interface Component Integration
The system SHALL integrate all user interface components necessary for complete journal platform functionality.

#### Scenario: Dashboard and project management interface
- GIVEN users accessing their project dashboard
- WHEN the frontend loads project management components
- THEN the system SHALL display user projects with status indicators
- AND users SHALL create new journals or continue existing projects
- AND the interface SHALL provide project search and filtering capabilities
- AND the dashboard SHALL integrate with backend project APIs

#### Scenario: Settings and API key management interface
- GIVEN users accessing account settings
- WHEN the settings interface is loaded
- THEN the frontend SHALL provide API key configuration options
- AND users SHALL add, update, or remove API keys with validation
- AND the interface SHALL display API key status and usage statistics
- AND the settings SHALL integrate with backend user management APIs

#### Scenario: Journal creation wizard interface
- GIVEN users initiating journal creation workflow
- WHEN the creation wizard interface is displayed
- THEN the frontend SHALL guide users through theme and style selection
- AND users SHALL provide input for research depth and author preferences
- AND the interface SHALL handle AI generation progress tracking
- AND users SHALL download completed journals in multiple formats

### Requirement: Error Handling and User Feedback Integration
The system SHALL provide comprehensive error handling and user feedback systems across the frontend-backend integration.

#### Scenario: Frontend error handling and recovery
- GIVEN errors occurring during frontend-backend interactions
- WHEN error conditions are detected
- THEN the frontend SHALL display user-friendly error messages
- AND the system SHALL provide options for error recovery or retry
- AND the interface SHALL log errors for debugging purposes
- AND users SHALL receive guidance for resolving common issues

#### Scenario: User feedback and notification system
- GIVEN various system events requiring user notification
- WHEN notifications need to be displayed
- THEN the frontend SHALL provide toast notifications for status updates
- AND the system SHALL display success messages for completed operations
- AND the interface SHALL show loading states during long-running operations
- AND users SHALL receive contextual help and guidance when needed