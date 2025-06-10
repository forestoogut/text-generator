import os
from openai import OpenAI
from dotenv import load_dotenv
from template_utils import load_structures
import random
import logging

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_structure_for_word_limit(max_words):
    all_structs = load_structures()
    selected = []
    total = 0
    attempts = 0
    max_attempts = 500

    # Accept slight overflow if total is very close
    min_words = int(max_words * 0.85)

    while attempts < max_attempts and len(selected) < 100:
        s = random.choice(all_structs)
        sentence_word_count = s[0]

        if total + sentence_word_count > max_words:
            if total < min_words:
                attempts += 1
                continue  # Try another sentence — we’re too far below
            else:
                break  # Close enough
        selected.append(s)
        total += sentence_word_count
        attempts += 1

    logging.info(f"[STRUCTURE] Built structure with {len(selected)} sentences and {total} words (target: {max_words})")
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
    logging.info(f"[GENERATION] Preparing description for topic: '{topic}' with length: '{length_category}' and max_words: {max_words}")

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

    logging.info(f"[OPENAI] Sending request with {len(sentence_structures)} structured sentences")

    chat_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional SEO and editorial content writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.85,
        max_tokens=approx_tokens
    )

    logging.info("[OPENAI] Response received")
    return chat_response.choices[0].message.content.strip()
