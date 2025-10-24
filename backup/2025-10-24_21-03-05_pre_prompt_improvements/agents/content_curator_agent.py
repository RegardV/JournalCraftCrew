from crewai import Agent
import json
import os
from datetime import datetime
from config.settings import JSON_SUBDIR, LLM_SUBDIR, DATE_FORMAT, MEDIA_SUBDIR
from utils import parse_llm_json, save_json, log_debug

def create_content_curator_agent(llm):
    """Create a content curator agent to craft journaling guides."""
    return Agent(
        role="Content Curator",
        goal="Craft a unique 30-day journaling guide and 6-day lead magnet with dynamic, theme-specific content",
        backstory="""I’m a creative curator who weaves research into bespoke journaling guides. I design a 30-day journey and a 6-day teaser, 
        each with engaging spreads tailored to the theme and style. Using minimal LLM calls, I ensure every page is fresh and purposeful.""",
        tools=[],
        verbose=True,
        memory=True,
        llm=llm,
        allow_delegation=False
    )

def curate_content(self, research_summary: list, theme: str, title: str, author_style: str, run_dir: str):
    """Curate content for 30-day journal and 6-day lead magnet, generating an image requirements list."""
    today = datetime.now().strftime(DATE_FORMAT)
    output_dir = os.path.join(run_dir, LLM_SUBDIR)
    json_dir = os.path.join(run_dir, JSON_SUBDIR)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    
    journal_json_path = os.path.join(json_dir, f"30day_journal_{title}_{theme}.json")
    lead_magnet_json_path = os.path.join(json_dir, f"lead_magnet_{title}_{theme}.json")
    image_requirements_path = os.path.join(json_dir, f"image_requirements_{title}_{theme}.json")
    theme_part = theme.split(" for ")[1] if " for " in theme else theme

    # 30-day Journal
    journal_data = {}
    image_requirements = []

    # Cover
    cover_prompt = (
        "Generate content for the cover as a JSON object with 'title' and 'image' keys directly, like {\"title\": \"...\", \"image\": \"...\"}. "
        f"Include a 'title' (e.g., '{theme}: A 30-Day Journey') and an 'image' placeholder (e.g., 'Cover Image') in a '{author_style}' style. "
        "Ensure the output is a valid JSON object with no extra text or nesting."
    )
    journal_data["cover"] = parse_llm_json(self.llm, cover_prompt, output_dir, "journal_cover.txt", expected_keys=["title", "image"], flatten=False)
    image_requirements.append({
        "image_id": "cover_30dayjournal",
        "placement": "journal_cover",
        "prompt": f"Cover image for a 30-day {theme} journal in {author_style} style",
        "path": f"{MEDIA_SUBDIR}/cover_30dayjournal.png"
    })

    # Intro Spread
    intro_prompt = (
        "Generate content for the intro spread as a JSON object with 'left' and 'right' keys directly, like {\"left\": {\"quote\": \"...\"}, \"right\": {\"image\": \"...\", \"title\": \"...\", \"writeup\": \"...\"}}. "
        f"Include 'left' with a 'quote' (180–220 words) and 'right' with an 'image' placeholder (e.g., 'Intro Image'), a 'title', and a 'writeup' (180–220 words, motivational) in a '{author_style}' style. "
        f"Use {str(research_summary[:2])} for inspiration. "
        "Ensure the output is a valid JSON object with no extra text or nesting."
    )
    journal_data["intro_spread"] = parse_llm_json(self.llm, intro_prompt, output_dir, "journal_intro.txt", expected_keys=["left", "right"], flatten=False)
    image_requirements.append({
        "image_id": "intro_30dayjournal",
        "placement": "journal_intro_spread_right",
        "prompt": f"Intro image for a 30-day {theme} journal in {author_style} style",
        "path": f"{MEDIA_SUBDIR}/intro_30dayjournal.png"
    })

    # Commitment Page
    commitment_prompt = (
        "Generate content for the commitment page as a JSON object with 'text' and 'writeup' keys directly, like {\"text\": \"...\", \"writeup\": \"...\"}. "
        f"Include a 'text' (commitment statement with '[Name]') and a 'writeup' (180–220 words, dedication-focused) in a '{author_style}' style. "
        f"Use {str(research_summary[2:4])}. "
        "Ensure the output is a valid JSON object with no extra text or nesting."
    )
    journal_data["commitment_page"] = parse_llm_json(self.llm, commitment_prompt, output_dir, "journal_commitment.txt", expected_keys=["text", "writeup"], flatten=False)

    # Days (Batched)
    days_prompt = (
        "Generate 30 daily entries as a JSON list, each with 'day', 'image_full_page', 'image_bottom', 'pre_writeup', 'prompt', and 'lines' keys, like [{\"day\": 1, \"image_full_page\": \"...\", ...}, ...]. "
        "For each day: 'day' (integer 1–30), 'image_full_page' (placeholder, e.g., 'Day X Full Page Image'), 'image_bottom' (placeholder, e.g., 'Day X Bottom Image'), "
        "'pre_writeup' (180–220 words, action-oriented for weekdays [Mon–Fri], reflective for weekends [Sat–Sun]), 'prompt' (reflective question), 'lines' (25). "
        f"Use {str(research_summary)} in a '{author_style}' style. "
        "Ensure variety and no repetition. Output as a valid JSON list with no extra text."
    )
    journal_data["days"] = parse_llm_json(self.llm, days_prompt, output_dir, "journal_days.txt", flatten=False)
    for day in journal_data["days"]:
        day_num = day["day"]
        image_requirements.append({
            "image_id": f"day{day_num}_full_30dayjournal",
            "placement": f"journal_day_{day_num}_full",
            "prompt": f"Full-page image for Day {day_num} of a 30-day {theme} journal in {author_style} style",
            "path": f"{MEDIA_SUBDIR}/day{day_num}_full_30dayjournal.png"
        })
        image_requirements.append({
            "image_id": f"day{day_num}_bottom_30dayjournal",
            "placement": f"journal_day_{day_num}_bottom",
            "prompt": f"Bottom image for Day {day_num} of a 30-day {theme} journal in {author_style} style",
            "path": f"{MEDIA_SUBDIR}/day{day_num}_bottom_30dayjournal.png"
        })

    # Certificate
    cert_prompt = (
        "Generate content for the certificate as a JSON object with 'summary', 'text', 'fields', and 'image' keys directly, like {\"summary\": \"...\", \"text\": \"...\", \"fields\": [...], \"image\": \"...\"}. "
        f"Include a 'summary' (180–220 words), 'text' (with '[Name]' and '[benefit]'), 'fields' (list like ['Name', 'Date']), and an 'image' placeholder in a '{author_style}' style. "
        f"Use {str(research_summary[-2:])}. "
        "Ensure the output is a valid JSON object with no extra text or nesting."
    )
    journal_data["certificate"] = parse_llm_json(self.llm, cert_prompt, output_dir, "journal_certificate.txt", expected_keys=["summary", "text", "fields", "image"], flatten=False)
    image_requirements.append({
        "image_id": "certificate_30dayjournal",
        "placement": "journal_certificate",
        "prompt": f"Certificate image for a 30-day {theme} journal in {author_style} style",
        "path": f"{MEDIA_SUBDIR}/certificate_30dayjournal.png"
    })

    save_json(journal_data, journal_json_path)
    log_debug(f"30-day journal saved to {journal_json_path}")

    # 6-day Lead Magnet
    lead_magnet_data = {}

    # Cover
    lead_cover_prompt = (
        "Generate content for the lead magnet cover as a JSON object with 'title' and 'image' keys directly, like {\"title\": \"...\", \"image\": \"...\"}. "
        f"Include a 'title' (e.g., 'Start {theme}: A Short Guide') and an 'image' placeholder in a '{author_style}' style. "
        "Ensure the output is a valid JSON object with no extra text or nesting."
    )
    lead_magnet_data["cover"] = parse_llm_json(self.llm, lead_cover_prompt, output_dir, "lead_cover.txt", expected_keys=["title", "image"], flatten=False)
    image_requirements.append({
        "image_id": "cover_leadmagnet",
        "placement": "lead_magnet_cover",
        "prompt": f"Cover image for a 6-day {theme} lead magnet in {author_style} style",
        "path": f"{MEDIA_SUBDIR}/cover_leadmagnet.png"
    })

    # Intro Spread
    lead_intro_prompt = (
        "Generate content for the lead magnet intro spread as a JSON object with 'left' and 'right' keys directly, like {\"left\": {\"quote\": \"...\"}, \"right\": {\"image\": \"...\", \"title\": \"...\", \"writeup\": \"...\"}}. "
        f"Include 'left' with a 'quote' (180–220 words) and 'right' with an 'image' placeholder, a 'title', and a 'writeup' (180–220 words, teaser-focused) in a '{author_style}' style. "
        f"Use {str(research_summary[:2])}. "
        "Ensure the output is a valid JSON object with no extra text or nesting."
    )
    lead_magnet_data["intro_spread"] = parse_llm_json(self.llm, lead_intro_prompt, output_dir, "lead_intro.txt", expected_keys=["left", "right"], flatten=False)
    image_requirements.append({
        "image_id": "intro_leadmagnet",
        "placement": "lead_magnet_intro_spread_right",
        "prompt": f"Intro image for a 6-day {theme} lead magnet in {author_style} style",
        "path": f"{MEDIA_SUBDIR}/intro_leadmagnet.png"
    })

    # Commitment Page
    lead_commit_prompt = (
        "Generate content for the lead magnet commitment page as a JSON object with 'text' and 'writeup' keys directly, like {\"text\": \"...\", \"writeup\": \"...\"}. "
        f"Include a 'text' (commitment statement with '[Name]') and a 'writeup' (180–220 words, teaser-focused) in a '{author_style}' style. "
        f"Use {str(research_summary[2:3])}. "
        "Ensure the output is a valid JSON object with no extra text or nesting."
    )
    lead_magnet_data["commitment_page"] = parse_llm_json(self.llm, lead_commit_prompt, output_dir, "lead_commitment.txt", expected_keys=["text", "writeup"], flatten=False)

    # Days (Batched)
    lead_days_prompt = (
        "Generate 6 daily entries as a JSON list, each with 'day', 'image_full_page', 'image_bottom', 'pre_writeup', 'prompt', and 'lines' keys, like [{\"day\": 1, \"image_full_page\": \"...\", ...}, ...]. "
        "For each day: 'day' (integer 1–6), 'image_full_page' (placeholder), 'image_bottom' (placeholder), 'pre_writeup' (180–220 words, action-oriented for days 1–5, reflective for day 6), 'prompt' (reflective question), 'lines' (25). "
        f"Use {str(research_summary[:6])} in a '{author_style}' style. "
        "Ensure variety and no repetition. Output as a valid JSON list with no extra text."
    )
    lead_magnet_data["days"] = parse_llm_json(self.llm, lead_days_prompt, output_dir, "lead_days.txt", flatten=False)
    for day in lead_magnet_data["days"]:
        day_num = day["day"]
        image_requirements.append({
            "image_id": f"day{day_num}_full_leadmagnet",
            "placement": f"lead_magnet_day_{day_num}_full",
            "prompt": f"Full-page image for Day {day_num} of a 6-day {theme} lead magnet in {author_style} style",
            "path": f"{MEDIA_SUBDIR}/day{day_num}_full_leadmagnet.png"
        })
        image_requirements.append({
            "image_id": f"day{day_num}_bottom_leadmagnet",
            "placement": f"lead_magnet_day_{day_num}_bottom",
            "prompt": f"Bottom image for Day {day_num} of a 6-day {theme} lead magnet in {author_style} style",
            "path": f"{MEDIA_SUBDIR}/day{day_num}_bottom_leadmagnet.png"
        })

    # Certificate
    lead_cert_prompt = (
        "Generate content for the lead magnet certificate as a JSON object with 'summary', 'text', 'fields', and 'image' keys directly, like {\"summary\": \"...\", \"text\": \"...\", \"fields\": [...], \"image\": \"...\"}. "
        f"Include a 'summary' (180–220 words), 'text' (with '[Name]'), 'fields' (list like ['Name', 'Date']), and an 'image' placeholder in a '{author_style}' style. "
        f"Use {str(research_summary[6:7])}. "
        "Ensure the output is a valid JSON object with no extra text or nesting."
    )
    lead_magnet_data["certificate"] = parse_llm_json(self.llm, lead_cert_prompt, output_dir, "lead_certificate.txt", expected_keys=["summary", "text", "fields", "image"], flatten=False)
    image_requirements.append({
        "image_id": "certificate_leadmagnet",
        "placement": "lead_magnet_certificate",
        "prompt": f"Certificate image for a 6-day {theme} lead magnet in {author_style} style",
        "path": f"{MEDIA_SUBDIR}/certificate_leadmagnet.png"
    })

    save_json(lead_magnet_data, lead_magnet_json_path)
    log_debug(f"Lead magnet saved to {lead_magnet_json_path}")
    
    # Save image requirements
    save_json(image_requirements, image_requirements_path)
    log_debug(f"Image requirements saved to {image_requirements_path}")

    return {"journal": journal_json_path, "lead_magnet": lead_magnet_json_path, "image_requirements": image_requirements_path}