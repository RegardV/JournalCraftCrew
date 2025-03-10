from crewai import Agent
from tools.tools import duckdb_tool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import os
from datetime import datetime
from config.settings import (
    TESTING_MODE, COURSE_TOPIC, COURSE_SUBJECT,
    OUTPUT_DIR, PDF_FILENAME_FORMAT, COURSE_PDF_FILENAME_FORMAT
)

# Function to create the Manager Agent, accepting an LLM parameter
def create_manager_agent(llm):
    return Agent(
        role="Manager",
        goal="Orchestrate CourseCraft Crew operations across all phases to create engaging self-help courses",
        backstory="""As the backbone of the CourseCraft Crew, I'm designed to coordinate three phase-specific crews, 
        ensuring seamless task delegation, progress tracking, and phase transitions. With a keen eye on operational tools 
        like DuckDB and Apache Airflow, I keep the project on track from research to deployment.""",
        tools=[duckdb_tool],  # Tools for data coordination
        verbose=True,  # Enables detailed logging for monitoring
        memory=True,  # Allows the agent to retain context across interactions
        llm=llm,  # Use the LLM passed from main.py
        allow_delegation=True  # Enable delegation to other agents
    )

# Coordinate phases function with enhanced data handling
def coordinate_phases(manager_agent, research_agent, content_curator_agent, editor_agent, pdf_builder_agent):
    """Coordinates the work of Phase 1 agents"""
    print("Manager Agent: Coordinating tasks across Phase 1 crew...")
    
    # Output path setup
    today = datetime.now().strftime("%Y-%m-%d")
    
    if TESTING_MODE:
        # Testing mode: simpler output structure
        output_folder = os.path.join(OUTPUT_DIR, today)
        # Find the next available paper number
        paper_num = 1
        while os.path.exists(os.path.join(
            output_folder, 
            PDF_FILENAME_FORMAT.format(paper_num, COURSE_TOPIC.lower().replace(" ", "_"), today)
        )):
            paper_num += 1
        
        output_path = os.path.join(
            output_folder, 
            PDF_FILENAME_FORMAT.format(paper_num, COURSE_TOPIC.lower().replace(" ", "_"), today)
        )
    else:
        # Full mode: more structured output
        output_folder = os.path.join(OUTPUT_DIR, COURSE_SUBJECT, COURSE_TOPIC.replace(" ", ""), today)
        output_path = os.path.join(
            output_folder,
            COURSE_PDF_FILENAME_FORMAT.format(COURSE_TOPIC.lower().replace(" ", "_"), today)
        )
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Step 1: Research phase
    print("Manager Agent: Delegating research task to Research Agent...")
    research_data = research_agent.run(
        task_description=f"Research the topic '{COURSE_TOPIC}' and gather key findings",
        stream=not TESTING_MODE  # Stream only for full courses to handle large outputs
    )
    
    # Step 2: Content curation phase
    print("Manager Agent: Delegating content curation to Content Curator Agent...")
    draft_content = content_curator_agent.run(
        task_description=f"Create structured course content from research findings",
        context={"research_data": research_data},
        stream=not TESTING_MODE
    )
    
    # Step 3: Editing phase
    print("Manager Agent: Delegating editing to Editor Agent...")
    final_content = editor_agent.run(
        task_description="Polish and finalize the course content",
        context={"draft_content": draft_content},
        stream=not TESTING_MODE
    )
    
    # Step 4: PDF generation phase
    print("Manager Agent: Delegating PDF generation to PDF Builder Agent...")
    pdf_path = pdf_builder_agent.run(
        task_description="Create a PDF document from the final content",
        context={"final_content": final_content, "output_path": output_path}
    )
    
    print(f"Manager Agent: Phase 1 complete! PDF saved at: {pdf_path}")
    return pdf_path