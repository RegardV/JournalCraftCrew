#main.py
import os
import nltk
import warnings
from dotenv import load_dotenv
from crewai import LLM
from agents.manager_agent import create_manager_agent, coordinate_phases
from agents.onboarding_agent import create_onboarding_agent
from agents.discovery_agent import create_discovery_agent
from agents.research_agent import create_research_agent
from agents.content_curator_agent import create_content_curator_agent
from agents.editor_agent import create_editor_agent
from config.settings import TESTING_MODE, OUTPUT_DIR

warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

os.makedirs(OUTPUT_DIR, exist_ok=True)
load_dotenv()

xai_api_key = os.getenv("XAI_API_KEY")
if not xai_api_key:
    raise ValueError("XAI_API_KEY not found. Please set it in the .env file.")

try:
    llm = LLM(
        model="xai/grok-2-1212",
        api_key=xai_api_key,
        base_url="https://api.x.ai/v1",
        temperature=0,
        max_tokens=None
    )
except Exception as e:
    print(f"Error initializing LLM: {e}")
    exit(1)

def run_with_manager():
    print(f"Starting CourseCraft Crew in {'TESTING' if TESTING_MODE else 'FULL'} mode")
    manager_agent = create_manager_agent(llm)
    onboarding_agent = create_onboarding_agent(llm)
    discovery_agent = create_discovery_agent(llm)
    research_agent = create_research_agent(llm)
    content_curator_agent = create_content_curator_agent(llm)
    editor_agent = create_editor_agent(llm)
    result = coordinate_phases(manager_agent, onboarding_agent, discovery_agent, research_agent, content_curator_agent, editor_agent)
    print(f"Process complete! Edited files: {result}")
    return result

if __name__ == "__main__":
    from tools.tools import analyze_sentiment
    test_text = "This is a great course!"
    print(f"Sentiment test: {analyze_sentiment(test_text)}")
    run_with_manager()