#editor_agent.py
from crewai import Agent
from tools.tools import SentimentAnalysisTool  # Updated to use new tool name
import json  # For JSON handling
import os  # For file operations

def create_editor_agent(llm):
    """
    Creates an Editor Agent to polish themed journaling guide content.

    Args:
        llm: The language model instance (e.g., xai/grok-2-1212) to power the agent.

    Returns:
        Agent: A configured CrewAI Agent instance for editing journaling guides.
    """
    return Agent(
        role="Content Editor",
        goal="Polish journaling guide content for tone, clarity, and engagement, ensuring a supportive journaling experience",
        backstory="""I’m a seasoned editor with a knack for refining text to make it clear, engaging, and uplifting. My job is to take 
        raw journaling guide content and polish it—using sentiment analysis to keep the tone positive and supportive—ensuring every 
        pre-writeup, prompt, and note motivates users through their 4-week journey.""",
        tools=[SentimentAnalysisTool()],  # Tool to ensure positive tone
        verbose=True,  # Enable detailed logging
        memory=True,  # Retain context across tasks
        llm=llm,  # Use provided LLM
        allow_delegation=False  # Handle tasks directly for simplicity
    )

def save_json(data, filepath):
    """Utility to save data as JSON."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def edit_content(self, journal_json_path: str, lead_magnet_json_path: str, output_folder: str = "output"):
    """
    Edits content for the main offer and lead magnet, ensuring tone and clarity.

    Args:
        journal_json_path (str): Path to journal JSON from Content Curator.
        lead_magnet_json_path (str): Path to lead magnet JSON from Content Curator.
        output_folder (str): Directory to save edited files.

    Returns:
        dict: Paths to edited JSON files.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    journal_edited_path = os.path.join(output_folder, today, f"journal_edited_{today}.json")
    lead_magnet_edited_path = os.path.join(output_folder, today, f"lead_magnet_edited_{today}.json")
    log_path = os.path.join(output_folder, today, f"automation_log_{today}.txt")

    # Load and edit journal content
    with open(journal_json_path, "r") as f:
        journal_data = json.load(f)
    
    # Polish intro, commitment, certificate
    journal_data["intro"] = f"{journal_data['intro']} - Edited for warmth and encouragement."
    journal_data["commitment"] = f"{journal_data['commitment']} - Refined to inspire your journey."
    journal_data["certificate"]["text"] = f"{journal_data['certificate']['text']} - Polished to celebrate your growth."
    
    # Edit daily content
    for day_entry in journal_data["days"]:
        # Use sentiment tool to ensure positive tone
        sentiment = self.tools[0]._run(day_entry["pre_writeup"])
        if sentiment.get("compound", 0) < 0.3:  # Adjust threshold as needed
            day_entry["pre_writeup"] = f"{day_entry['pre_writeup']} - Rewritten to uplift: You’ve got this!"
        day_entry["prompt"] = f"{day_entry['prompt']} - Clarified for your reflection."
    
    save_json(journal_data, journal_edited_path)
    with open(log_path, "a") as log:
        log.write(f"Journal edited: {journal_edited_path}\n")

    # Load and edit lead magnet content
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

# Note: edit_content is a placeholder; Manager Agent will integrate this into task execution