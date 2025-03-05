# CourseCraft Crew with #crew_ai
# Overview

Welcome to CourseCraft Crew, an innovative, AI-powered platform designed to create engaging self-help and self-improvement courses with minimal effort. Built using Crew AI, this modular, script-based setup automates the process of researching, developing, and deploying courses to Teachable. The first course we're crafting is "Journaling for Anxiety: Journaling to Calm Your Mind", serving as a proof-of-concept for a system that can adapt to any course topic.

The CourseCraft Crew is more than just code—it’s a journey to harness AI for education, led by a single creator (me!) with the help of Grok 3 from xAI. This repository documents my process, from initial setup to beta release, with plans to scale it under an LLC for future collaboration with industry-specific crews.

# Goals
- Deliver a phased course-building process:
  - Phase 1: Text and image-based course.
  - Phase 2: Add audio components.
  - Phase 3: Produce and edit video content.
- Create a flexible, reusable system that can build a wide variety of courses.
- Ensure scalability for future enhancements or additional crews.

# Approach
I’m building this project in 4-hour sessions, every other day, starting March 3, 2025, aiming for a first beta by April 25, 2025. Here’s how I’m tackling it:

- **Modular Design**: Using separate script files for agents, tasks, and tools in directories like `agents/`, `tasks/`, `crews/`, and `tools/` to keep things organized and adaptable.
- **Hierarchical Workflow**: A Manager Agent oversees three smaller crews (one per phase) for simplicity and efficiency, with execution driven by `main.py`.
- **Self-Help Focus**: Tools like PubMed API (research), VADER (sentiment analysis), and Grok 3 (content generation) ensure courses are evidence-based and motivational.
- **Session-Based Progress**: Each session builds on the last, with logs in `developmentlogs/` shared on X as #CourseCraftJourney to document my learning and engage the community.
- **Work-Life Balance**: Weekends off, with occasional double sessions when inspiration strikes.

# Progress
- P1. Step 1: Setting up the project environment (Crew AI, tools) - March 3, 2025
- P1. Step 2: Reviewed crew structure and finalized setup (Option 2) - March 5, 2025
- P2. Step 1: Defined Manager Agent’s role and responsibilities (early) - March 5, 2025
Follow my journey on X with #CourseCraftJourney for real-time updates!

# Structure 
All files have been created but they are still blank. As I complete them I will mark it here
The scripts folder contains a script that would replicate this setup as a template. All files are still blank. 

~/crewprojects/coursecraft_crew/
├── agents/
│   ├── content_curator_agent.py
│   ├── editor_agent.py
│   ├── iteration_agent.py
│   ├── manager_agent.py
│   ├── media_production_agent.py
│   ├── platform_setup_agent.py
│   ├── research_agent.py
├── config/
│   └── settings.py
├── crews/
│   ├── phase1_crew.py
│   ├── phase2_crew.py
│   ├── phase3_crew.py
├── developmentlogs/
│   ├── session1_log.txt
│   ├── session2_log.txt
├── .env
├── .gitignore 
├── knowledge/
│   └── user_preference.txt
├── main.py
├── pyproject.toml
├── README.md
├── requirements.txt
├── scripts/
│   └── SetupDirAndTemplatefiles.py - # Setup base template of folders and files like this tree
├── src/
│   └── crew_config.md
├── tasks/
│   ├── manager_tasks.py
│   ├── phase1_tasks.py
│   ├── phase2_tasks.py
│   ├── phase3_tasks.py
├── tools/
│   └── tools.py

## Manager Agent Role
Defined early on March 5, 2025 (P2. Step 1):
- **Task Delegation**: Assigns jobs (e.g., research to Phase 1 crew).
- **Progress Monitoring**: Tracks completion across phases.
- **Phase Transitions**: Hands off outputs (e.g., text from Phase 1 to Phase 2).
- **Tool Coordination**: Manages DuckDB, Apache Airflow for operational efficiency.
See `agents/manager_agent.py` for implementation details.

## Crew Structure
Using multiple crews for modularity, finalized on March 5, 2025 (P1. Step 2):
- **Phase 1 Crew (Text/Images)**: Research Agent, Content Curator Agent, Editor Agent. See `crews/phase1_crew.py`.
- **Phase 2 Crew (Audio)**: Media Production Agent, Platform Setup Agent. See `crews/phase2_crew.py`.
- **Phase 3 Crew (Video)**: Media Production Agent, Platform Setup Agent, Iteration Agent. See `crews/phase3_crew.py`.
Coordinated by the Manager Agent for seamless phase transitions.

## Project Schedule
Mar 3, 2025  Mon  Set up project environment (e.g., Crew AI, tools)              P1. Step 1  
Mar 5, 2025  Wed  Review crew structure and finalize setup (Option 2)        P1. Step 2  
Mar 7, 2025  Fri  Define Manager Agent’s role and responsibilities           P2. Step 1  
Mar 10, 2025 Mon  Map agents’ roles for Phase 1 (text/images)                P2. Step 2  
Mar 12, 2025 Wed  Propose modular folder structure and script outlines       P3. Step 1  
Mar 14, 2025 Fri  Confirm agent setup and roles per phase                    P4. Step 1  
Mar 17, 2025 Mon  Build Research Agent (Phase 1)                             P2. Step 2  
Mar 19, 2025 Wed  Build Content Curator Agent (Phase 1)                      P2. Step 2  
Mar 21, 2025 Fri  Build Editor Agent (Phase 1)                               P2. Step 2  
Mar 24, 2025 Mon  Integrate Phase 1 agents and test data flow                P5. Step 2  
Mar 26, 2025 Wed  Build Media Production Agent (Phase 2 - Audio)             P2. Step 2  
Mar 28, 2025 Fri  Build Platform Setup Agent for Phase 2 integration         P2. Step 2  
Mar 31, 2025 Mon  Test Phase 2 (audio) and refine based on feedback          P5. Step 2  
Apr 2, 2025  Wed  Build Media Production Agent (Phase 3 - Video)             P2. Step 2  
Apr 4, 2025  Fri  Build Iteration Agent for cross-phase feedback             P2. Step 2  
Apr 7, 2025  Mon  Integrate Phase 3 agents and test video output             P5. Step 2  
Apr 9, 2025  Wed  Set up operational tools (e.g., DuckDB, LangSmith)         P5. Step 1  
Apr 11, 2025 Fri  Configure Manager Agent’s workflow automation             P5. Step 1  
Apr 14, 2025 Mon  Test Manager Agent’s coordination across phases            P5. Step 1  
Apr 16, 2025 Wed  Refine agents based on test results                       P6. Step 1  
Apr 18, 2025 Fri  Add post-launch agents (Marketing, Engagement)             P2. Step 2  
Apr 21, 2025 Mon  Finalize integrations and prepare for beta testing         P6. Step 1  
Apr 23, 2025 Wed  Conduct stress tests on the full system                    P6. Step 1  
Apr 25, 2025 Fri  Launch first beta and share milestone on X                 P6. Step 2  

## Installation
Once the Project has been completed I will complete this section 



