import json
import random
from pathlib import Path

TEMPLATE_FILE = Path("D:/CryptoGamble/text-editor/templates.json")

def load_sentence_pool():
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        templates = json.load(f)

    sentence_formats = []
    for template in templates.values():
        sentence_formats.extend(zip(template["sentence_lengths"], template["punctuation"]))

    return sentence_formats

def sample_structures(length_category: str):
    pool = load_sentence_pool()

    count_map = {
        'short': 2,
        'medium': 4,
        'long': 6
    }
    num_sentences = count_map.get(length_category, 4)

    if len(pool) < num_sentences:
        raise ValueError("Not enough sentence templates available.")

    return random.sample(pool, num_sentences)
