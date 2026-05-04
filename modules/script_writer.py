import json
from groq import Groq

PROMPT_TEMPLATE = """You are a scriptwriter for a viral faceless YouTube channel about history and mysteries.
Write a compelling video script about: {topic}

The video should be 5-8 minutes long (roughly 800-1100 words total across all sections).
Tone: alternate between dark/suspenseful and epic/cinematic. Start with a gripping hook.

Return ONLY valid JSON — no markdown, no explanation — in exactly this format:
{{
  "title": "Captivating YouTube title under 60 characters",
  "description": "YouTube description 150-200 words covering what the video is about",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],
  "sections": [
    {{
      "text": "Narration text for this slide. 2-4 sentences. 25-40 words. Dramatic and conversational.",
      "duration": 20
    }}
  ]
}}

Title rules — make it irresistible to click:
- Use power words: "Vanished", "Terrifying", "Nobody Knows", "Disturbing", "Covered Up", "They Never Found", "Still Unsolved"
- Use curiosity gaps: "The Truth About...", "What Really Happened to...", "They Tried to Hide This"
- Numbers work well: "3 Minutes That Changed History", "The Last 48 Hours of..."
- Under 60 characters. No clickbait lies — must reflect the actual content.

Other requirements:
- 15-20 sections total
- Each section: 2-4 dramatic sentences, 25-40 words
- First section must open with a gripping hook sentence
- Last section must end with a reflective or chilling closing thought
- Include 8 relevant tags
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
    client = Groq(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(topic=topic)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    cleaned = _strip_markdown(response.choices[0].message.content)
    return json.loads(cleaned)
