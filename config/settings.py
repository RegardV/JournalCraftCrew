import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
XAI_API_KEY = os.getenv("XAI_API_KEY", "")
MEDIA_LLM_API_KEY = os.getenv("MEDIA_LLM_API_KEY", "")

# Debugging Configuration
DEBUG = True

# Media Generation Toggle
ENABLE_MEDIA_LLM = False  # Set to True to enable real media LLM calls, False for dry run with placeholders

# Base Output Configuration
OUTPUT_DIR = "Projects_Derived"
LLM_SUBDIR = "LLM_output"
JSON_SUBDIR = "Json_output"
MEDIA_SUBDIR = "media"
PDF_SUBDIR = "PDF_output"
DATE_FORMAT = "%Y-%m-%d"

# Onboarding Style Configurations
TITLE_STYLES = [
    "motivational", "actionable", "insightful", "inspirational", "practical",
    "thought-provoking", "encouraging", "implementable", "illuminating", "empowering"
]
AUTHOR_FORMAT = "Author: {name}\nRole: Bestselling Author\nBio: {style}"

# Research Depth Configurations
VALID_RESEARCH_DEPTHS = {
    "light": 5,
    "medium": 15,
    "deep": 25
}

# Course Topic Configuration
COURSE_TOPIC = "Journaling for Personal Growth"

# Testing Configuration
TESTING_MODE = False  # Set to True for testing with demo data