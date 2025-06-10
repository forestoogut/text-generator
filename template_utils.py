import json
import random
from pathlib import Path

# Path to the templates.json file (placed in the same directory as this script)
TEMPLATE_FILE = Path(__file__).parent / "templates.json"

def load_structures():
    """
    Load all available sentence structures from the templates.json file.
    Each structure is a tuple of (word_count, punctuation).
    """
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Flatten and parse all sentence structures from all templates
        return [tuple(item) for template in data for item in template]
