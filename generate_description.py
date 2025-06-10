import os
from openai import OpenAI
from dotenv import load_dotenv
from template_utils import sample_structures

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(topic, sentence_structures):
    structure_lines = [
        f"- Sentence {i+1}: {wc} words, ends with '{punc}'"
        for i, (wc, punc) in enumerate(sentence_structures)
    ]

    return f"""
You are a professional SEO content writer.

Write a descriptive and informative SEO paragraph about the topic: "{topic}".

Requirements:
- Use exactly {len(sentence_structures)} sentences.
- Match the following sentence structures:
{chr(10).join(structure_lines)}
- Sound natural, clear, human-like.
- Avoid robotic tone, clichés, or repetition.
- Do not use filler or overexplain simple terms.
    """.strip()

def generate_description(topic, length_category='medium', max_words=120):
    sentence_structures = sample_structures(length_category)
    prompt = build_prompt(topic, sentence_structures)

    approx_tokens = int(max_words * 1.4)

    chat_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert SEO copywriter."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
        max_tokens=approx_tokens
    )

    return chat_response.choices[0].message.content.strip()
