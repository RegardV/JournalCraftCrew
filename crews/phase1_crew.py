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
from config.settings import TESTING_MODE
import os
from datetime import datetime

def create_phase1_crew(llm):
    """Creates the Phase 1 crew for text and image-based course content"""
    
    # Create all necessary agents
    research_agent = create_research_agent(llm)
    content_curator_agent = create_content_curator_agent(llm)
    editor_agent = create_editor_agent(llm)
    pdf_builder_agent = create_pdf_builder_agent(llm)
    
    # Create tasks
    research_task = create_research_task(research_agent)
    
    # These tasks will receive context after previous tasks complete
    curation_task = create_curation_task(content_curator_agent)
    editing_task = create_editing_task(editor_agent)
    pdf_task = create_pdf_task(pdf_builder_agent)
    
    # Create the crew
    crew = Crew(
        agents=[research_agent, content_curator_agent, editor_agent, pdf_builder_agent],
        tasks=[research_task, curation_task, editing_task, pdf_task],
        verbose=2,  # Detailed logging
        process=process_results  # Process function to handle task outputs
    )
    
    return crew

def process_results(crew_results):
    """Process and store the results from the Phase 1 crew execution"""
    # Extract the final result, which should be the path to the PDF
    if crew_results and len(crew_results) >= 4:
        pdf_path = crew_results[3]  # Assumes PDF task is the 4th task
        
        print(f"Phase 1 Complete! PDF created at: {pdf_path}")
        
        # Log completion in development logs
        today = datetime.now().strftime("%Y-%m-%d")
        log_dir = "developmentlogs"
        os.makedirs(log_dir, exist_ok=True)
        
        with open(os.path.join(log_dir, "phase1_log.md"), "a") as f:
            f.write(f"\n## Phase 1 Execution - {today}\n\n")
            f.write(f"Test PDF saved at: {pdf_path}\n")
            f.write(f"TESTING_MODE: {TESTING_MODE}\n")
            f.write("Status: Complete\n\n")
        
        return pdf_path
    else:
        print("Warning: Phase 1 execution did not complete all tasks.")
        return None