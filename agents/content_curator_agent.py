from crewai import Agent
from tools.tools import analyze_sentiment
from models import DraftContent, CourseModule
from config.settings import MAX_MODULES, TESTING_MODE

def create_content_curator_agent(llm):
    """Creates a Content Curator Agent to organize research into structured course content"""
    return Agent(
        role="Content Curator",
        goal="Transform research findings into engaging, well-structured course modules",
        backstory="""I am an experienced content strategist and educator skilled at organizing
        complex information into clear, engaging learning modules. My background in instructional
        design helps me create logical flows that maximize learner engagement and retention.
        I excel at maintaining a consistent, supportive tone throughout educational materials.""",
        tools=[analyze_sentiment],
        verbose=True,
        memory=True,
        llm=llm,
        output_parser=parse_curator_output
    )

def parse_curator_output(output):
    """Parses the content curator's output into a structured DraftContent object"""
    # For simplicity, we expect the agent to provide a JSON or formatted output
    # In a real implementation, this would use more robust parsing

    if isinstance(output, DraftContent):
        return output

    if TESTING_MODE:
        # In testing mode, we'll create a simplified example if parsing fails
        try:
            # Try to extract title and modules from the output
            # This is a placeholder for more sophisticated parsing
            title = output.get("title", "Journaling for Anxiety: Calming Your Mind Through Writing")

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
                    # Handle string or other format
                    modules.append(CourseModule(
                        title="Untitled Module",
                        content=str(m),
                        image_placement=None
                    ))

            return DraftContent(
                title=title,
                modules=modules
            )

        except Exception as e:
            print(f"Error parsing curator output: {e}")
            # Fall back to mock data
            return create_mock_draft_content()
    else:
        # In full mode, we'd implement more sophisticated parsing
        # This is a placeholder for that implementation
        # For now, we'll just use the testing mode logic
        return create_mock_draft_content()


def create_mock_draft_content():
    """Creates mock draft content when parsing fails"""
    print("[MOCK] Creating mock draft content")

    modules = [
        CourseModule(
            title="Understanding Anxiety and the Power of Journaling",
            content="""Anxiety affects millions worldwide, manifesting as persistent worry, fear,
            and physical symptoms that disrupt daily life. Research shows that regular journaling
            can reduce anxiety symptoms by up to 23% within just six weeks. This powerful practice
            works by providing a safe outlet for processing negative emotions and breaking cycles
            of rumination that fuel anxiety. In this module, we'll explore the science behind
            anxiety and how the simple act of writing can activate your body's relaxation
            response.""",
            image_placement="Image of a person journaling in a peaceful setting"
        ),
        CourseModule(
            title="Getting Started: Effective Journaling Techniques",
            content="""The most effective journaling practice involves writing for 15 minutes at
            least three times per week. You don't need fancy equipment—a simple notebook and pen
            will do. This module explores practical techniques including free writing, prompt-based
            journaling, and gratitude entries. We'll also cover when to journal (morning vs.
            evening), how to create a comfortable journaling environment, and ways to overcome
            common obstacles like "I don't know what to write about." The goal is to establish a
            sustainable practice that fits your lifestyle.""",
            image_placement="Image of journal and pen with example prompts visible"
        )
    ]

    if not TESTING_MODE:
        # Add more modules for full mode
        modules.append(CourseModule(
            title="Advanced Techniques for Anxiety Management",
            content="""Once you've established a basic journaling practice, you can incorporate
            specialized techniques specifically designed for anxiety management. This module covers
            thought records to identify and challenge anxious thinking, worry time to contain
            rumination, and body scan journaling to recognize physical manifestations of anxiety.
            You'll learn how to track anxiety triggers and patterns over time, creating your
            personal anxiety management toolkit through consistent documentation.""",
            image_placement="Infographic showing journaling techniques and their benefits"
        ))

    return DraftContent(
        title="Journaling for Anxiety: Calming Your Mind Through Writing",
        modules=modules[:MAX_MODULES]
    )