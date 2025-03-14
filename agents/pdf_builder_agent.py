from crewai import Agent
from crewai.tools import BaseTool
from tools.tools import create_pdf
from models import PDFContent, CourseModule
from config.settings import TESTING_MODE
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

def create_pdf_builder_agent(llm):
    """Creates a PDF Builder Agent to generate PDF documents from course content."""
    class PDFCreatorTool(BaseTool):
        name: str = "create_pdf"
        description: str = "Generate professionally formatted PDF documents from course content"
        def _run(self, content: Dict[str, Any], output_path: str) -> str:
            return create_pdf(content, output_path)  # Uses the imported function
    
    return Agent(
        role="PDF Builder",
        goal="Transform finalized course content into professionally formatted PDF documents",
        backstory="""I am a document engineering specialist with expertise in creating 
        beautifully formatted educational materials. My background in typography, layout 
        design, and technical documentation helps me transform raw content into polished, 
        professional PDFs that enhance readability and learning retention.""",
        tools=[PDFCreatorTool()],
        verbose=True,
        memory=False,
        llm=llm,
        output_parser=parse_pdf_builder_output
    )

def parse_pdf_builder_output(output):
    """Parses the PDF builder's output to get the path to the created PDF."""
    if isinstance(output, str) and output.endswith('.pdf'):
        return output
    if isinstance(output, dict) and 'pdf_path' in output:
        return output['pdf_path']
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("output", today, f"course_output_{today}.pdf")

def prepare_pdf_content(final_content):
    """Converts FinalContent to PDFContent for PDF generation."""
    return PDFContent(
        title=final_content.title,
        body=final_content.modules,
        footer=f"© CourseCraft Crew | Generated on {datetime.now().strftime('%Y-%m-%d')}",
        image_paths=[]  # In a real implementation, this would contain actual image paths
    )