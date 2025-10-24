from crewai import Agent
from tools.tools import SentimentAnalysisTool
import json
import os
from datetime import datetime
from config.settings import DATE_FORMAT
from utils import save_json, log_debug

def create_editor_agent(llm):
    """Create an editor agent to polish journaling content."""
    return Agent(
        role="Content Editor",
        goal="Polish journaling guide content for tone, clarity, and engagement, ensuring a supportive journaling experience",
        backstory="""I’m a seasoned editor with a knack for refining text to make it clear, engaging, and uplifting. My job is to take 
        raw journaling guide content and polish it—using sentiment analysis and author style to keep the tone positive and supportive—ensuring every 
        pre-writeup, prompt, and note motivates users through their journey.""",
        tools=[SentimentAnalysisTool()],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def edit_content(self, journal_file: str, lead_magnet_file: str, author_style: str):
    """Edit journal and lead magnet content for tone and clarity."""
    output_folder = os.path.dirname(journal_file)
    os.makedirs(output_folder, exist_ok=True)  # Ensure output directory exists
    
    # New naming convention: "edited_<original_filename>"
    journal_base = os.path.basename(journal_file)
    lead_magnet_base = os.path.basename(lead_magnet_file)
    journal_edited_path = os.path.join(output_folder, f"edited_{journal_base}")
    lead_magnet_edited_path = os.path.join(output_folder, f"edited_{lead_magnet_base}")
    log_path = os.path.join(output_folder, f"automation_log_{datetime.now().strftime(DATE_FORMAT)}.txt")
    
    # Define tone adjustments
    tone_modifier = " with an uplifting twist" if "inspirational" in author_style.lower() else " with a clear perspective"
    if "narrative-driven" in author_style.lower():
        tone_modifier += "—let this story guide you"
    
    # Load and edit journal
    if not os.path.exists(journal_file):
        log_debug(f"Journal file {journal_file} not found.")
        raise FileNotFoundError(f"Journal file {journal_file} not found.")
    log_debug(f"Loading journal file: {journal_file}")
    with open(journal_file, "r") as f:
        journal_data = json.load(f)
    
    journal_data["intro_spread"]["right"]["writeup"] = f"{journal_data['intro_spread']['right']['writeup']} - Edited{tone_modifier}."
    journal_data["commitment_page"]["text"] = f"{journal_data['commitment_page']['text']} - Refined to inspire your journey{tone_modifier}."
    journal_data["certificate"]["text"] = f"{journal_data['certificate']['text']} - Polished to celebrate your growth{tone_modifier}."
    
    for day_entry in journal_data["days"]:
        sentiment = self.tools[0]._run(day_entry["pre_writeup"])
        if sentiment.get("compound", 0) < 0.3:
            day_entry["pre_writeup"] = f"{day_entry['pre_writeup']} - Rewritten{tone_modifier}: You’ve got this!"
        else:
            day_entry["pre_writeup"] = f"{day_entry['pre_writeup']} - Enhanced{tone_modifier}."
        day_entry["prompt"] = f"{day_entry['prompt']} - Clarified for your reflection{tone_modifier}."
    
    try:
        save_json(journal_data, journal_edited_path)
        with open(log_path, "a") as log:
            log.write(f"Journal edited: {journal_edited_path}\n")
        log_debug(f"Journal edited and saved to {journal_edited_path}")
    except Exception as e:
        log_debug(f"Failed to save edited journal to {journal_edited_path}: {e}")
        raise

    # Load and edit lead magnet
    if not os.path.exists(lead_magnet_file):
        log_debug(f"Lead magnet file {lead_magnet_file} not found.")
        raise FileNotFoundError(f"Lead magnet file {lead_magnet_file} not found.")
    log_debug(f"Loading lead magnet file: {lead_magnet_file}")
    with open(lead_magnet_file, "r") as f:
        lead_magnet_data = json.load(f)
    
    lead_magnet_data["intro_spread"]["right"]["writeup"] = f"{lead_magnet_data['intro_spread']['right']['writeup']} - Edited to spark your start{tone_modifier}."
    lead_magnet_data["commitment_page"]["text"] = f"{lead_magnet_data['commitment_page']['text']} - Refined to encourage exploration{tone_modifier}."
    lead_magnet_data["certificate"]["text"] = f"{lead_magnet_data['certificate']['text']} - Enhanced to mark your beginning{tone_modifier}."
    
    for day_entry in lead_magnet_data["days"]:
        sentiment = self.tools[0]._run(day_entry["pre_writeup"])
        if sentiment.get("compound", 0) < 0.3:
            day_entry["pre_writeup"] = f"{day_entry['pre_writeup']} - Rewritten{tone_modifier}: Take this step!"
        else:
            day_entry["pre_writeup"] = f"{day_entry['pre_writeup']} - Enhanced{tone_modifier}."
        day_entry["prompt"] = f"{day_entry['prompt']} - Clarified for your ease{tone_modifier}."
    
    try:
        save_json(lead_magnet_data, lead_magnet_edited_path)
        with open(log_path, "a") as log:
            log.write(f"Lead magnet edited: {lead_magnet_edited_path}\n")
        log_debug(f"Lead magnet edited and saved to {lead_magnet_edited_path}")
    except Exception as e:
        log_debug(f"Failed to save edited lead magnet to {lead_magnet_edited_path}: {e}")
        raise

    return {"journal": journal_edited_path, "lead_magnet": lead_magnet_edited_path}