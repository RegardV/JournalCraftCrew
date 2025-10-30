"""
Journal Platform Backend Application Initialization
Phase 3: Backend Development
"""

import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration
from app.core.config import settings