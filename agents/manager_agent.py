#manager_agent.py
from crewai import Agent, Task
from tools.tools import DuckDBTool
from config.settings import TESTING_MODE, OUTPUT_DIR
from datetime import datetime
import os
import json
from agents.onboarding_agent import create_onboarding_agent, onboard_user
from agents.discovery_agent import create_discovery_agent, discover_idea
from agents.research_agent import create_research_agent, research_content
from agents.content_curator_agent import create_content_curator_agent, curate_content
from agents.editor_agent import create_editor_agent, edit_content

def create_manager_agent(llm):
    return Agent(
        role="Manager",
        goal="Orchestrate the creation of themed journaling guides with lead magnet, main offer, and edited content",
        backstory="""I’m the coordinator of the CourseCraft Content Crew, ensuring each agent produces a piece of the journaling guide package.
        I manage onboarding, discovery, research, content curation, and editing, keeping everything on track.""",
        tools=[DuckDBTool()],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=True
    )

def coordinate_phases(manager_agent, onboarding_agent, discovery_agent, research_agent, content_curator_agent, editor_agent):
    print("Manager Agent: Coordinating Content Creation Crew...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    base_output_dir = OUTPUT_DIR
    
    print()
    print("---------- Step 1: Onboarding ----------")
    print("Manager Agent: Gathering user preferences with Onboarding Agent...")
    prefs_path = onboard_user(onboarding_agent, base_output_dir)
    
    print()
    print("---------- Step 2: Discovery ----------")
    print("Manager Agent: Discovering journal idea with Discovery Agent...")
    idea_path = discover_idea(discovery_agent, prefs_path)
    with open(prefs_path, "r") as f:
        prefs = json.load(f)
    with open(idea_path, "r") as f:
        idea = json.load(f)
    
    print("---------- Step 3: Title Selection ----------")
    all_titles = idea["titles"] + idea["styled_titles"]
    print()
    print("Choose your preferred title from the following options:")
    print("SEO-Optimized Titles:")
    for i, title in enumerate(idea["titles"], 1):
        print(f"{i}. {title}")
    print("Style-Influenced Titles:")
    for i, title in enumerate(idea["styled_titles"], len(idea["titles"]) + 1):
        print(f"{i}. {title}")
    print()  # Blank line before input prompt
    while True:
        try:
            choice = int(input(f"Enter the number of your choice (1-{len(all_titles)}): ")) - 1
            if choice in range(len(all_titles)):
                break
            print(f"Please enter a number between 1 and {len(all_titles)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(all_titles)}.")
    selected_title = all_titles[choice]
    idea["title"] = selected_title
    with open(idea_path, "w") as f:
        json.dump(idea, f, indent=2)
    
    output_folder = os.path.dirname(idea_path)
    research_data_path = os.path.join(output_folder, f"research_data_{today}.json")
    
    print()  # Blank line before input prompt
    print("---------- Step 4: Research ----------")
    print("Manager Agent: Delegating research task to Research Agent...")
    research_summary = research_content(research_agent, idea["theme"], research_data_path)
    with open(research_data_path, "r") as f:
        json.load(f)
    log_path = os.path.join(output_folder, f"automation_log_{today}.txt")
    with open(log_path, "a") as log:
        log.write(f"Research completed: {research_data_path} | Summary: {research_summary}\n")

    print()  # Blank line before input prompt
    print("---------- Step 5: Content Curation ----------")
    print("Manager Agent: Delegating content curation to Content Curator Agent...")
    curation_result = curate_content(content_curator_agent, research_summary, research_data_path, idea["theme"], output_folder)
    journal_json_path = curation_result["journal"]
    lead_magnet_json_path = curation_result["lead_magnet"]
    with open(log_path, "a") as log:
        log.write(f"Content curation completed: {journal_json_path}, {lead_magnet_json_path}\n")

    print()  # Blank line before input prompt
    print("---------- Step 6: Editing ----------")
    print("Manager Agent: Delegating editing to Editor Agent...")
    edited_result = edit_content(editor_agent, journal_json_path, lead_magnet_json_path, output_folder)
    journal_edited_path = edited_result["journal"]
    lead_magnet_edited_path = edited_result["lead_magnet"]
    with open(log_path, "a") as log:
        log.write(f"Editing completed: {journal_edited_path}, {lead_magnet_edited_path}\n")

    print()  # Blank line before input prompt
    print("---------- Step 7: Completion ----------")
    print(f"Manager Agent: Content Creation complete! Edited files: {journal_edited_path}, {lead_magnet_edited_path}")
    return {"journal": journal_edited_path, "lead_magnet": lead_magnet_edited_path}