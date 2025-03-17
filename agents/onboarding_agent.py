#onboarding_agent.py
from crewai import Agent
import json
import os
from datetime import datetime

def create_onboarding_agent(llm):
    return Agent(
        role="Onboarding Specialist",
        goal="Gather user preferences and align with best-selling self-help authors for a journaling guide",
        backstory="""I’m here to help you define your journaling guide by collecting your theme, preferred title, desired writing style, 
        and title style preference, drawing inspiration from top self-help authors.""",
        tools=[],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def onboard_user(self, base_output_dir: str):
    print()  # Blank line before first prompt
    while True:
        theme = input("Enter the journaling theme (e.g., 'Journaling for Anxiety', or just 'Anxiety'): ").strip()
        if theme:
            if 'for' not in theme.lower():
                original_theme = theme
                theme = f"Journaling for {theme}"
                print(f"Adjusted theme to '{theme}' for consistency (from '{original_theme}').")
            break
        print("Theme cannot be empty. Please enter a valid theme, like 'Journaling for Happiness' or 'Happiness'.")
    
    print()  # Blank line before title prompt
    while True:
        title = input("Enter your preferred journal title (e.g., 'Calm Reflections'): ").strip()
        if title:
            break
        print("Title cannot be empty. Please enter a valid title, like 'Morning Reflections'.")
    
    print()  # Blank line before title style prompt
    print("Select a style for your title options:")
    styles = ["Motivational", "Actionable", "Insightful"]
    for i, style in enumerate(styles, 1):
        print(f"{i}. {style}")
    while True:
        try:
            style_choice = int(input("Enter the number of your choice (1-3): ")) - 1
            if style_choice in range(len(styles)):
                break
            print(f"Please enter a number between 1 and {len(styles)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(styles)}.")
    title_style = styles[style_choice]
    
    print()  # Blank line before author style prompt
    print("Identifying best-selling self-help authors from recent times...")
    authors = [
        {"name": "James Clear", "style": "clear, actionable, science-backed", "book": "Atomic Habits"},
        {"name": "Mark Manson", "style": "blunt, irreverent, honest", "book": "The Subtle Art of Not Giving a F*ck"},
        {"name": "Brené Brown", "style": "empathetic, research-driven, warm", "book": "Daring Greatly"},
        {"name": "Robin Sharma", "style": "inspirational, narrative-driven", "book": "The 5 AM Club"},
        {"name": "Mel Robbins", "style": "direct, motivational, practical", "book": "The 5 Second Rule"}
    ]
    print("Choose an author’s writing style:")
    for i, author in enumerate(authors, 1):
        print(f"{i}. {author['name']} ({author['style']}) - {author['book']}")
    while True:
        try:
            choice = int(input(f"Enter the number of your choice (1-{len(authors)}): ")) - 1
            if choice in range(len(authors)):
                break
            print(f"Please enter a number between 1 and {len(authors)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(authors)}.")
    author_style = authors[choice]["style"]
    
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join(base_output_dir, f"{theme.lower().replace(' ', '-')}-{title.lower().replace(' ', '-')}-{today}")
    prefs = {"theme": theme, "title": title, "author_style": author_style, "title_style": title_style}
    prefs_path = os.path.join(folder, "onboarding_prefs.json")
    os.makedirs(folder, exist_ok=True)
    with open(prefs_path, "w") as f:
        json.dump(prefs, f, indent=2)
    return prefs_path