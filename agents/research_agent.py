#research_agent.py
from crewai import Agent
from tools.tools import BlogSummarySearchTool
import json
import os

def create_research_agent(llm):
    """
    Creates a Research Agent to gather data for themed journaling guides.

    Args:
        llm: The language model instance (e.g., xai/grok-2-1212) to power the agent.

    Returns:
        Agent: A configured CrewAI Agent instance for researching journaling themes.
    """
    return Agent(
        role="Research Specialist",
        goal="Gather journaling insights for a 4-week themed guide with two outputs (self-print PDF and book PDF/EPUB/KDP), ensuring originality",
        backstory="""I’m an expert at sourcing practical journaling insights from blog posts summarizing books and direct book inspiration, 
        reformulating them to avoid plagiarism. My work supports a 4-week guide—self-print PDF with daily spreads (left pre-writeup, right prompt 
        with lines) and book PDF/EPUB/KDP with image placeholders before each day’s spread (left pre-writeup, right prompt with lines)—plus an 
        intro, commitment, and certificate celebrating growth.""",
        tools=[BlogSummarySearchTool()],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def save_json(data, filepath):
    """Utility to save data as JSON."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def research_content(self, theme: str, output_file: str):
    """Gather and save research data for the theme."""
    summary = self.tools[0]._run(f"journaling techniques for {theme.lower()} management")
    full_data = [
        {"technique": "Immediate Journaling", "description": "Start journaling when anxiety hits to process emotions in real-time."},
        {"technique": "Daily Anxiety Journaling", "description": "Write daily to lighten your emotional load."},
        {"technique": "Weekend Reflection", "description": "Use weekend prompts to find peace and reflect."},
        {"technique": "Identifying Triggers", "description": "Note specific anxiety triggers for better management."},
        {"technique": "Coping Mechanisms", "description": "Document strategies to cope with anxiety."}
    ]
    save_json(full_data, output_file)
    return summary