from crewai import Agent
from tools.tools import BlogSummarySearchTool
import os
from datetime import datetime
from config.settings import VALID_RESEARCH_DEPTHS, LLM_SUBDIR, DATE_FORMAT
from utils import parse_llm_json, log_debug

def create_research_agent(llm):
    """Create a research agent to gather journaling insights."""
    return Agent(
        role="Research Specialist",
        goal="Gather unique, theme-specific journaling insights based on user-specified depth",
        backstory="""I’m a diligent researcher who dives into journaling themes, pulling rich, varied insights from diverse sources.""",
        tools=[BlogSummarySearchTool()],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def research_content(self, theme: str, depth: str, run_dir: str):
    """Gather research content based on theme and user-specified depth."""
    timestamp = datetime.now().strftime(DATE_FORMAT)
    output_dir = os.path.join(run_dir, LLM_SUBDIR)
    os.makedirs(output_dir, exist_ok=True)
    research_file = os.path.join(output_dir, f"research_output_{timestamp}.txt")

    theme_part = theme.split(" for ")[1] if " for " in theme else theme
    research_prompt = (
        "Generate 25 unique journaling insights for '" + theme + "' based on blogs, books, and studies. "
        "Each insight should have a 'technique' (e.g., '" + theme_part + " Insight 1') and a 'description' (50–100 words). "
        "Ensure variety: include historical context, psychological benefits, and actionable tips. "
        "Output as a JSON list of dictionaries."
    )
    log_debug(f"Sending research prompt for theme '{theme}' with depth '{depth}'")
    try:
        research_data = parse_llm_json(self.llm, research_prompt, output_dir, f"research_output_{timestamp}.txt")
        max_insights = VALID_RESEARCH_DEPTHS.get(depth, VALID_RESEARCH_DEPTHS["deep"])
        result = research_data[:max_insights] if max_insights < len(research_data) else research_data
        log_debug(f"Research completed with {len(result)} insights")
        return result
    except Exception as e:
        log_debug(f"Failed to parse research response: {e} - Saved to {research_file}")
        return []