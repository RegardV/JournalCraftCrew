# CourseCraft Crew with #crew_ai
# Overview

Welcome to CourseCraft Crew, an innovative, AI-powered platform designed to create engaging self-help and self-improvement courses with minimal effort. Built using Crew AI, this modular, script-based setup automates the process of researching, developing, and deploying courses to Teachable. The first course we're crafting is "Journaling for Anxiety: Journaling to Calm Your Mind", serving as a proof-of-concept for a system that can adapt to any course topic.

The CourseCraft Crew is more than just code—it’s a journey to harness AI for education, led by a single creator (me!) with the help of Grok 3 from xAI. This repository documents my process, from initial setup to beta release, with plans to scale it under an LLC for future collaboration with industry-specific crews.

# Goals
Deliver a phased course-building process:
Phase 1: Text and image-based course.
Phase 2: Add audio components.
Phase 3: Produce and edit video content.
Create a flexible, reusable system that can build a wide variety of courses.
Ensure scalability for future enhancements or additional crews.

# Approach
I’m building this project in 4-hour sessions, every other day, starting March 3, 2025, aiming for a first beta by April 25, 2025. Here’s how I’m tackling it:

* Modular Design: Using separate script files for agents, tasks, and tools to keep things organized and adaptable.

* Hierarchical Workflow: A Manager Agent oversees three smaller crews (one per phase) for simplicity and efficiency.

* Self-Help Focus: Tools like PubMed API (research), VADER (sentiment analysis), and Grok 3 (content generation) ensure courses are evidence-based and motivational.

* Session-Based Progress: Each session builds on the last, with logs shared on X as #CourseCraftJourney to document my learning and engage the community.

* Work-Life Balance: Weekends off, with occasional double sessions when inspiration strikes.

# Progress
P1. Step 1: Setting up the project environment (Crew AI, tools) - March 3, 2025
Follow my journey on X with #CourseCraftJourney for real-time updates!

# TempCourseCraft Crew

Welcome to the CourseCraft Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/temp_course_craft/config/agents.yaml` to define your agents
- Modify `src/temp_course_craft/config/tasks.yaml` to define your tasks
- Modify `src/temp_course_craft/crew.py` to add your own logic, tools and specific args
- Modify `src/temp_course_craft/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the temp_course_craft Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The temp_course_craft Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the CourseCraft Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
