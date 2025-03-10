# CourseCraft Crew

## Overview
**CourseCraft Crew** is an AI-powered platform designed to automate the creation of self-help and self-improvement courses. Using [Crew AI](https://docs.crewai.com/), it simplifies researching, developing, and generating course content. The first course, *"Journaling for Anxiety: Journaling to Calm Your Mind"*, demonstrates its capabilities as a proof-of-concept for a system that can adapt to any course topic.

## Current Status
- **Phase 1**: Complete and ready for testing. This phase focuses on text and image-based course creation, with a testing mode that generates a 2-3 page PDF for validation.
- **Phase 2 & 3**: Planned for future implementation (audio and video components).
- **Timeline**: Following a phased development approach with a target beta release by April 25, 2025.

## Features
- **Evidence-Based Research**: Automatically gathers credible information using PubMed API (with mock fallback).
- **Content Curation**: Organizes findings into structured, engaging course modules.
- **Editorial Refinement**: Polishes content for clarity, engagement, and appropriate tone using VADER sentiment analysis.
- **PDF Generation**: Creates professional course PDFs with proper formatting.
- **Testing Mode**: Produces a quick 2-3 page PDF for testing purposes.
- **Modular Architecture**: Organized into agents, tasks, and crews for flexibility and maintainability.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/coursecraft_crew.git
   cd coursecraft_crew
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure the output directory exists:
   ```bash
   mkdir -p output
   ```

## Configuration

1. Create a `.env` file in the project root with your API keys:
   ```
   XAI_API_KEY=your_xai_api_key_here
   PUBMED_API_KEY=your_pubmed_api_key_here  # Optional, will use mock data if missing
   ```

2. Configure testing mode:
   - Edit `config/settings.py` and set `TESTING_MODE = True` for a quick test output.
   - Set `TESTING_MODE = False` for full course generation.

3. Adjust course parameters:
   - Modify `COURSE_TOPIC` and `COURSE_SUBJECT` in `config/settings.py` if you want to create a course on a different topic.

## Usage

1. Ensure your configuration is set up correctly.

2. Run the system:
   ```bash
   python main.py
   ```

3. Execution options (set in `main.py`):
   - Manager-driven: Set `use_manager = True` (default)
   - Crew-driven: Set `use_manager = False`

4. Monitor progress in the console output.

5. Review the generated PDF in the output directory.

## Testing

### Testing Mode
Enable testing mode by setting `TESTING_MODE = True` in `config/settings.py`.

**What to expect:**
- A 2-3 page PDF with 2-3 course modules (100-200 words each)
- Output path: `/output/YYYY-MM-DD/paper1_journaling_for_anxiety_YYYY-MM-DD.pdf`
- Execution logs: `/developmentlogs/phase1_log.md`
- Limited research findings and content

### Full Mode
For comprehensive course generation, set `TESTING_MODE = False`.

**What to expect:**
- A full course PDF with unlimited modules
- Output path: `/output/SelfHelp/JournalingForAnxiety/YYYY-MM-DD/course_journaling_for_anxiety_YYYY-MM-DD.pdf`
- Streaming processing for handling larger content
- More comprehensive research and content

## Future Plans

- **Phase 2**: Add audio components to courses.
- **Phase 3**: Produce and edit video content.
- **Platform Integration**: Deploy courses to platforms like Teachable.
- **Advanced Research**: Enhance PubMed integration and add more research sources.
- **Marketing & Engagement**: Add agents for promoting and monitoring course performance.

## Changelog

See the [Changelog](changelog.md) for a detailed update history.

## Acknowledgements

- **Crew AI**: Powers the agent-based workflow.
- **Grok 3 from xAI**: Assists with content generation and research.
- **NLTK/VADER**: Provides sentiment analysis for content tone.
- **Reportlab**: Enables professional PDF generation.
- **Community**: #CourseCraftJourney followers providing feedback and encouragement.

## Project Structure

```
~/crewprojects/coursecraft_crew/
├── agents/                   # Agent implementations
│   ├── content_curator_agent.py
│   ├── editor_agent.py
│   ├── manager_agent.py
│   ├── pdf_builder_agent.py
│   ├── research_agent.py
│   └── ...                   # Future agents
├── config/
│   └── settings.py           # Configuration settings
├── crews/                    # Crew implementations
│   ├── phase1_crew.py
│   └── ...                   # Future crews
├── developmentlogs/          # Development logs
├── knowledge/                # Knowledge base
├── models.py                 # Pydantic data models
├── tasks/                    # Task definitions
│   ├── phase1_tasks.py
│   └── ...                   # Future tasks
├── tools/
│   └── tools.py              # Tool implementations
├── .env                      # Environment variables
├── changelog.md              # Update history
├── main.py                   # Main execution script
└── README.md                 # This file