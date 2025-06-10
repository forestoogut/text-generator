import os
from openai import OpenAI
from dotenv import load_dotenv
from template_utils import load_structures
import random

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_structure_for_word_limit(max_words):
    all_structs = load_structures()
    selected = []
    total = 0

    while total < max_words - 50 and len(selected) < 100:
        s = random.choice(all_structs)
        sentence_word_count = s[0]
        if total + sentence_word_count <= max_words:
            selected.append(s)
            total += sentence_word_count
    return selected

def build_prompt(topic, sentence_structures):
    structure_lines = [
        f"- Sentence {i+1}: {wc} words, ends with '{punc}'"
        for i, (wc, punc) in enumerate(sentence_structures)
    ]

    return f"""
You are a skilled, professional long-form content writer.

Your task is to write a high-quality SEO-optimized description on the topic: "{topic}".

Requirements:
- Use exactly {len(sentence_structures)} sentences.
- Match the structure of each sentence as follows:
{chr(10).join(structure_lines)}
- Group the sentences into coherent paragraphs.
- Do not summarize. Expand every idea with depth and clarity.
- Avoid clichés, overly formal tone, or excessive keyword stuffing.
- Prioritize clarity, precision, and natural human-like flow.
    """.strip()

def generate_description(topic, length_category='medium', max_words=1300):
    if length_category == 'custom':
        sentence_structures = build_structure_for_word_limit(max_words)
    else:
        target_word_count = {
            "very_short": 350,
            "short": 850,
            "medium": 1300,
            "long": 1800
        }.get(length_category, 1300)
        sentence_structures = build_structure_for_word_limit(target_word_count)

    prompt = build_prompt(topic, sentence_structures)

    approx_tokens = int(max_words * 1.5)
    if approx_tokens > 4096:
        approx_tokens = 4096

    chat_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional SEO and editorial content writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.85,
        max_tokens=approx_tokens
    )

    return chat_response.choices[0].message.content.strip()
