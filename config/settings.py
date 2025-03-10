import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
XAI_API_KEY = os.getenv("XAI_API_KEY", "")
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")

# Course Configuration
TESTING_MODE = True  # Set to False for full course generation
COURSE_TOPIC = "Journaling for Anxiety"
COURSE_SUBJECT = "SelfHelp"

# Output Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
PDF_FILENAME_FORMAT = "paper{}_{}_{}.pdf"  # paper1_2025-03-10.pdf in testing mode
COURSE_PDF_FILENAME_FORMAT = "course_{}_{}.pdf"  # course_journaling_2025-03-10.pdf in full mode

# Testing Mode Limits
MAX_FINDINGS = 3 if TESTING_MODE else 100
MAX_MODULES = 3 if TESTING_MODE else 100
MAX_IMAGES = 2 if TESTING_MODE else 100