import json
import google.generativeai as genai

PROMPT_TEMPLATE = """You are a scriptwriter for a faceless YouTube channel about history and mysteries.
Write a compelling video script about: {topic}

The video should be 5-8 minutes long (roughly 800-1100 words total across all sections).
Tone: alternate between dark/suspenseful and epic/cinematic. Start with a gripping hook.

Return ONLY valid JSON — no markdown, no explanation — in exactly this format:
{{
  "title": "Compelling YouTube title under 60 characters",
  "description": "YouTube description 150-200 words covering what the video is about",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "sections": [
    {{
      "text": "Narration text for this slide. 2-4 sentences. 25-40 words. Dramatic and conversational.",
      "duration": 20
    }}
  ]
}}

Requirements:
- 15-20 sections total
- Each section: 2-4 dramatic sentences, 25-40 words
- First section must open with a gripping hook sentence
- Last section must end with a reflective or chilling closing thought
- Title must be click-worthy and under 60 characters
- Include 5-8 relevant tags
- description must NOT repeat the title verbatim"""


def _strip_markdown(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def generate_script(topic: str, api_key: str) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = PROMPT_TEMPLATE.format(topic=topic)
    response = model.generate_content(prompt)
    cleaned = _strip_markdown(response.text)
    return json.loads(cleaned)
