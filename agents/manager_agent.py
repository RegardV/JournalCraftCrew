import os
import json
from datetime import datetime
from crewai import Agent
from tools.tools import DuckDBTool
from config.settings import OUTPUT_DIR, JSON_SUBDIR, DATE_FORMAT
from agents.onboarding_agent import onboard_user
from agents.discovery_agent import discover_idea
from agents.research_agent import research_content
from agents.content_curator_agent import curate_content
from agents.editor_agent import edit_content
from agents.media_agent import generate_media
from agents.pdf_builder_agent import generate_pdf
from utils import save_json, log_debug

def create_manager_agent(llm):
    """Create the manager agent to orchestrate content creation."""
    return Agent(
        role="Manager",
        goal="Orchestrate the creation of themed journaling guides with dynamic theming",
        backstory="""I'm the coordinator of the Journal Craft Crew, guiding agents to craft journaling guides tailored to user preferences. 
        I manage data flow dynamically, ensuring efficiency and adaptability.""",
        tools=[DuckDBTool()],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=True
    )

def coordinate_phases(manager_agent, onboarding_agent, discovery_agent, research_agent, content_curator_agent, editor_agent, media_agent, pdf_builder_agent):
    """Coordinate the phases of content creation, from onboarding to optional PDF generation."""
    log_debug("Manager Agent: Coordinating Content Creation Crew...")
    today = datetime.now().strftime(DATE_FORMAT)
    
    # Step 1: Onboarding
    log_debug("Step 1: Onboarding")
    prefs = onboard_user(onboarding_agent, OUTPUT_DIR)
    
    # Handle non-new journal actions
    if "action" in prefs:
        run_dir = prefs["run_dir"]
        if prefs["action"] == "generate_media":
            log_debug("Generating media for existing content...")
            try:
                generate_media(media_agent, run_dir)
                return {"status": "media_generated"}
            except Exception as e:
                log_debug(f"Failed to generate media: {e}")
                print(f"Error generating media: {e}")
                raise
        elif prefs["action"] == "generate_pdf_with_images":
            log_debug("Generating PDF with images...")
            try:
                pdf_result = generate_pdf(pdf_builder_agent, run_dir, use_media=True)
                return {"status": "pdf_generated_with_images", "pdfs": pdf_result}
            except Exception as e:
                log_debug(f"Failed to generate PDF with images: {e}")
                print(f"Error generating PDF with images: {e}")
                raise
        elif prefs["action"] == "generate_pdf_without_images":
            log_debug("Generating PDF without images...")
            try:
                pdf_result = generate_pdf(pdf_builder_agent, run_dir, use_media=False)
                return {"status": "pdf_generated_without_images", "pdfs": pdf_result}
            except Exception as e:
                log_debug(f"Failed to generate PDF without images: {e}")
                print(f"Error generating PDF without images: {e}")
                raise
        elif prefs["action"] == "generate_epub_kdp":
            log_debug("Generating Epub and KDP versions...")
            try:
                pdf_result = generate_pdf(pdf_builder_agent, run_dir, use_media=False, epub_kdp=True)
                return {"status": "epub_kdp_generated", "pdfs": pdf_result}
            except Exception as e:
                log_debug(f"Failed to generate Epub/KDP: {e}")
                print(f"Error generating Epub/KDP: {e}")
                raise
    
    # New journal process
    theme = prefs.get("theme", "Unknown Theme")
    title = prefs.get("title", "Untitled Journal")
    title_style = prefs.get("title_style")
    author_style = prefs.get("author_style")
    research_depth = prefs.get("research_depth")
    run_dir = prefs["run_dir"]
    log_debug(f"Manager Agent: Using preferences - Theme: {theme}, Title Style: {title_style}, Author Style: {author_style}, Research Depth: {research_depth}")
    
    # Step 2: Discovery
    log_debug("Step 2: Discovery")
    log_debug("Manager Agent: Discovering journal idea with Discovery Agent...")
    ideas = discover_idea(discovery_agent, theme=theme, title_style=title_style)
    
    # Step 3: Title Selection
    log_debug("Step 3: Title Selection")
    if "titles" not in ideas or "styled_titles" not in ideas:
        log_debug(f"Invalid title ideas structure: {ideas}")
        raise ValueError("Discovery agent returned invalid title ideas structure")
    all_titles = ideas["titles"] + ideas["styled_titles"]
    log_debug(f"Presenting {len(all_titles)} title options to user")
    print(f"\nSelect a title from the following {len(all_titles)} options:")
    for i, title_option in enumerate(all_titles, 1):
        print(f"  {i}. {title_option}")
        log_debug(f"Title option {i}: {title_option}")
    print()
    while True:
        try:
            choice = int(input(f"Enter your choice (1-{len(all_titles)}): ")) - 1
            if choice in range(len(all_titles)):
                break
            print(f"Please enter a number between 1 and {len(all_titles)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(all_titles)}.")
    selected_title = all_titles[choice]
    log_debug(f"User selected title: {selected_title} (option {choice + 1})")
    
    # Update run_dir with selected title
    old_run_dir = run_dir
    run_dir = os.path.join(OUTPUT_DIR, f"{selected_title.replace(' ', '_')}_{today}")
    if old_run_dir != run_dir and os.path.exists(old_run_dir):
        os.rename(old_run_dir, run_dir)
    
    # Save onboarding preferences
    prefs["title"] = selected_title
    prefs_path = os.path.join(run_dir, JSON_SUBDIR, f"onboarding_prefs_{selected_title}_{theme}.json")
    os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
    save_json(prefs, prefs_path)
    
    # Save discovery ideas
    idea_path = os.path.join(run_dir, JSON_SUBDIR, f"discovery_idea_{selected_title}_{theme}.json")
    save_json({"theme": theme, "ideas": ideas}, idea_path)
    
    # Step 4: Research
    log_debug("Step 4: Research")
    log_debug(f"Manager Agent: Delegating research task with depth: {research_depth}")
    research_summary = research_content(research_agent, theme=theme, depth=research_depth, run_dir=run_dir)
    research_data_path = os.path.join(run_dir, JSON_SUBDIR, f"research_data_{selected_title}_{theme}.json")
    save_json({"theme": theme, "research": research_summary}, research_data_path)
    
    # Step 5: Content Curation
    log_debug("Step 5: Content Curation")
    log_debug("Manager Agent: Delegating content curation with author style...")
    curation_result = curate_content(content_curator_agent, research_summary=research_summary, theme=theme, title=selected_title, author_style=author_style, run_dir=run_dir)
    
    # Step 6: Editing
    log_debug("Step 6: Editing")
    log_debug("Manager Agent: Delegating editing with author style...")
    edited_result = edit_content(editor_agent, journal_file=curation_result["journal"], lead_magnet_file=curation_result["lead_magnet"], author_style=author_style)
    
    # Interactive Pause
    log_debug("JSON generation complete, prompting user for next step")
    print("\nJSON generation complete!")
    while True:
        continue_choice = input("Continue with PDF generation now? (1) Yes, (2) No: ").strip()
        if continue_choice in ['1', '2']:
            break
        print("Please enter '1' or '2'.")
    if continue_choice == '2':
        log_debug("User chose to pause after JSON generation.")
        print("Process paused. JSON files saved in:", run_dir)
        return {"journal": edited_result["journal"], "lead_magnet": edited_result["lead_magnet"]}
    
    # Step 7: Media Generation
    log_debug("Step 7: Media Generation")
    log_debug("Manager Agent: Generating media for content...")
    generate_media(media_agent, run_dir)
    
    # Step 8: PDF Generation
    log_debug("Step 8: PDF Generation")
    log_debug("Manager Agent: Generating PDFs with images...")
    try:
        pdf_result = generate_pdf(pdf_builder_agent, run_dir, use_media=True)
    except Exception as e:
        log_debug(f"Failed to generate PDFs: {e}")
        print(f"Error generating PDFs: {e}")
        raise
    
    # Step 9: Completion
    log_debug("Step 9: Completion")
    log_debug(f"Manager Agent: Content Creation complete! Edited files: {edited_result['journal']}, {edited_result['lead_magnet']}")
    if "journal_pdf" in pdf_result and "lead_magnet_pdf" in pdf_result:
        log_debug(f"PDF files: {pdf_result['journal_pdf']}, {pdf_result['lead_magnet_pdf']}")
    else:
        log_debug(f"Partial PDF generation: {pdf_result}")
    return {"journal": edited_result["journal"], "lead_magnet": edited_result["lead_magnet"], "pdfs": pdf_result}