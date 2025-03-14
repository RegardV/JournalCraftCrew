#manager_agent.py
from crewai import Agent, Task
from tools.tools import DuckDBTool
from config.settings import TESTING_MODE, OUTPUT_DIR
from datetime import datetime
import os
from agents.research_agent import create_research_agent, research_content
from agents.content_curator_agent import create_content_curator_agent, curate_content
from agents.editor_agent import create_editor_agent, edit_content

def create_manager_agent(llm):
    return Agent(
        role="Manager",
        goal="Orchestrate the creation of themed journaling guides with lead magnet, main offer, and edited content",
        backstory="""I’m the coordinator of the CourseCraft Content Crew, ensuring each agent produces a piece of the journaling guide package.
        I manage research, content curation, and editing, keeping everything on track for a practical, interactive guide.""",
        tools=[DuckDBTool()],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=True
    )

def coordinate_phases(manager_agent, research_agent, content_curator_agent, editor_agent, theme="Journaling for Anxiety"):
    print("Manager Agent: Coordinating Content Creation Crew...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    output_folder = os.path.join(OUTPUT_DIR, today)
    os.makedirs(output_folder, exist_ok=True)
    research_data_path = os.path.join(output_folder, f"research_data_{today}.json")
    log_path = os.path.join(output_folder, f"automation_log_{today}.txt")

    # Step 1: Research phase
    print("Manager Agent: Delegating research task to Research Agent...")
    research_task = Task(
        description=f"""Gather journaling insights for '{theme}' from blog posts and books, reformulating to avoid plagiarism.
        Support a 4-week guide with Day 0, daily spreads (book: image placeholder + pre-writeup + prompt with lines; self-print: pre-writeup + prompt with lines),
        intro, commitment, and certificate. Save full data to {research_data_path}.""",
        agent=research_agent,
        expected_output="Summary of 3-5 journaling insights",
        output_file=research_data_path
    )
    research_summary = research_content(research_agent, theme, research_data_path)
    with open(log_path, "a") as log:
        log.write(f"Research completed: {research_data_path} | Summary: {research_summary}\n")

    # Step 2: Content curation phase
    print("Manager Agent: Delegating content curation to Content Curator Agent...")
    curation_result = curate_content(content_curator_agent, research_summary, research_data_path, theme, output_folder)
    journal_json_path = curation_result["journal"]
    lead_magnet_json_path = curation_result["lead_magnet"]
    with open(log_path, "a") as log:
        log.write(f"Content curation completed: {journal_json_path}, {lead_magnet_json_path}\n")

    # Step 3: Editing phase
    print("Manager Agent: Delegating editing to Editor Agent...")
    edited_result = edit_content(editor_agent, journal_json_path, lead_magnet_json_path, output_folder)
    journal_edited_path = edited_result["journal"]
    lead_magnet_edited_path = edited_result["lead_magnet"]
    with open(log_path, "a") as log:
        log.write(f"Editing completed: {journal_edited_path}, {lead_magnet_edited_path}\n")

    print(f"Manager Agent: Content Creation complete! Edited files: {journal_edited_path}, {lead_magnet_edited_path}")
    return {"journal": journal_edited_path, "lead_magnet": lead_magnet_edited_path}