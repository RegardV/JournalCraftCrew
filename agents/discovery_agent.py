#discovery_agent.py
from crewai import Agent
from tools.tools import BlogSummarySearchTool
import json
import os

def create_discovery_agent(llm):
    return Agent(
        role="Discovery Specialist",
        goal="Propose a unique journaling guide idea with SEO-optimized titles based on user preferences",
        backstory="""I explore user themes to craft fresh journaling concepts and SEO-friendly titles that stand out.""",
        tools=[BlogSummarySearchTool()],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def discover_idea(self, prefs_path: str):
    with open(prefs_path, "r") as f:
        prefs = json.load(f)
    theme = prefs["theme"]
    theme_part = theme.split(' for ')[1] if ' for ' in theme else theme  # "Gratitude"
    summary = self.tools[0]._run(theme_part.lower())  # Pass just "gratitude"
    concept = f"A 4-week guide blending daily {theme.lower()} rituals with reflective prompts to enhance well-being."
    title_style = prefs["title_style"].lower()
    
    titles = [
        prefs["title"],
        f"30-Day {theme} Journaling Guide",
        f"{theme} Relief Through Journaling",
        f"Master {theme_part} with Daily Journaling",
        f"{theme_part} Journaling for a Better You"
    ]
    styled_titles = {
        "motivational": [
            f"Ignite {theme_part} Daily",
            f"Rise with {theme_part} Journaling",
            f"Thrive Through {theme_part} Writing",
            f"Unlock {theme_part} Inspiration"
        ],
        "actionable": [
            f"Start {theme_part} Today",
            f"Build {theme_part} Step by Step",
            f"Act on {theme_part} Daily",
            f"Master {theme_part} Now"
        ],
        "insightful": [
            f"Uncover {theme_part} Within",
            f"Reflect on {theme_part} Daily",
            f"Discover {theme_part} Through Journaling",
            f"Deepen {theme_part} Insight"
        ]
    }
    
    idea = {
        "theme": theme,
        "title": prefs["title"],
        "concept": concept,
        "titles": titles,
        "styled_titles": styled_titles[title_style],
        "insights": summary
    }
    output_folder = os.path.dirname(prefs_path)
    idea_path = os.path.join(output_folder, "discovery_idea.json")
    with open(idea_path, "w") as f:
        json.dump(idea, f, indent=2)
    return idea_path