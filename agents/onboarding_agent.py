import os
from datetime import datetime
from crewai import Agent
from config.settings import OUTPUT_DIR, TITLE_STYLES, VALID_RESEARCH_DEPTHS, DATE_FORMAT
from utils import parse_llm_json, log_debug

def create_onboarding_agent(llm):
    """Create an onboarding agent to gather user preferences dynamically."""
    return Agent(
        role="Onboarding Specialist",
        goal="Gather user preferences for a journaling guide",
        backstory="""I’m here to help you define your journaling guide by collecting your theme, 
        preferred title, writing style, and research depth, leveraging dynamic author insights.""",
        tools=[],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def onboard_user(self, base_output_dir):
    """Gather user preferences, check existing runs, and set up the project folder."""
    today = datetime.now().strftime(DATE_FORMAT)
    print()  # Blank line for readability
    
    # Check for existing runs
    existing_runs = [d for d in os.listdir(base_output_dir) if os.path.isdir(os.path.join(base_output_dir, d))]
    if existing_runs:
        log_debug(f"Existing projects found: {existing_runs}")
        print("Existing projects found:")
        for i, run in enumerate(existing_runs, 1):
            print(f"{i}. {run}")
        print("\nSelect an option:")
        print("1) Make a new journal")
        print("2) Make media for an existing project")
        print("3) Generate PDF with images")
        print("4) Generate PDF without images")
        print("5) Generate Epub and KDP versions")
        print("6) Quit")
        while True:
            try:
                choice = int(input("Enter your choice (1-6): "))
                log_debug(f"User entered choice: {choice}")
                if choice in range(1, 7):
                    break
                print("Please enter a number between 1 and 6.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 6.")
        
        if choice == 6:
            log_debug("User chose to quit the process.")
            print("Exiting to CLI.")
            exit(0)
        elif choice > 1:
            while True:
                try:
                    run_choice = int(input(f"Select a project (1-{len(existing_runs)}): "))
                    log_debug(f"User selected project number: {run_choice}")
                    if run_choice in range(1, len(existing_runs) + 1):
                        break
                    print(f"Please enter a number between 1 and {len(existing_runs)}.")
                except ValueError:
                    print(f"Invalid input. Please enter a number between 1 and {len(existing_runs)}.")
            selected_run = existing_runs[run_choice - 1]
            run_dir = os.path.join(base_output_dir, selected_run)
            if not os.path.exists(run_dir):
                log_debug(f"Selected run directory {run_dir} does not exist.")
                print("Error: Selected project directory not found.")
                exit(1)
            if choice == 2:
                log_debug("Returning action: generate_media")
                return {"action": "generate_media", "run_dir": run_dir}
            elif choice == 3:
                log_debug("Returning action: generate_pdf_with_images")
                return {"action": "generate_pdf_with_images", "run_dir": run_dir}
            elif choice == 4:
                log_debug("Returning action: generate_pdf_without_images")
                return {"action": "generate_pdf_without_images", "run_dir": run_dir}
            elif choice == 5:
                log_debug("Returning action: generate_epub_kdp")
                return {"action": "generate_epub_kdp", "run_dir": run_dir}
    
    # New journal process
    log_debug("No existing projects or user chose to create a new journal.")
    print("No existing projects found.\n1) Make a new journal")
    while True:
        theme = input("Enter the journaling theme (e.g., 'Journaling for Anxiety', or just 'Anxiety'): ").strip()
        if theme:
            if 'for' not in theme.lower():
                original_theme = theme
                theme = f"Journaling for {theme}"
                log_debug(f"Adjusted theme to '{theme}' from '{original_theme}'.")
                print(f"Adjusted theme to '{theme}' for consistency (from '{original_theme}').")
            break
        print("Theme cannot be empty. Please enter a valid theme.")
    
    print()
    while True:
        title = input("Enter your preferred journal title (e.g., 'Calm Reflections'): ").strip()
        if title:
            break
        print("Title cannot be empty. Please enter a valid title.")
    
    # Title style selection
    print()
    print("Select a style for your title options:")
    for i, style in enumerate(TITLE_STYLES, 1):
        print(f"{i}. {style}")
    while True:
        try:
            style_choice = int(input(f"Enter the number of your choice (1-{len(TITLE_STYLES)}): ")) - 1
            if style_choice in range(len(TITLE_STYLES)):
                break
            print(f"Please enter a number between 1 and {len(TITLE_STYLES)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(TITLE_STYLES)}.")
    title_style = TITLE_STYLES[style_choice]
    
    # Research depth selection
    print()
    print("Select the research depth for your journal:")
    depth_options = list(VALID_RESEARCH_DEPTHS.keys())
    for i, depth in enumerate(depth_options, 1):
        print(f"{i}. {depth.capitalize()} ({VALID_RESEARCH_DEPTHS[depth]} insights)")
    while True:
        try:
            depth_choice = int(input(f"Enter the number of your choice (1-{len(depth_options)}): ")) - 1
            if depth_choice in range(len(depth_options)):
                break
            print(f"Please enter a number between 1 and {len(depth_options)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(depth_options)}.")
    research_depth = depth_options[depth_choice]
    
    # Dynamic author styles via LLM
    print()
    log_debug(f"Fetching bestselling authors for '{theme}'...")
    print(f"Fetching bestselling authors for '{theme}'...")
    author_prompt = (
        f"List 5 bestselling authors in the '{theme}' niche or related personal development themes for 2025, "
        "each with a short style description (e.g., 'direct actionable'). "
        "Return a JSON list of dictionaries with 'name' and 'style' keys, "
        "e.g., [{\"name\": \"James Clear\", \"style\": \"direct actionable\"}, ...]. "
        "Ensure valid JSON with no extra text outside the list."
    )
    output_dir = os.path.join(base_output_dir, "temp_llm")
    try:
        authors = parse_llm_json(self.llm, author_prompt, output_dir, "author_styles.txt", expected_keys=["name", "style"], flatten=False)
        log_debug(f"LLM returned authors: {authors}")
        if not authors or not isinstance(authors, list):
            raise ValueError("Invalid author list returned")
    except Exception as e:
        log_debug(f"Failed to fetch dynamic authors: {e}. Falling back to default styles.")
        authors = [
            {"name": "James Clear", "style": "direct actionable"},
            {"name": "Mark Manson", "style": "blunt irreverent"},
            {"name": "Brené Brown", "style": "empathetic research-driven"},
            {"name": "Robin Sharma", "style": "inspirational narrative"},
            {"name": "Mel Robbins", "style": "direct motivational"}
        ]
    
    print("Choose an author’s writing style:")
    for i, author in enumerate(authors, 1):
        print(f"{i}. {author['name']} ({author['style']})")
    while True:
        try:
            choice = int(input(f"Enter the number of your choice (1-{len(authors)}): ")) - 1
            if choice in range(len(authors)):
                break
            print(f"Please enter a number between 1 and {len(authors)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(authors)}.")
    author_style = authors[choice]["style"]
    
    # Set up run directory
    run_dir = os.path.join(base_output_dir, f"{title.replace(' ', '_')}_{today}")
    os.makedirs(run_dir, exist_ok=True)
    
    prefs = {
        "theme": theme,
        "title": title,
        "title_style": title_style,
        "author_style": author_style,
        "research_depth": research_depth,
        "run_dir": run_dir,
        "date": today
    }
    log_debug(f"Onboarding complete with preferences: {prefs}")
    return prefs