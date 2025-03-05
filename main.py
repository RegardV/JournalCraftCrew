# ~/crewprojects/coursecraft_crew/main.py
import os
from dotenv import load_dotenv
from langchain_community.llms import Grok  # Import Grok LLM
from agents.manager_agent import create_manager_agent  # Import the function
from crewai import Crew, Task

# Load environment variables from .env
load_dotenv()

# Retrieve the xAI API key
xai_api_key = os.getenv("XAI_API_KEY")

# Create the Grok LLM instance
llm = Grok(api_key=xai_api_key, model="grok-3")  # Adjust model name if needed

# Create the Manager Agent with the Grok LLM
manager_agent = create_manager_agent(llm)

# Define a simple task for the Manager Agent
task = Task(
    description="Coordinate the CourseCraft Crew to plan a self-help course on journaling for anxiety",
    agent=manager_agent
)

# Set up the Crew with the Manager Agent and the task
crew = Crew(
    agents=[manager_agent],
    tasks=[task],
    verbose=2  # Detailed logging
)

# Run the crew
crew.kickoff()