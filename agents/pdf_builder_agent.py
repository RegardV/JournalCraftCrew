from crewai import Agent
from crewai_tools.tools import Tool
from tools.tools import create_pdf
from models import PDFContent, CourseModule
from config.settings import TESTING_MODE
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

def create_pdf_builder_agent(llm):
    """Creates a PDF Builder Agent to generate PDF documents from course content"""
    return Agent(
        role="PDF Builder",
        goal="Transform finalized course content into professionally formatted PDF documents",
        backstory="""I am a document engineering specialist with expertise in creating 
        beautifully formatted educational materials. My background in typography, layout 
        design, and technical documentation helps me transform raw content into polished, 
        professional PDFs that enhance readability and learning retention.""",
        tools=[
            Tool(
                name="create_pdf",
                func=create_pdf,
                description="Generate professionally formatted PDF documents from course content"
            )
        ],
        verbose=True,
        memory=False,  # PDF creation doesn't need memory between runs
        llm=llm,
        output_parser=parse_pdf_builder_output
    )

def parse_pdf_builder_output(output):
    """Parses the PDF builder's output to get the path to the created PDF"""
    # If output is a string, assume it's the path to the PDF
    if isinstance(output, str) and output.endswith('.pdf'):
        return output
    
    # If output is a dict, try to extract the path
    if isinstance(output, dict) and 'pdf_path' in output:
        return output['pdf_path']
    
    # Fall back to a default path if parsing fails
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("output", today, f"course_output_{today}.pdf")

def prepare_pdf_content(final_content):
    """Converts FinalContent to PDFContent for PDF generation"""
    return PDFContent(
        title=final_content.title,
        body=final_content.modules,
        footer=f"© CourseCraft Crew | Generated on {datetime.now().strftime('%Y-%m-%d')}",
        image_paths=[]  # In a real implementation, this would contain actual image paths
    )