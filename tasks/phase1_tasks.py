from crewai import Task
from config.settings import COURSE_TOPIC, TESTING_MODE

def create_research_task(research_agent, theme=None, depth=None, run_dir=None):
    """Creates a task for the Research Agent to gather information"""
    # Use provided theme or fall back to default
    research_topic = theme if theme else COURSE_TOPIC

    description = f"""Research the topic '{research_topic}' thoroughly.

    Find evidence-based information about this topic from credible sources. Focus on scientific
    studies, expert opinions, and practical applications. Identify key concepts, benefits,
    techniques, and challenges.

    Research depth: {depth if depth else 'standard'}

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

def create_curation_task(content_curator_agent, context=None, theme=None, title=None, author_style=None, run_dir=None):
    """Creates a task for the Content Curator Agent to structure course content"""
    # Use provided theme or fall back to default
    content_topic = theme if theme else COURSE_TOPIC
    content_title = title if title else "Custom Journal"
    writing_style = author_style if author_style else "supportive and encouraging"

    description = f"""Transform research findings into structured, engaging journal content for '{content_topic}'.

    Create compelling content for the journal titled "{content_title}" and organize the content into logical modules. Each module
    should have a clear title and informative content with a {writing_style} tone.

    {"In testing mode, create 2-3 modules (100-200 words each) with 1-2 image placement suggestions."
    if TESTING_MODE else "Create a comprehensive journal structure with multiple modules covering all aspects of the topic."}

    Ensure content flows naturally between modules and maintains a consistent voice throughout.
    """

    return Task(
        description=description,
        agent=content_curator_agent,
        context=context,
        expected_output="Structured draft content with title and modules"
    )

def create_editing_task(editor_agent, context=None, author_style=None):
    """Creates a task for the Editor Agent to refine content"""
    writing_style = author_style if author_style else "supportive and encouraging"

    description = f"""Polish and refine the draft journal content.

    Review for clarity, engagement, accuracy, and a {writing_style} tone. Fix any grammatical or
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

def create_pdf_task(pdf_builder_agent, context=None, run_dir=None, use_media=False):
    """Creates a task for the PDF Builder Agent to generate a PDF"""
    media_option = "with images and media" if use_media else "text-only"

    description = f"""Create a professional PDF document from the finalized journal content.

    Format the document with a clear title page, well-structured modules, and appropriate spacing.
    Create a {media_option} PDF.

    {"In testing mode, create a 2-3 page PDF with placeholder images if specified."
    if TESTING_MODE else "Create a comprehensive journal PDF with all modules and appropriate imagery."}

    Include a footer with copyright information and the generation date.
    """

    return Task(
        description=description,
        agent=pdf_builder_agent,
        context=context,
        expected_output="Path to the generated PDF file"
    )