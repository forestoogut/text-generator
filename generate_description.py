import os
from openai import OpenAI
from dotenv import load_dotenv
from template_utils import load_structures
import random
import logging
import math

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

Now write the description.
""".strip()

def calculate_chunks(total_words, per_chunk_limit=1000):
    chunks = math.ceil(total_words / per_chunk_limit)
    base = total_words // chunks
    remainder = total_words % chunks
    return [base + (1 if i < remainder else 0) for i in range(chunks)]

def generate_chunk(topic, word_target):
    sentence_structures = build_structure_for_word_limit(word_target)
    prompt = build_prompt(topic, sentence_structures)
    approx_tokens = min(int(word_target * 1.5), 4096)

    retries = 3
    result = ""

    for attempt in range(1, retries + 1):
        logging.info(f"[OPENAI] Attempt {attempt} for {word_target} words")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional SEO and editorial content writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=approx_tokens
        )

        result = response.choices[0].message.content.strip()
        word_count = len(result.split())

        logging.info(f"[OPENAI] Response length: {word_count} words")

        if word_count >= int(word_target * 0.9):
            break
        else:
            logging.warning(f"[RESULT] Too short, retrying...")

    return result

def generate_description(topic, length_category='medium', max_words=1300):
    logging.info(f"[GENERATION] Topic: '{topic}' | Length: '{length_category}' | Max Words: {max_words}")

    if length_category != 'custom':
        max_words = {
            "very_short": 350,
            "short": 950,
            "medium": 1350,
            "long": 1950
        }.get(length_category, 1300)

    # Force chunks of max 500 words
    chunk_size = 500
    num_chunks = (max_words + chunk_size - 1) // chunk_size
    chunk_targets = [max_words // num_chunks] * num_chunks
    for i in range(max_words % num_chunks):
        chunk_targets[i] += 1

    logging.info(f"[GENERATION] Split into {num_chunks} chunks: {chunk_targets}")

    final_output = []

    for i, target in enumerate(chunk_targets):
        logging.info(f"[PART {i+1}] Generating...")
        structure = build_structure_for_word_limit(target)
        logging.info(f"[STRUCTURE] Built structure with {len(structure)} sentences and {sum(wc for wc, _ in structure)} words (target: {target})")
        prompt = build_prompt(topic, structure)

        retries = 3
        for attempt in range(1, retries + 1):
            logging.info(f"[OPENAI] Attempt {attempt} for {target} words")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional SEO and editorial content writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.85,
                max_tokens=min(4096, int(target * 1.5))
            )

            text = response.choices[0].message.content.strip()
            word_count = len(text.split())
            logging.info(f"[OPENAI] Response length: {word_count} words")

            if word_count >= int(target * 0.9):
                logging.info(f"[RESULT] Accepted part {i+1}")
                final_output.append(text)
                break
            else:
                logging.warning(f"[RESULT] Too short, retrying...")

        else:
            logging.warning(f"[RESULT] Part {i+1} failed to meet length. Using best attempt.")
            final_output.append(text)

    final_result = "\n\n".join(final_output)
    logging.info(f"[RESULT] Final length: {len(final_result.split())} words")
    return final_result

