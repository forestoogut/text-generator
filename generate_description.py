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
    max_attempts = 1500

    min_words = int(max_words * 0.9)

    while attempts < max_attempts and len(selected) < 200:
        s = random.choice(all_structs)
        sentence_word_count = s[0]

        if total + sentence_word_count > max_words:
            if total < min_words:
                attempts += 1
                continue
            else:
                break
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
You are a skilled, professional SEO writer. Your goal is to generate a high-quality, human-sounding description about the topic: "{topic}".

You MUST follow this exact structure:
- Write exactly {len(sentence_structures)} sentences.
- Match each sentence to its exact word count and punctuation from the list below:
{chr(10).join(structure_lines)}

Critical Instructions:
- You are NOT allowed to shorten or skip any sentence.
- You MUST expand your ideas enough to fully use each sentence’s word count.
- The description should be grouped into paragraphs naturally.
- Avoid repetition, clichés, or robotic language.
- If you don’t understand the topic, improvise with authority — never skip.

Your job is to fill this structure with informative, SEO-optimized, natural writing.

Now write the description.
    """.strip()


def generate_description(topic, length_category='medium', max_words=1300):
    logging.info(f"[GENERATION] Preparing description for topic: '{topic}' with length: '{length_category}' and max_words: {max_words}")

    if length_category == 'custom':
        sentence_structures = build_structure_for_word_limit(max_words)
    else:
        target_word_count = {
            "very_short": 350,
            "short": 950,     # mid of 750–1100
            "medium": 1350,   # mid of 1000–1700
            "long": 1950      # mid of 1700–2200
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

retries = 3
result = ""
word_count = 0

for attempt in range(1, retries + 1):
    logging.info(f"[OPENAI] Attempt {attempt} — Sending request...")
    chat_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional SEO and editorial content writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.85,
        max_tokens=approx_tokens
    )

    result = chat_response.choices[0].message.content.strip()
    word_count = len(result.split())

    logging.info(f"[OPENAI] Response received — Word count: {word_count}")

    if word_count >= int(max_words * 0.9):  # accept if at least 90% of max_words
        logging.info(f"[RESULT] Accepted response on attempt {attempt}")
        break
    else:
        logging.warning(f"[RESULT] Too short — Retrying (attempt {attempt})...")

if word_count < int(max_words * 0.9):
    logging.error(f"[RESULT] Failed to meet length after {retries} attempts — returning best attempt")

return result

