# CourseCraft Crew

![CourseCraft Banner](https://via.placeholder.com/800x200?text=CourseCraft+Crew)

## Overview

CourseCraft Crew is an advanced, multi-agent system for automatically generating high-quality, personalized journaling guides. Using multiple specialized AI agents working in concert, the system produces comprehensive 30-day journals and condensed 6-day lead magnets on any user-defined theme, with professional visual assets and output in PDF format.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## 🚀 Key Features

- **Theme-Agnostic Content Generation**: Creates tailored journaling content for any topic, from mindfulness to programming skills
- **Multi-Phase Content Creation Pipeline**: Orchestrated workflow from idea discovery to final PDF generation 
- **Professional-Quality Output**: Generates complete 30-day journals and 6-day lead magnets with complementary visuals
- **Evidence-Based Research Integration**: Incorporates real research from academic and practical sources
- **Organic Content Progression**: Creates a natural development arc throughout the journal experience
- **Visually Consistent Design**: Maintains cohesive visual identity across all journal pages

## 📋 Table of Contents

- [System Architecture](#system-architecture)
- [Agent Capabilities](#agent-capabilities)
- [Input & Output](#input--output)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Technical Details](#technical-details)
- [License](#license)

## 🏗️ System Architecture

CourseCraft Crew implements a crew-based architecture with specialized agents orchestrated by a manager agent. The system follows a sequential multi-phase workflow:

```
Onboarding → Discovery → Research → Content Curation → Editing → Media Generation → PDF Creation
```

Each phase is handled by a dedicated agent with specific expertise, with the Manager Agent coordinating the entire process and maintaining state.

### Phase 1: User Onboarding and Discovery
- Collects user preferences
- Discovers potential journal titles
- Analyzes title implications

### Phase 2: Research and Content Creation
- Performs evidence-based research
- Creates comprehensive journal content
- Generates lead magnet version

### Phase 3: Refinement and Production
- Edits content for quality and tone
- Generates visual assets
- Compiles final PDF documents

## 🤖 Agent Capabilities

### Manager Agent
- **Purpose**: Orchestrates the entire content creation process
- **Capabilities**:
  - Maintains workflow state across all phases
  - Collects and distributes information between agents
  - Handles user interaction for key decisions
  - Manages file storage and organization

### Onboarding Agent
- **Purpose**: Gathers user preferences and initializes project
- **Capabilities**:
  - Collects theme selection (e.g., "Anxiety," "Leadership")
  - Suggests writing styles based on bestselling authors
  - Determines research depth preferences
  - Creates project directory structure

### Discovery Agent
- **Purpose**: Generates title options and analyzes their implications
- **Capabilities**:
  - Creates 20 diverse, theme-appropriate title options
  - Adapts title generation to theme category
  - Analyzes each title for:
    - Primary promise (transformation offered)
    - Approach type (journey, mastery, discovery)
    - Tone (inspiring, authoritative, supportive)
    - Structure (transformation, skill-building)
    - Key verbs (action words for content)

### Research Agent
- **Purpose**: Gathers evidence-based content for the journal theme
- **Capabilities**:
  - Performs targeted blog searches for practical techniques
  - Searches academic databases (NCBI PubMed) for scientific backing
  - Analyzes category relevance based on theme
  - Structures insights into therapeutic categories:
    - UNDERSTANDING (psychology and science insights)
    - TECHNIQUES (evidence-based journaling approaches)
    - REFLECTION (prompts for patterns and insights)
    - PHYSICAL (body-focused exercises)
    - PROGRESS (methods for measuring improvement)

### Content Curator Agent
- **Purpose**: Creates comprehensive journal content
- **Capabilities**:
  - Generates theme-appropriate visual concepts
  - Creates consistent visual style definitions
  - Produces content for 30-day journal:
    - Cover design
    - Introduction
    - 30 daily entries with prompts
    - Commitment page
    - Completion certificate
  - Creates condensed 6-day lead magnet
  - Adapts content structures to theme category
  - Ensures organic progression throughout journal
  - Generates dynamic content structures and phrase banks

### Editor Agent
- **Purpose**: Refines and enhances content quality
- **Capabilities**:
  - Polishes language for tone and clarity
  - Ensures supportive, positive guidance
  - Applies author style preferences
  - Uses sentiment analysis to maintain positive tone

### Media Agent
- **Purpose**: Creates visual assets for journal content
- **Capabilities**:
  - Generates cover images for journal and lead magnet
  - Creates introduction page visuals
  - Produces day-specific imagery for each journal entry
  - Ensures visual consistency across all assets

### PDF Builder Agent
- **Purpose**: Compiles final PDF documents
- **Capabilities**:
  - Formats content with professional typography
  - Integrates text and visual elements
  - Creates navigable document structure
  - Outputs final journal and lead magnet PDFs

## 📥 Input & Output

### Inputs
- **Theme**: The primary subject matter (e.g., "Anxiety," "Leadership Skills")
- **Title Style**: Preferred style for title generation (e.g., "inspirational," "scientific")
- **Author Style**: Writing style preference (e.g., "Brené Brown - empathetic research-driven")
- **Research Depth**: Desired depth of research (shallow, medium, deep)

### Outputs
- **30-Day Journal PDF**: Complete journal with:
  - Cover page
  - Introduction
  - 30 daily entries with reflection prompts
  - Commitment page
  - Completion certificate
  - Complementary visuals throughout

- **6-Day Lead Magnet PDF**: Condensed version with:
  - Cover page
  - Introduction
  - 6 daily entries with reflection prompts
  - Completion certificate
  - Complementary visuals throughout

- **Supporting JSON Files**:
  - Discovery ideas and title analysis
  - Research data
  - Journal content
  - Lead magnet content
  - Image requirements

- **Image Assets**: 
  - Cover images
  - Introduction visuals
  - Day-specific illustrations
  - Certificate designs

## 💻 Installation

### Prerequisites
- Python 3.9+
- OpenAI API key for LLM functionality
- NCBI API key for research agent (optional)

### Step 1: Clone the repository
```bash
git clone https://github.com/yourusername/coursecraft_crew.git
cd coursecraft_crew
```

### Step 2: Set up virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up environment variables
Create a `.env` file in the project root and add:
```
OPENAI_API_KEY=your_openai_api_key
NCBI_API_KEY=your_ncbi_api_key  # Optional
```

## 🚦 Usage

### Running the Application

```bash
python main.py
```

This starts the CourseCraft Crew and begins the guided process:

1. **Onboarding**: Enter your theme, title style preference, and author style preference
2. **Discovery**: Review and select from generated title options
3. **Automated Creation**: The system will automatically:
   - Perform relevant research
   - Create journal and lead magnet content
   - Edit for quality
   - Generate visual assets (if enabled)
   - Compile PDF documents

4. **Output**: Find your completed journals in the `Projects_Derived/{Title}_{Date}/PDF_output/` directory

### Example Workflow

```
Enter the journaling theme: Leadership Skills
Enter title style preference: professional
Select author style: Simon Sinek - inspirational strategic
Select research depth: medium
Choose a title from the generated options: [3] Strategic Leadership: 30 Days to More Influential Management
```

## ⚙️ Configuration

### Main Settings (config/settings.py)

- `DEBUG`: Toggle debug logging
- `ENABLE_MEDIA_LLM`: Enable/disable media generation (default: False)
- `OUTPUT_DIR`: Base directory for generated content
- `JSON_SUBDIR`: Subdirectory for JSON outputs
- `MEDIA_SUBDIR`: Subdirectory for media assets
- `LLM_SUBDIR`: Subdirectory for LLM outputs
- `PDF_SUBDIR`: Subdirectory for PDF outputs

### LLM Configuration

- Model settings in `main.py`:
  - Content generation: GPT-4
  - Media generation: DALL-E (if enabled)

## 🔧 Technical Details

### Dependencies

- **crewai**: Multi-agent orchestration framework
- **langchain**: LLM integration and prompt management
- **openai**: API access for content generation
- **reportlab**: PDF generation
- **nltk**: Sentiment analysis for editing
- **requests**: External API interactions

### Directory Structure

```
coursecraft_crew/
├── agents/                   # Agent implementations
│   ├── content_curator_agent.py
│   ├── discovery_agent.py
│   ├── editor_agent.py
│   ├── manager_agent.py
│   ├── media_agent.py
│   ├── onboarding_agent.py
│   ├── pdf_builder_agent.py
│   └── research_agent.py
├── config/                   # Configuration
│   └── settings.py
├── crews/                    # Crew definitions
│   ├── phase1_crew.py
│   ├── phase2_crew.py
│   └── phase3_crew.py
├── knowledge/                # Knowledge resources
├── tasks/                    # Task definitions
├── tools/                    # Tool implementations
│   └── tools.py
├── main.py                   # Application entry point
├── utils.py                  # Utility functions
└── requirements.txt          # Dependencies
```

### API Rate Limiting

The system implements sequential processing which naturally prevents excessive API call rates. Critical sections like title analysis and content generation are handled in sequence, keeping API call rates well below typical limits of 8 requests per second.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgements

- Built on the CrewAI framework
- Uses OpenAI's API for content generation
- Incorporates NCBI PubMed for research capabilities

---

*CourseCraft Crew: Transforming themes into comprehensive journaling experiences.*
