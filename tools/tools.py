from crewai import Agent
from langchain.tools import Tool
# Assuming tools.py is in a tools/ subdirectory
from tools.tools import analyze_sentiment
from models import FinalContent, CourseModule
from config.settings import TESTING_MODE, MAX_MODULES
from typing import List, Dict, Any

def create_editor_agent(llm):
    """
    Creates an Editor Agent to refine and polish course content.

    Args:
        llm: The language model instance to power the agent.

    Returns:
        Agent: A configured CrewAI Agent instance.
    """
    return Agent(
        role="Content Editor",
        goal="Polish and refine course content to ensure clarity, engagement, and pedagogical effectiveness",
        backstory="""I am a seasoned editor with years of experience refining educational materials. 
        My specialty is maintaining a clear, approachable voice while ensuring content is accurate, 
        engaging, and structured effectively for learning. I have a keen eye for detail and am 
        skilled at improving flow, readability, and emotional resonance in self-help materials.""",
        tools=[
            Tool(
                name="analyze_sentiment",
                func=analyze_sentiment,
                description="Analyze the sentiment of text to ensure content maintains a clear, positive, and supportive tone"
            )
        ],
        verbose=True,
        memory=True,
        llm=llm,
        output_parser=parse_editor_output
    )

def parse_editor_output(output):
    """
    Parses the editor's output into a structured FinalContent object.

    Args:
        output: The raw output from the editor agent.

    Returns:
        FinalContent: A structured object containing the parsed content.
    """
    if isinstance(output, FinalContent):
        return output
    
    if TESTING_MODE:
        try:
            title = output.get("title", "Journaling for Anxiety: Calming Your Mind Through Writing")
            notes = output.get("notes", "Content has been edited for clarity and engagement.")
            modules_raw = output.get("modules", [])
            modules = []
            for m in modules_raw[:MAX_MODULES]:
                if isinstance(m, dict):
                    modules.append(CourseModule(
                        title=m.get("title", "Untitled Module"),
                        content=m.get("content", ""),
                        image_placement=m.get("image_placement", None)
                    ))
                else:
                    modules.append(CourseModule(
                        title="Untitled Module",
                        content=str(m),
                        image_placement=None
                    ))
            return FinalContent(title=title, modules=modules, notes=notes)
        except Exception as e:
            print(f"Error parsing editor output: {e}")
            return create_mock_final_content()
    else:
        # Placeholder for full parsing logic in production
        return create_mock_final_content()

def create_mock_final_content():
    """
    Creates mock final content when parsing fails or in testing mode.

    Returns:
        FinalContent: A mock FinalContent object with sample data.
    """
    print("[MOCK] Creating mock final content")
    modules = [
        CourseModule(
            title="Understanding Anxiety and the Power of Journaling",
            content="""Anxiety affects millions worldwide...""",  # Truncated for brevity
            image_placement="Image of a person journaling in a peaceful setting"
        ),
        CourseModule(
            title="Getting Started: Effective Journaling Techniques",
            content="""The most effective journaling practice...""",  # Truncated
            image_placement="Image of journal and pen with example prompts visible"
        )
    ]
    if not TESTING_MODE:
        modules.append(CourseModule(
            title="Advanced Techniques for Anxiety Management",
            content="""Once you've established a basic journaling practice...""",  # Truncated
            image_placement="Infographic showing journaling techniques and their benefits"
        ))
    return FinalContent(
        title="Journaling for Anxiety: Calming Your Mind Through Writing",
        modules=modules[:MAX_MODULES],
        notes="Content has been edited for clarity, engagement, and emotional resonance."
    )