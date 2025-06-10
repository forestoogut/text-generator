import json
import re
from pathlib import Path

def split_into_sentences(text):
    # Basic sentence split: punctuation followed by space and capital
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def analyze_description(description):
    sentences = split_into_sentences(description)
    sentence_lengths = [len(s.split()) for s in sentences]
    punctuation = [s[-1] if s and s[-1] in '.!?' else '.' for s in sentences]

    total_sentences = len(sentences)
    if total_sentences <= 2:
        category = 'short'
    elif total_sentences <= 4:
        category = 'medium'
    else:
        category = 'long'

    return {
        "sentence_lengths": sentence_lengths,
        "punctuation": punctuation,
        "total_sentences": total_sentences,
        "length_category": category,
        "original_text": description
    }

def load_descriptions(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        raw = file.read()
        descriptions = [desc.strip().strip('"') for desc in raw.split('---') if desc.strip()]
        return descriptions

def main():
    input_path = Path("D:/CryptoGamble/text-editor/descriptions.txt")
    output_path = Path("D:/CryptoGamble/text-editor/templates.json")

    descriptions = load_descriptions(input_path)
    templates = {}

    for idx, desc in enumerate(descriptions, start=1):
        template_data = analyze_description(desc)
        templates[f"template_{idx}"] = template_data

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(templates, f, indent=2)

    print(f"✅ {len(templates)} templates saved to {output_path}")

if __name__ == '__main__':
    main()
