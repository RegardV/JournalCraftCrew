import os
import nltk
from dotenv import load_dotenv
from langchain_xai import ChatXAI  # Import ChatXAI from langchain_xai
from agents.manager_agent import create_manager_agent, coordinate_phases
from agents.research_agent import create_research_agent
from agents.content_curator_agent import create_content_curator_agent
from agents.editor_agent import create_editor_agent
from agents.pdf_builder_agent import create_pdf_builder_agent
from crews.phase1_crew import create_phase1_crew
from config.settings import TESTING_MODE, OUTPUT_DIR
import os

# Ensure NLTK resources are downloaded
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load environment variables from .env
load_dotenv()

# Retrieve the xAI API key
xai_api_key = os.getenv("XAI_API_KEY")

# Create the ChatXAI LLM instance
llm = ChatXAI(
    api_key=xai_api_key,
    model="grok-beta",  # Using grok-beta as specified in the example
    temperature=0,
    max_tokens=None
)

def run_with_manager():
    """Run the course creation process with the Manager Agent coordinating"""
    print(f"Starting CourseCraft Crew in {'TESTING' if TESTING_MODE else 'FULL'} mode")
    
    # Create all agents
    manager_agent = create_manager_agent(llm)
    research_agent = create_research_agent(llm)
    content_curator_agent = create_content_curator_agent(llm)
    editor_agent = create_editor_agent(llm)
    pdf_builder_agent = create_pdf_builder_agent(llm)
    
    # Run the coordination process
    pdf_path = coordinate_phases(
        manager_agent, 
        research_agent, 
        content_curator_agent, 
        editor_agent, 
        pdf_builder_agent
    )
    
    print(f"Process complete! PDF available at: {pdf_path}")
    return pdf_path

def run_with_crew():
    """Run the course creation process using the Phase 1 crew"""
    print(f"Starting Phase 1 Crew in {'TESTING' if TESTING_MODE else 'FULL'} mode")
    
    # Create and run Phase 1 crew
    phase1_crew = create_phase1_crew(llm)
    results = phase1_crew.kickoff()
    
    if results:
        print(f"Process complete! PDF available at: {results}")
        return results
    else:
        print("Process completed but no PDF was generated.")
        return None

if __name__ == "__main__":
    # Choose which approach to use
    use_manager = True  # Set to False to use the Crew approach instead
    
    if use_manager:
        run_with_manager()
    else:
        run_with_crew()