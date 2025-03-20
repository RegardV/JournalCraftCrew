from crewai import Agent
import os
from datetime import datetime
from config.settings import LLM_SUBDIR, DATE_FORMAT
from utils import parse_llm_json, log_debug

def create_discovery_agent(llm):
    """Create a discovery agent to generate unique title ideas."""
    return Agent(
        role="Discovery Specialist",
        goal="Generate unique title ideas for a journaling guide based on theme and style",
        backstory="""I’m a creative spark, crafting evocative titles that set the tone for journaling journeys.""",
        tools=[],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def discover_idea(self, theme: str, title_style: str):
    """Generate title ideas based on theme and title style."""
    output_dir = os.path.join(os.getcwd(), LLM_SUBDIR, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(output_dir, exist_ok=True)
    prompt = (
        "Generate 10 unique title ideas for a '" + theme + "' journaling guide in a '" + title_style + "' style. "
        "Provide 5 SEO-optimized titles under 'titles' and 5 style-influenced titles under 'styled_titles'. "
        "Ensure the output is a valid JSON object, e.g., {'titles': ['Title 1', ...], 'styled_titles': ['Styled Title 1', ...]}. "
        "Do not include any extra text outside the JSON."
    )
    log_debug(f"Generating title ideas for theme '{theme}' with style '{title_style}'")
    try:
        result = parse_llm_json(self.llm, prompt, output_dir, "discovery_titles.txt", flatten=False)
        log_debug(f"Discovery titles generated: {result}")
        return result
    except Exception as e:
        log_debug(f"Error generating discovery titles: {e}")
        return {"titles": [], "styled_titles": []}