from crewai import Task
from config.settings import COURSE_TOPIC, TESTING_MODE

def create_research_task(research_agent):
    """Creates a task for the Research Agent to gather information"""
    description = f"""Research the topic '{COURSE_TOPIC}' thoroughly. 
    
    Find evidence-based information about this topic from credible sources. Focus on scientific 
    studies, expert opinions, and practical applications. Identify key concepts, benefits, 
    techniques, and challenges.
    
    {"In testing mode, limit your findings to 2-3 key points (100-200 words total) and 1-2 image references." 
    if TESTING_MODE else "Gather comprehensive information covering all aspects of the topic."}
    
    Organize your findings clearly and cite your sources.
    """
    
    return Task(
        description=description,
        agent=research_agent,
        expected_output="Structured research findings for course content creation",
        output_file="research_data.json"  # Optional: save output to a file
    )

def create_curation_task(content_curator_agent, context=None):
    """Creates a task for the Content Curator Agent to structure course content"""
    description = f"""Transform research findings into structured, engaging course content for '{COURSE_TOPIC}'.
    
    Create a compelling title for the course and organize the content into logical modules. Each module 
    should have a clear title and informative content with a conversational, supportive tone.
    
    {"In testing mode, create 2-3 modules (100-200 words each) with 1-2 image placement suggestions." 
    if TESTING_MODE else "Create a comprehensive course structure with multiple modules covering all aspects of the topic."}
    
    Ensure content flows naturally between modules and maintains a consistent voice throughout.
    """
    
    return Task(
        description=description,
        agent=content_curator_agent,
        context=context,
        expected_output="Structured draft content with title and modules"
    )

def create_editing_task(editor_agent, context=None):
    """Creates a task for the Editor Agent to refine content"""
    description = f"""Polish and refine the draft course content on '{COURSE_TOPIC}'.
    
    Review for clarity, engagement, accuracy, and a supportive tone. Fix any grammatical or 
    stylistic issues. Ensure content is accessible to a general audience while maintaining 
    educational value.
    
    {"In testing mode, focus on polishing 2-3 modules to fit within 2-3 PDF pages." 
    if TESTING_MODE else "Ensure all modules are fully polished and ready for publication."}
    
    Add notes about any significant changes or suggestions for improvement.
    """
    
    return Task(
        description=description,
        agent=editor_agent,
        context=context,
        expected_output="Polished final content ready for PDF creation"
    )

def create_pdf_task(pdf_builder_agent, context=None):
    """Creates a task for the PDF Builder Agent to generate a PDF"""
    description = f"""Create a professional PDF document from the finalized course content on '{COURSE_TOPIC}'.
    
    Format the document with a clear title page, well-structured modules, and appropriate spacing. 
    
    {"In testing mode, create a 2-3 page PDF with placeholder images if specified." 
    if TESTING_MODE else "Create a comprehensive course PDF with all modules and appropriate imagery."}
    
    Include a footer with copyright information and the generation date.
    """
    
    return Task(
        description=description,
        agent=pdf_builder_agent,
        context=context,
        expected_output="Path to the generated PDF file"
    )