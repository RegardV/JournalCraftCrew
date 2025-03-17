#content_curator_agent.py
from crewai import Agent
import json
import os
from datetime import datetime  # Added import

def create_content_curator_agent(llm):
    return Agent(
        role="Content Curator",
        goal="Create a 30-day journaling guide and lead magnet with structured daily spreads, intro, commitment, and certificate",
        backstory="""I’m a skilled curator who transforms journaling research into practical, engaging guides. I craft a 30-day journey 
        with a starter Day 0, 4 weeks reflecting life’s rhythm, and a lead magnet to spark interest—each with motivational intros, 
        commitments, and certificates. My work supports both self-print PDFs and book formats with image placeholders, ensuring a 
        supportive, interactive experience.""",
        tools=[],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def curate_content(self, research_summary: str, research_data_path: str, theme: str = "Journaling for Anxiety", output_folder: str = "output"):
    today = datetime.now().strftime("%Y-%m-%d")
    journal_json_path = os.path.join(output_folder, f"journal_{today}.json")
    lead_magnet_json_path = os.path.join(output_folder, f"lead_magnet_{today}.json")

    # Main Offer: 30-day guide
    journal_data = {
        "title": f"{theme}: A 30-Day Journey",
        "intro": f"Thank you for taking time out to help yourself with {theme}! Expect a 4-week journey starting with Day 0 anytime, then syncing to Mondays. Each day offers a reflection—weekdays tackle pressures, weekends bring calm—ending with a certificate of growth. Keep going; every page builds a stronger you!",
        "commitment": f"I, [Name], commit to completing this 30-day journaling guide to enhance my {theme.split(' for ')[1].lower() if ' for ' in theme else theme.lower()}.",
        "days": [
            {"day": 0, "image_placeholder": "Day 0 Image", "pre_writeup": f"Welcome to {theme}! Life’s pace can feel relentless—start today to find your footing. This unbound day eases you in before Monday.", "prompt": f"What drew you to {theme}? Jot down your hopes.", "lines": 25}
        ],
        "certificate": {
            "text": f"Certificate of Growth in {theme.split(' for ')[1] if ' for ' in theme else theme} - I, [Name], confirm I’ve completed this guide and grown by [benefit].",
            "writings": ["One thing I learned", f"How this guide helped me with {theme.split(' for ')[1].lower() if ' for ' in theme else theme.lower()}"]
        }
    }
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for week in range(1, 5):
        for i, day in enumerate(days, start=(week-1)*7 + 1):
            is_weekend = day in ["Saturday", "Sunday"]
            journal_data["days"].append({
                "day": i,
                "image_placeholder": f"Day {i} Image",
                "pre_writeup": f"{day}: {research_summary.split('; ')[0]} - {'Life’s pressures peak midweek—journaling helps you cope.' if not is_weekend else 'Weekends are for calm—reflect to recharge.'}",
                "prompt": f"{'List 3 things stressing you today' if not is_weekend else 'What soothed you this week?'}",
                "lines": 25
            })
    for day in range(29, 31):
        journal_data["days"].append({
            "day": day,
            "image_placeholder": f"Day {day} Image",
            "pre_writeup": f"Bonus Day {day-28}: Wrap up your {theme} journey with a final reflection.",
            "prompt": f"What’s changed since Day 0?",
            "lines": 25
        })
    save_json(journal_data, journal_json_path)

    # Lead Magnet: 6-day guide
    lead_magnet_data = {
        "title": f"Start {theme}: A Short Guide",
        "intro": f"Welcome to your 6-day starter guide to {theme}! This guide introduces you to journaling as a tool to manage and understand your {theme.lower()}. Each day offers a step toward growth.",
        "commitment": f"I, [Name], commit to exploring {theme.lower()} with this guide.",
        "days": [
            {"day": i, "image_placeholder": f"Day {i} Image", "pre_writeup": f"Day {i}: {research_summary.split('; ')[min(i-1, 2)]} - Start small; it’s your path to [benefit].", "prompt": f"What’s one {theme.lower()} moment today?", "lines": 25}
            for i in range(1, 7)
        ],
        "how_to": f"To continue your journey, consider the full 30-day guide. Start with Day 0 anytime, then Mondays for 4 weeks—deepen your {theme.lower()}!",
        "certificate": {
            "text": f"Certificate of Starting {theme} - I, [Name], confirm I’ve begun this journey.",
            "writings": [f"One insight I gained about {theme.lower()}"]
        }
    }
    save_json(lead_magnet_data, lead_magnet_json_path)

    return {"journal": journal_json_path, "lead_magnet": lead_magnet_json_path}