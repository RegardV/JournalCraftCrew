## ADDED Requirements

### Requirement: Journal Creation API Endpoint
The backend SHALL provide a REST API endpoint for starting journal creation processes with the CrewAI system.

#### Scenario: Journal creation request
- **WHEN** a frontend component sends a POST request to `/api/journals/create`
- **THEN** the system SHALL validate the request and create a unique job ID
- **AND** start the CrewAI workflow process in the background
- **AND** return the job ID and initial status to the frontend

#### Scenario: Journal creation preferences
- **WHEN** creating a journal
- **THEN** the system SHALL accept preferences for theme, title, author style, research depth
- **AND** convert web format preferences to CrewAI agent format
- **AND** store preferences with the job for workflow execution

### Requirement: Real-time Progress WebSocket
The backend SHALL provide WebSocket connections for real-time progress tracking during journal creation.

#### Scenario: Progress updates
- **WHEN** CrewAI agents complete tasks
- **THEN** the system SHALL broadcast progress updates via WebSocket
- **AND** include current agent, progress percentage, and status messages
- **AND** provide estimated time remaining for completion

#### Scenario: WebSocket connection management
- **WHEN** frontend connects to `/ws/journal/{job_id}`
- **THEN** the system SHALL authenticate the connection
- **AND** manage multiple connections per job
- **AND** handle connection cleanup and heartbeat monitoring

### Requirement: File Download API
The backend SHALL provide secure file access for completed journal projects.

#### Scenario: File download request
- **WHEN** a user requests a file download
- **THEN** the system SHALL validate user permissions for the file
- **AND** serve the file with appropriate download headers
- **AND** log the download action for audit purposes

#### Scenario: Project file listing
- **WHEN** accessing a project's files
- **THEN** the system SHALL return a structured list of available files
- **AND** include file metadata (size, type, creation date)
- **AND** organize files by type (PDFs, media, data files)

## MODIFIED Requirements

### Requirement: Project Library API Enhancement
The existing `/api/library/llm-projects` endpoint SHALL be enhanced to provide comprehensive project data.

#### Scenario: Comprehensive project data
- **WHEN** fetching the library
- **THEN** the system SHALL return complete project metadata
- **AND** include file listings, progress status, and completion information
- **AND** organize projects by creation date and status

#### Scenario: Real-time project updates
- **WHEN** projects are created or updated
- **THEN** the library API SHALL reflect changes immediately
- **AND** provide consistent data across multiple requests
- **AND** handle concurrent access to project data

### Requirement: Authentication Integration
All new API endpoints SHALL integrate with the existing JWT authentication system.

#### Scenario: Endpoint security
- **WHEN** accessing journal creation or file endpoints
- **THEN** the system SHALL require valid JWT authentication
- **AND** validate user permissions for specific resources
- **AND** return appropriate error responses for unauthorized access

#### Scenario: WebSocket authentication
- **WHEN** establishing WebSocket connections
- **THEN** the system SHALL authenticate via token parameter
- **AND** associate connections with user accounts
- **AND** enforce job ownership rules

## REMOVED Requirements

### Requirement: Static Data Responses
All API endpoints SHALL return dynamic data from the actual system state rather than static or mock responses.

#### Scenario: Real data integration
- **WHEN** API endpoints are called
- **THEN** the system SHALL query actual file system and database
- **AND** return current system state
- **AND** reflect real-time changes in the data