import json
from pathlib import Path
import logging

TEMPLATE_FILE = Path(__file__).parent / "templates.json"

def load_structures():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        structures = []
        for template in data:
            for item in template:
                if isinstance(item, list) and len(item) == 2:
                    try:
                        wc = int(item[0])
                        punc = str(item[1])
                        structures.append((wc, punc))
                    except Exception as e:
                        logging.warning(f"Skipping invalid item (bad types): {item} ({e})")
                else:
                    logging.warning(f"Skipping malformed structure: {item}")
        return structures
