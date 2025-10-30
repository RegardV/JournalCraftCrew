# Onboarding Agent Web Interface Specification

## Purpose
Define requirements for creating a web-based interface for the onboarding agent that serves as the critical entry point for the CrewAI workflow, gathering user preferences and orchestrating the entire AI journal generation process.

## ADDED Requirements

### Requirement: Web-based Onboarding Flow
The system SHALL provide a complete web-based interface for the onboarding agent functionality that matches the existing CLI capabilities.

#### Scenario: User starts new journal creation
- GIVEN user is authenticated and wants to create a new journal
- WHEN user accesses the journal creation interface
- THEN system SHALL display onboarding agent web form
- AND user SHALL be able to enter journal theme
- AND user SHALL be able to enter preferred journal title
- AND system SHALL automatically format theme with "Journaling for" prefix if needed
- AND user SHALL see real-time validation feedback

#### Scenario: Dynamic author style selection
- GIVEN user has entered a journal theme
- WHEN system fetches author styles
- THEN system SHALL call LLM to get bestselling authors for the theme
- AND system SHALL display 5 author options with style descriptions
- AND user SHALL be able to select preferred writing style
- AND system SHALL provide fallback author styles if LLM fails

### Requirement: Title Style and Research Depth Selection
The system SHALL provide web-based selection interfaces for title styles and research depth options.

#### Scenario: Title style selection
- GIVEN user has completed theme and title entry
- WHEN presenting title style options
- THEN system SHALL display all available title styles from TITLE_STYLES
- AND user SHALL be able to select preferred title style via radio buttons or dropdown
- AND selected style SHALL be stored in user preferences

#### Scenario: Research depth selection
- GIVEN user has selected title style
- WHEN presenting research depth options
- THEN system SHALL display all research depth options with insight counts
- AND user SHALL be able to select preferred research depth
- AND system SHALL clearly show the number of insights for each depth level

### Requirement: Preference Management and Storage
The system SHALL manage user preferences gathered by the onboarding agent and store them for downstream agent workflows.

#### Scenario: Preference storage
- GIVEN user has completed onboarding form
- WHEN user submits preferences
- THEN system SHALL store all preferences in structured format
- AND system SHALL create unique project directory
- AND system SHALL associate preferences with authenticated user
- AND preferences SHALL be available for CrewAI agent workflow

#### Scenario: Preference retrieval and editing
- GIVEN user has existing projects
- WHEN user views project dashboard
- THEN system SHALL display existing projects with preferences
- AND user SHALL be able to edit preferences for existing projects
- AND system SHALL preserve project history with preference changes

### Requirement: Integration with CrewAI Workflow
The system SHALL seamlessly integrate web-collected preferences with the CrewAI agent workflow.

#### Scenario: Workflow initiation
- GIVEN user has completed onboarding preferences
- WHEN user initiates journal generation
- THEN system SHALL pass preferences to CrewAI workflow
- AND onboarding agent SHALL orchestrate workflow initialization
- AND system SHALL provide feedback that workflow has started

#### Scenario: Agent coordination
- GIVEN CrewAI workflow is in progress
- WHEN downstream agents need user preferences
- THEN system SHALL provide preferences from onboarding agent
- AND agents SHALL be able to access theme, title, style, and depth preferences
- AND workflow SHALL maintain preference consistency across all agents

### Requirement: Real-time Validation and Feedback
The system SHALL provide real-time validation and user feedback throughout the onboarding process.

#### Scenario: Form validation
- GIVEN user is filling out onboarding form
- WHEN user enters invalid data
- THEN system SHALL display inline validation errors
- AND system SHALL provide helpful error messages
- AND system SHALL prevent submission of incomplete forms

#### Scenario: Progress indication
- GIVEN user is completing onboarding process
- WHEN user navigates through form sections
- THEN system SHALL display progress indicators
- AND user SHALL know which steps are completed
- AND system SHALL provide clear next step guidance

## Technical Implementation Details

### Onboarding Form Structure
- **Theme Input**: Text input with automatic "Journaling for" formatting
- **Title Input**: Text input with validation for empty values
- **Title Style Selection**: Radio buttons or dropdown with TITLE_STYLES options
- **Research Depth Selection**: Cards showing depth options with insight counts
- **Author Style Selection**: Dynamic cards with author names and style descriptions
- **Progress Indicator**: Step-by-step progress bar
- **Submit Action**: Central call-to-action button

### API Integration
- **Dynamic Author Fetching**: API endpoint for LLM-based author style generation
- **Preference Storage**: API endpoints for storing and retrieving user preferences
- **Workflow Initiation**: API endpoint for starting CrewAI workflow with preferences
- **Validation Endpoints**: Real-time form validation API calls

### Error Handling
- **LLM Fallback**: Default author styles if dynamic fetching fails
- **Network Resilience**: Offline mode with cached preference options
- **Data Validation**: Client and server-side validation for all inputs
- **User Feedback**: Clear error messages and recovery options

## Success Metrics

- Onboarding completion rate > 90% for authenticated users
- Average onboarding time < 5 minutes
- User satisfaction with onboarding process > 85%
- Zero data loss in preference collection and storage
- Successful CrewAI workflow initiation from web interface > 95%
- Real-time validation effectiveness > 98% accuracy