# ~/crewprojects/coursecraft_crew/agents/manager_agent.py
from crewai import Agent
from tools.tools import duckdb_tool  # Assuming DuckDB tool is defined in tools.py

# Function to create the Manager Agent, accepting an LLM parameter
def create_manager_agent(llm):
    return Agent(
        role="Manager",
        goal="Orchestrate CourseCraft Crew operations across all phases to create engaging self-help courses",
        backstory="As the backbone of the CourseCraft Crew, I’m designed to coordinate three phase-specific crews, ensuring seamless task delegation, progress tracking, and phase transitions. With a keen eye on operational tools like DuckDB and Apache Airflow, I keep the project on track from research to deployment.",
        tools=[duckdb_tool],  # Tools for data coordination; expand as needed
        verbose=True,  # Enables detailed logging for monitoring
        memory=True,  # Allows the agent to retain context across interactions
        llm=llm  # Use the LLM passed from main.py
    )

# Optional: Add a method or logic for coordination (to be expanded later)
def coordinate_phases():
    print("Manager Agent: Coordinating tasks across Phase 1, Phase 2, and Phase 3 crews...")
    # Future logic: Delegate tasks, monitor progress, handle transitions
    pass

if __name__ == "__main__":
    # Optional test block for standalone testing
    from langchain_community.llms import Grok
    test_llm = Grok(api_key="your-test-key", model="grok-3")  # Replace with a test key
    manager_agent = create_manager_agent(test_llm)
    print(f"Manager Agent Role: {manager_agent.role}")
    print(f"Manager Agent Goal: {manager_agent.goal}")
    coordinate_phases()