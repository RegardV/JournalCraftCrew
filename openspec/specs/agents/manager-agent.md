# Manager Agent Specification

## Purpose
Orchestrate the journal processing workflow by coordinating all specialized agents.

## Requirements

### Requirement: Workflow Orchestration
The manager agent SHALL coordinate task distribution across all specialized agents.

#### Scenario: Process journal entry
- GIVEN a valid journal entry from user
- WHEN processing begins
- THEN manager SHALL assign tasks to appropriate agents
- AND monitor progress of each agent
- AND collect results from all agents
