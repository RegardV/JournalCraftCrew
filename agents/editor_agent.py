#editor_agent.py
from crewai import Agent
from tools.tools import SentimentAnalysisTool
import json  # Added import
import os
from datetime import datetime  # Added import

def create_editor_agent(llm):
    return Agent(
        role="Content Editor",
        goal="Polish journaling guide content for tone, clarity, and engagement, ensuring a supportive journaling experience",
        backstory="""I’m a seasoned editor with a knack for refining text to make it clear, engaging, and uplifting. My job is to take 
        raw journaling guide content and polish it—using sentiment analysis to keep the tone positive and supportive—ensuring every 
        pre-writeup, prompt, and note motivates users through their 4-week journey.""",
        tools=[SentimentAnalysisTool()],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def edit_content(self, journal_json_path: str, lead_magnet_json_path: str, output_folder: str = "output"):
    today = datetime.now().strftime("%Y-%m-%d")
    journal_edited_path = os.path.join(output_folder, f"journal_edited_{today}.json")
    lead_magnet_edited_path = os.path.join(output_folder, f"lead_magnet_edited_{today}.json")
    log_path = os.path.join(output_folder, f"automation_log_{today}.txt")

    with open(journal_json_path, "r") as f:
        journal_data = json.load(f)
    
    journal_data["intro"] = f"{journal_data['intro']} - Edited for warmth and encouragement."
    journal_data["commitment"] = f"{journal_data['commitment']} - Refined to inspire your journey."
    journal_data["certificate"]["text"] = f"{journal_data['certificate']['text']} - Polished to celebrate your growth."
    
    for day_entry in journal_data["days"]:
        sentiment = self.tools[0]._run(day_entry["pre_writeup"])
        if sentiment.get("compound", 0) < 0.3:
            day_entry["pre_writeup"] = f"{day_entry['pre_writeup']} - Rewritten to uplift: You’ve got this!"
        day_entry["prompt"] = f"{day_entry['prompt']} - Clarified for your reflection."
    
    save_json(journal_data, journal_edited_path)
    with open(log_path, "a") as log:
        log.write(f"Journal edited: {journal_edited_path}\n")

    with open(lead_magnet_json_path, "r") as f:
        lead_magnet_data = json.load(f)
    
    lead_magnet_data["intro"] = f"{lead_magnet_data['intro']} - Edited to spark your start."
    lead_magnet_data["commitment"] = f"{lead_magnet_data['commitment']} - Refined to encourage exploration."
    lead_magnet_data["how_to"] = f"{lead_magnet_data['how_to']} - Polished for clear guidance."
    lead_magnet_data["certificate"]["text"] = f"{lead_magnet_data['certificate']['text']} - Enhanced to mark your beginning."
    
    for day_entry in lead_magnet_data["days"]:
        sentiment = self.tools[0]._run(day_entry["pre_writeup"])
        if sentiment.get("compound", 0) < 0.3:
            day_entry["pre_writeup"] = f"{day_entry['pre_writeup']} - Rewritten to inspire: Take this step!"
        day_entry["prompt"] = f"{day_entry['prompt']} - Clarified for your ease."
    
    save_json(lead_magnet_data, lead_magnet_edited_path)
    with open(log_path, "a") as log:
        log.write(f"Lead magnet edited: {lead_magnet_edited_path}\n")

    return {"journal": journal_edited_path, "lead_magnet": lead_magnet_edited_path}