## ADDED Requirements

### Requirement: CrewAI Workflow Execution with Timeout Protection
The system SHALL execute CrewAI multi-agent workflows with real OpenAI API integration and timeout protection.

#### Scenario: Successful CrewAI execution
- **WHEN** user initiates journal creation with valid API key
- **THEN** system executes real CrewAI workflow with `crew.kickoff()`
- **AND** applies 10-minute timeout protection using `asyncio.wait_for()`
- **AND** provides real-time progress updates via WebSocket

#### Scenario: OpenAI API error handling
- **WHEN** CrewAI execution encounters OpenAI API errors
- **THEN** system detects specific error types (rate limits, auth failures, quota exceeded)
- **AND** provides user-friendly error messages for each error type
- **AND** fails gracefully without exposing sensitive information

### Requirement: Secure API Key Handling
The system SHALL protect API keys from exposure in browser console logs.

#### Scenario: Secure WebSocket logging
- **WHEN** WebSocket messages are logged for debugging
- **THEN** system logs only non-sensitive fields (type, status, agent)
- **AND** removes API keys and other sensitive data from console output
- **AND** maintains debugging capability without security risks

### Requirement: Enhanced Research Content Generation
The system SHALL generate comprehensive, topic-specific research content for CrewAI agents.

#### Scenario: Research tool content generation
- **WHEN** CrewAI research agent requests information about a journaling topic
- **THEN** system generates 683+ characters of comprehensive research content
- **AND** content includes evidence-based benefits, practical techniques, and scientific findings
- **AND** content is unique for each different journaling topic

## MODIFIED Requirements

### Requirement: AI Workflow Progress Visualization
The system SHALL display real-time progress of CrewAI agent execution with enhanced UI constraints and security.

#### Scenario: CLI progress container constraints
- **WHEN** CrewAI progress visualization is displayed
- **THEN** CLI container respects strict height constraints with `max-h-full overflow-hidden`
- **AND** content scrolls properly within fixed boundaries
- **AND** prevents modal expansion beyond 85vh viewport height

#### Scenario: Enhanced journal library identification
- **WHEN** users view journal library cards
- **THEN** cards display theme and style information beyond generic "Journal Entry" titles
- **AND** include author style and title style for better identification
- **AND** provide descriptive titles based on theme and preferences
