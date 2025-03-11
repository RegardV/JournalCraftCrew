#!/bin/bash

# Set project root
PROJECT_DIR=~/crewprojects/coursecraft_crew

# Navigate to project root
cd "$PROJECT_DIR" || { echo "Directory $PROJECT_DIR not found!"; exit 1; }

# Create directories if they don’t exist
mkdir -p agents tasks crews tools config

# Create blank .py files in agents/
touch agents/manager_agent.py
touch agents/research_agent.py
touch agents/content_curator_agent.py
touch agents/editor_agent.py
touch agents/media_production_agent.py
touch agents/platform_setup_agent.py
touch agents/iteration_agent.py

# Create blank .py files in tasks/
touch tasks/phase1_tasks.py
touch tasks/phase2_tasks.py
touch tasks/phase3_tasks.py
touch tasks/manager_tasks.py

# Create blank .py files in crews/
touch crews/phase1_crew.py
touch crews/phase2_crew.py
touch crews/phase3_crew.py

# Create blank .py file in tools/
touch tools/tools.py

# Create blank .py file in config/
touch config/settings.py

# Create blank .py file at root
touch main.py

echo "All .py files created/overwritten in $PROJECT_DIR"
ls -lR | grep '\.py'  # Show only .py files in the structure