# Journal Craft Crew System Overview

## Purpose
AI-powered journal creation platform that combines multi-agent AI coordination with modern web interfaces to enable users to create personalized journals through sophisticated AI-guided workflows.

## System Architecture

### Technology Stack
- **Backend Framework**: FastAPI (Python) with async/await patterns
- **Multi-Agent System**: CrewAI framework for specialized AI agent coordination
- **Authentication**: JWT tokens with industry-standard security patterns
- **Real-time Communication**: WebSocket connections for live progress tracking
- **Data Persistence**: JSON file storage (development) designed for database migration
- **Document Generation**: Professional PDF creation with media integration
- **Deployment**: Uvicorn ASGI server with Docker containerization

### Component Architecture
- **API Layer**: RESTful endpoints with JWT middleware protection
- **Agent Coordination Layer**: Manager Agent orchestrating 8 specialized agents
- **Background Processing**: Async job system with Redis fallback for state management
- **File Management**: User-isolated storage with organized project structures
- **WebSocket Layer**: Real-time progress updates and user interaction handling

## Requirements

### Requirement: Multi-Agent AI Coordination System
The system SHALL coordinate 8 specialized CrewAI agents through a Manager Agent to create comprehensive journal content.

#### Scenario: Complete journal creation workflow
- GIVEN an authenticated user with valid API key configuration
- WHEN user initiates journal creation with preferences
- THEN the Manager Agent SHALL orchestrate sequential agent execution
- AND the Onboarding Agent SHALL collect user preferences (theme, style, research depth)
- AND the Discovery Agent SHALL generate multiple title options based on preferences
- AND the Research Agent SHALL gather theme-specific insights from multiple sources
- AND the Content Curator Agent SHALL create 30-day journal and 6-day lead magnet
- AND the Editor Agent SHALL refine content for quality and consistency
- AND the Media Agent SHALL generate AI images for journal elements
- AND the PDF Builder Agent SHALL create professional documents with integrated media
- AND users SHALL receive real-time progress updates throughout the process

#### Scenario: Agent coordination and error handling
- GIVEN the multi-agent workflow execution
- WHEN individual agents encounter errors or processing delays
- THEN the Manager Agent SHALL implement retry logic and error recovery
- AND the system SHALL maintain job state across agent failures
- AND users SHALL receive clear error messages and recovery options
- AND the system SHALL provide workflow continuation from failed states

### Requirement: Secure Authentication and User Management
The system SHALL provide comprehensive authentication with JWT tokens and secure API key management.

#### Scenario: User authentication flow
- GIVEN a new user accessing the platform
- WHEN user completes registration with email, username, and password
- THEN the system SHALL create secure accounts with bcrypt password hashing
- AND users SHALL receive JWT access and refresh tokens for session management
- AND the system SHALL implement session expiration and automatic refresh
- AND authentication SHALL follow WCAG 2.2 AA accessibility standards

#### Scenario: API key management in settings
- GIVEN an authenticated user in settings area
- WHEN user configures OpenAI API key for AI features
- THEN the system SHALL validate API key format and connectivity
- AND keys SHALL be encrypted and stored securely
- AND users SHALL receive real-time API key status indicators
- AND the system SHALL provide clear guidance for API key acquisition

### Requirement: Real-time Progress Tracking System
The system SHALL provide WebSocket-based real-time communication for progress tracking and user interaction.

#### Scenario: Live generation progress tracking
- GIVEN an active journal generation job with multiple agent phases
- WHEN the system processes through agent workflows
- THEN users SHALL receive real-time progress updates via WebSocket
- AND the system SHALL display current agent status and completion percentages
- AND users SHALL see estimated time remaining for completion
- AND the system SHALL handle connection drops with automatic reconnection

#### Scenario: Interactive user decision points
- GIVEN the Discovery Agent generates multiple title options
- WHEN user selection is required for workflow continuation
- THEN the system SHALL pause execution and present title options
- AND users SHALL select preferred titles via the web interface
- AND the system SHALL resume workflow based on user decisions
- AND WebSocket connections SHALL facilitate real-time user interactions

### Requirement: Professional Document Generation System
The system SHALL generate professional journal documents with advanced formatting and media integration.

#### Scenario: Multi-format document export
- GIVEN completed journal content with optional media assets
- WHEN user requests document export
- THEN the PDF Builder Agent SHALL create professional 30-day journals
- AND the system SHALL generate 6-day lead magnets for marketing
- AND documents SHALL include high-quality typography with DejaVu Sans fonts
- AND AI-generated images SHALL be integrated with proper layout and placement
- AND users SHALL receive downloads in PDF, EPUB, and KDP formats

#### Scenario: Media integration and quality
- GIVEN generated journal content requiring visual elements
- WHEN the Media Agent processes image requirements
- THEN the system SHALL generate theme-appropriate images using AI services
- AND images SHALL be optimized for PDF integration and print quality
- AND the system SHALL maintain consistent visual styling throughout documents
- AND fallback placeholder images SHALL be available when AI generation fails

### Requirement: Scalable Backend Infrastructure
The system SHALL provide a scalable FastAPI backend with comprehensive API endpoints and background processing.

#### Scenario: API endpoint architecture
- GIVEN the FastAPI application serving multiple user requests
- WHEN users interact with platform features
- THEN the system SHALL provide 12+ comprehensive API endpoints
- AND authentication SHALL protect all sensitive endpoints with JWT middleware
- AND the system SHALL include automatic OpenAPI documentation at /docs
- AND rate limiting SHALL protect against abuse and ensure fair usage

#### Scenario: Background job processing
- GIVEN multiple users simultaneously requesting AI generation
- WHEN the system manages background job queues
- THEN jobs SHALL be processed with proper prioritization and resource allocation
- AND the system SHALL maintain job state and progress tracking
- AND Redis SHALL provide job persistence with in-memory fallback
- AND users SHALL be able to cancel, pause, and resume background jobs
