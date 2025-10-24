#!/bin/bash
# Setup OpenSpec for JournalCraftCrew
# Run this from: ~/Documents/7.CodeProjects/Journal Craft Crew/openspec/

set -e  # Exit on error

echo "🚀 Setting up OpenSpec specifications for JournalCraftCrew..."

# We're already in openspec/, so create subdirectories
echo "📁 Creating spec directories..."
mkdir -p specs/system
mkdir -p specs/agents
mkdir -p specs/workflows
mkdir -p specs/data

# Create System Overview
echo "📝 Creating system overview spec..."
cat > specs/system/overview.md << 'EOF'
# JournalCraftCrew System Overview

## Purpose
Multi-agent AI system for automated journal entry processing, analysis, and content generation.

## Requirements

### Requirement: Multi-Agent Coordination
The system SHALL coordinate multiple specialized agents to process journal entries.

#### Scenario: Process journal entry
- GIVEN a user journal entry
- WHEN processing is initiated
- THEN agents SHALL work collaboratively
- AND results SHALL be synthesized
- AND final output SHALL be generated
EOF

# Create Manager Agent spec
echo "📝 Creating manager agent spec..."
cat > specs/agents/manager-agent.md << 'EOF'
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
EOF

# Create Workflow spec
echo "📝 Creating journal processing workflow spec..."
cat > specs/workflows/journal-processing.md << 'EOF'
# Journal Entry Processing Workflow

## Purpose
Define the end-to-end workflow for processing journal entries.

## Requirements

### Requirement: Entry Processing Pipeline
The system SHALL process journal entries through multiple stages.

#### Scenario: Complete processing
- GIVEN user submits raw journal entry
- WHEN processing is initiated
- THEN entry SHALL be validated
- AND sentiment analysis SHALL be performed
- AND NLP processing SHALL extract entities
- AND PDF SHALL be generated
EOF

# Create README
cat > specs/README.md << 'EOF'
# JournalCraftCrew Specifications

## Structure
- `system/` - System-level specifications
- `agents/` - Individual agent specifications
- `workflows/` - Workflow specifications
- `data/` - Data schemas

## Agents
See `agents/` directory for individual agent specifications.
EOF

echo ""
echo "✅ OpenSpec specs created successfully!"
echo ""
echo "📋 Created files:"
tree specs/ || ls -la specs/
echo ""