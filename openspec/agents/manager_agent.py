# Manager Agent Specification

## Purpose
Orchestrates the journal processing workflow by coordinating between specialized agents.

## Requirements

### Requirement: Agent Coordination
The manager agent SHALL coordinate the journal processing workflow.

#### Scenario: Valid journal entry
- GIVEN a user journal entry
- WHEN the manager receives the entry
- THEN it SHALL delegate tasks to specialized agents
- AND collect their outputs
- AND produce a final result

### Requirement: Error Handling
The manager agent MUST handle agent failures gracefully.

#### Scenario: Agent failure
- WHEN a specialized agent fails
- THEN the manager SHALL log the error
- AND attempt retry with fallback
- AND notify the user of the issue

## Agent Configuration

**Role:** Manager
**Goal:** Coordinate journal processing workflow efficiently
**Backstory:** Expert orchestrator of AI agent teams

## Tools
- DuckDBTool (for data queries)
- Coordination tools (built-in)