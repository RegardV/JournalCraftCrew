from crewai import Crew
from agents.research_agent import create_research_agent
from agents.content_curator_agent import create_content_curator_agent
from agents.editor_agent import create_editor_agent
from agents.pdf_builder_agent import create_pdf_builder_agent
from tasks.phase1_tasks import (
    create_research_task, 
    create_curation_task, 
    create_editing_task,
    create_pdf_task
)
from config.settings import OUTPUT_DIR, JSON_SUBDIR, PDF_SUBDIR, DATE_FORMAT
import os
from datetime import datetime
from utils import log_debug

def create_phase1_crew(llm, theme: str, research_depth: str, author_style: str, title: str):
    """
    Creates the Phase 1 crew for text and image-based course content creation.
    
    Args:
        llm: The language model instance to be used by agents.
        theme: The journaling theme (e.g., "Journaling for Happiness").
        research_depth: The depth of research ("light", "medium", "deep").
        author_style: The writing style for content (e.g., "inspirational narrative").
        title: The selected title for the journal (e.g., "Happiness Unleashed").
    
    Returns:
        Crew: A configured Crew instance for Phase 1 execution.
    """
    # Set up run directory
    today = datetime.now().strftime(DATE_FORMAT)
    run_dir = os.path.join(OUTPUT_DIR, f"{title.replace(' ', '_')}_{today}")
    os.makedirs(run_dir, exist_ok=True)
    json_dir = os.path.join(run_dir, JSON_SUBDIR)
    pdf_dir = os.path.join(run_dir, PDF_SUBDIR)
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)
    
    log_debug(f"Creating Phase 1 crew with run_dir: {run_dir}")
    
    # Create all necessary agents
    research_agent = create_research_agent(llm)
    content_curator_agent = create_content_curator_agent(llm)
    editor_agent = create_editor_agent(llm)
    pdf_builder_agent = create_pdf_builder_agent(llm)
    
    # Create tasks with contextual inputs
    research_task = create_research_task(research_agent, theme=theme, depth=research_depth, run_dir=run_dir)
    curation_task = create_curation_task(content_curator_agent, theme=theme, title=title, author_style=author_style, run_dir=run_dir)
    editing_task = create_editing_task(editor_agent, author_style=author_style)
    pdf_task = create_pdf_task(pdf_builder_agent, run_dir=run_dir, use_media=True)
    
    # Configure task dependencies
    curation_task.context = [research_task]
    editing_task.context = [curation_task]
    pdf_task.context = [editing_task]
    
    # Create the crew
    crew = Crew(
        agents=[research_agent, content_curator_agent, editor_agent, pdf_builder_agent],
        tasks=[research_task, curation_task, editing_task, pdf_task],
        verbose=2,  # Detailed logging
        process="sequential"  # Explicitly use sequential process
    )
    
    log_debug("Phase 1 crew created successfully")
    return crew

def process_results(crew_results):
    """
    Process and store the results from the Phase 1 crew execution.
    
    Args:
        crew_results: The results from the crew's task executions.
    
    Returns:
        dict: Paths to generated PDF files or None if incomplete.
    """
    log_debug(f"Processing Phase 1 crew results: {crew_results}")
    
    if crew_results and len(crew_results) >= 4:
        pdf_result = crew_results[3]  # Assumes PDF task is the 4th task
        
        if not isinstance(pdf_result, dict) or "journal_pdf" not in pdf_result:
            log_debug("PDF task result invalid or incomplete")
            print("Warning: PDF generation did not produce expected output.")
            return None
        
        journal_pdf = pdf_result.get("journal_pdf")
        lead_magnet_pdf = pdf_result.get("lead_magnet_pdf")
        
        print(f"Phase 1 Complete! PDF(s) created:")
        if journal_pdf:
            print(f"  Journal PDF: {journal_pdf}")
        if lead_magnet_pdf:
            print(f"  Lead Magnet PDF: {lead_magnet_pdf}")
        
        # Log completion in development logs
        today = datetime.now().strftime(DATE_FORMAT)
        log_dir = "developmentlogs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"phase1_log_{today}.md")
        with open(log_file, "a") as f:
            f.write(f"\n## Phase 1 Execution - {today}\n\n")
            if journal_pdf:
                f.write(f"Journal PDF saved at: {journal_pdf}\n")
            if lead_magnet_pdf:
                f.write(f"Lead Magnet PDF saved at: {lead_magnet_pdf}\n")
            f.write("Status: Complete\n\n")
        
        log_debug(f"Phase 1 results processed and logged to {log_file}")
        return pdf_result
    else:
        log_debug("Phase 1 execution did not complete all tasks")
        print("Warning: Phase 1 execution did not complete all tasks.")
        return None

if __name__ == "__main__":
    # Example usage (for testing purposes)
    from crewai import LLM
    from dotenv import load_dotenv
    
    load_dotenv()
    xai_api_key = os.getenv("XAI_API_KEY")
    if not xai_api_key:
        raise ValueError("XAI_API_KEY not found in .env file")
    
    llm = LLM(
        model="xai/grok-2-1212",
        api_key=xai_api_key,
        base_url="https://api.x.ai/v1",
        temperature=0,
        max_tokens=None
    )
    
    crew = create_phase1_crew(
        llm=llm,
        theme="Journaling for Happiness",
        research_depth="medium",
        author_style="inspirational narrative",
        title="Happiness Unleashed"
    )
    result = crew.kickoff()
    process_results(result)