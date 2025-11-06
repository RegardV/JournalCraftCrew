import os
import nltk
from dotenv import load_dotenv
from crewai import LLM
from agents.manager_agent import create_manager_agent, coordinate_phases
from agents.onboarding_agent import create_onboarding_agent
from agents.discovery_agent import create_discovery_agent
from agents.research_agent import create_research_agent
from agents.content_curator_agent import create_content_curator_agent
from agents.editor_agent import create_editor_agent
from agents.media_agent import create_media_agent
from agents.pdf_builder_agent import create_pdf_builder_agent
from config.settings import OUTPUT_DIR
from utils import log_debug

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

os.makedirs(OUTPUT_DIR, exist_ok=True)
load_dotenv()

# OpenAI Configuration
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in the .env file.")

try:
    llm = LLM(
        model="gpt-4",
        api_key=openai_api_key,
        temperature=0,
        max_tokens=None
    )
    log_debug("Successfully initialized OpenAI GPT-4 LLM")
    print("Using OpenAI GPT-4 for content generation")
except Exception as e:
    log_debug(f"Error initializing OpenAI LLM: {e}")
    print("Error: Failed to initialize OpenAI LLM")
    print("Please check your OPENAI_API_KEY in the .env file")
    exit(1)

def run_with_manager():
    log_debug("Starting Journal Craft Crew in FULL mode")
    manager_agent = create_manager_agent(llm)
    onboarding_agent = create_onboarding_agent(llm)
    discovery_agent = create_discovery_agent(llm)
    research_agent = create_research_agent(llm)
    content_curator_agent = create_content_curator_agent(llm)
    editor_agent = create_editor_agent(llm)
    media_agent = create_media_agent(llm)
    pdf_builder_agent = create_pdf_builder_agent(llm)
    
    result = coordinate_phases(
        manager_agent, onboarding_agent, discovery_agent, research_agent, 
        content_curator_agent, editor_agent, media_agent, pdf_builder_agent
    )
    log_debug(f"Process complete! Edited files: {result}")
    return result

if __name__ == "__main__":
    from tools.tools import analyze_sentiment
    test_text = "This is a great course!"
    sentiment_result = analyze_sentiment(test_text)
    log_debug(f"Sentiment test: {sentiment_result}")
    try:
        run_with_manager()
    except Exception as e:
        log_debug(f"Error in run_with_manager: {e}")
        raise