## ADDED Requirements

### Requirement: Unified CrewAI-Powered Journal Creation
The system SHALL provide a single, comprehensive journal creation workflow powered by all 9 CrewAI agents, eliminating duplicate or mock implementations.

#### Scenario: User initiates journal creation through unified interface
- **WHEN** user accesses journal creation from any entry point
- **THEN** system SHALL present the same CrewAI-powered onboarding workflow
- **AND** user SHALL have access to all 9 CrewAI agents with clear value propositions
- **AND** system SHALL provide progressive disclosure of agent capabilities

#### Scenario: System routes all journal creation through CrewAI workflow
- **WHEN** any request for journal creation is received
- **THEN** system SHALL process through unified `/api/crewai/start-workflow` endpoint
- **AND** system SHALL eliminate all mock AI generation implementations
- **AND** system SHALL provide consistent progress tracking across all workflows

### Requirement: Agent-Centric Progress Tracking
The system SHALL provide real-time progress tracking based on CrewAI agent phases with subtask-level precision and meaningful milestones.

#### Scenario: User monitors journal creation progress
- **WHEN** CrewAI workflow is executing
- **THEN** system SHALL display progress organized by agent phases
- **AND** each agent SHALL show 5 detailed subtask steps with completion percentages
- **AND** system SHALL provide estimated completion times and milestone celebrations

#### Scenario: System communicates agent status updates
- **WHEN** an agent completes a subtask or phase
- **THEN** system SHALL send structured WebSocket messages with agent context
- **AND** system SHALL provide notifications for agent start, progress, completion, and errors
- **AND** system SHALL maintain connection health with heartbeat monitoring

### Requirement: Project Continuation and State Management
The system SHALL enable users to continue incomplete projects by analyzing existing state and executing appropriate CrewAI agents to complete missing components.

#### Scenario: User resumes incomplete journal project
- **WHEN** user accesses existing incomplete project
- **THEN** system SHALL analyze project state and identify missing components
- **AND** system SHALL present specific continuation options based on what's incomplete
- **AND** system SHALL execute only the necessary CrewAI agents to complete the project

#### Scenario: System manages project state and workflow history
- **WHEN** project is paused, resumed, or encounters errors
- **THEN** system SHALL maintain complete state information and workflow history
- **AND** system SHALL enable workflow interruption and resumption at any agent phase
- **AND** system SHALL provide rollback options and error recovery mechanisms

### Requirement: Workflow Type Selection and Customization
The system SHALL provide workflow type options to match user needs, from express creation to comprehensive professional journal development.

#### Scenario: User selects workflow type during onboarding
- **WHEN** user begins journal creation process
- **THEN** system SHALL offer workflow options: express, standard, comprehensive, advanced
- **AND** each option SHALL clearly indicate which CrewAI agents will be executed
- **AND** system SHALL provide estimated time and complexity for each workflow type

#### Scenario: Advanced user customizes agent behavior
- **WHEN** advanced user selects comprehensive or advanced workflow
- **THEN** system SHALL provide options to customize agent parameters and behavior
- **AND** user SHALL be able to configure research depth, style intensity, and output formats
- **AND** system SHALL validate customizations and provide recommendations

## MODIFIED Requirements

### Requirement: Multi-Step Onboarding Process
The system SHALL provide a comprehensive onboarding process that collects user preferences while introducing CrewAI agent capabilities and workflow options.

#### Scenario: User completes enhanced onboarding with agent previews
- **WHEN** user progresses through onboarding steps
- **THEN** system SHALL collect theme, title, style, and research depth preferences
- **AND** system SHALL introduce relevant CrewAI agents and their roles
- **AND** system SHALL provide dynamic author style selection with LLM integration
- **AND** user SHALL understand which agents will execute and their expected contributions

#### Scenario: System validates onboarding preferences and sets up workflow
- **WHEN** user completes onboarding preferences
- **THEN** system SHALL validate all inputs and provide real-time feedback
- **AND** system SHALL create project directory and initialize workflow state
- **AND** system SHALL route to appropriate CrewAI workflow based on selections
- **AND** system SHALL provide clear next steps and timeline expectations

### Requirement: Real-Time Progress Monitoring
The system SHALL provide comprehensive real-time monitoring of CrewAI workflow execution with agent-specific progress, WebSocket communication, and detailed status updates.

#### Scenario: User views detailed agent progress during execution
- **WHEN** CrewAI workflow is active
- **THEN** system SHALL display real-time progress for each executing agent
- **AND** progress SHALL include current subtask, completion percentage, and next steps
- **AND** system SHALL provide agent-specific messages and achievement notifications
- **AND** user SHALL have access to workflow pause, resume, and cancellation controls

#### Scenario: System handles WebSocket communication and connection management
- **WHEN** user is monitoring active workflow
- **THEN** system SHALL maintain WebSocket connection with heartbeat monitoring
- **AND** system SHALL provide connection recovery and message replay capabilities
- **AND** system SHALL handle connection drops gracefully with automatic reconnection
- **AND** system SHALL provide fallback polling when WebSocket is unavailable

## REMOVED Requirements

### Requirement: Multiple Journal Creation Workflows
**Reason**: Eliminates user confusion and technical complexity by consolidating to single CrewAI-powered workflow.
**Migration**: All users will be routed through unified onboarding to CrewAI workflow regardless of entry point.

#### Scenario: Multiple workflow confusion (REMOVED)
- ~~**WHEN** user accesses journal creation from different entry points~~
- ~~**THEN** system presents different workflows: CrewAI, simple AI, basic~~
- ~~**AND** user experiences inconsistent interfaces and capabilities~~

### Requirement: Mock AI Generation System
**Reason**: Removes technical debt and provides all users with access to real CrewAI agents.
**Migration**: Mock system endpoints will be redirected to real CrewAI workflow with appropriate parameters.

#### Scenario: Mock AI generation (REMOVED)
- ~~**WHEN** user selects simple journal creation option~~
- ~~**THEN** system executes mock AI generation with simulated progress~~
- ~~**AND** user receives generic journal content without CrewAI agent benefits~~

### Requirement: Basic Journal Creation Without AI
**Reason**: All journals should benefit from AI assistance while maintaining user choice for simplicity.
**Migration**: Basic workflow becomes express CrewAI workflow with essential agents only.

#### Scenario: Basic journal creation (REMOVED)
- ~~**WHEN** user chooses simple journal creation~~
- ~~**THEN** system creates journal without AI assistance or agent coordination~~
- ~~**AND** user receives template-based content without personalization~~