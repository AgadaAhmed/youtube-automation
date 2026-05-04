import json
from groq import Groq

PROMPT_TEMPLATE = """You are a scriptwriter for a viral faceless YouTube channel about history and mysteries.
Write a single, cohesive, narrative-driven video script about: {topic}

This must read like ONE continuous story — not a list of facts. Every section must flow naturally into the next, like a documentary narrator walking the viewer through events in real time.

Return ONLY valid JSON — no markdown, no explanation — in exactly this format:
{{
  "title": "Captivating YouTube title — dramatic full sentence, 70-100 characters",
  "description": "YouTube description 150-200 words covering what the video is about",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],
  "sections": [
    {{
      "text": "Exactly 25-35 words of narration. One moment in the story. Must connect to the next section.",
      "duration": 20
    }}
  ]
}}

STRICT RULES:
- 15-18 sections total
- Each section: EXACTLY 25-35 words — no more, no less
- Every section must feel like the next beat in a continuous story
- Use narrative transitions: "But that wasn't the strangest part.", "What happened next shocked investigators.", "Nobody could explain what they found.", "And then — silence."
- Build tension gradually: Hook → Setup → Rising dread → Revelation → Unanswered questions → Haunting close
- Section 1: gripping hook that drops the viewer into the moment
- Final section: chilling or reflective thought that lingers
- NO bullet-point style writing. NO "In this video we will explore..." — pure cinematic narration only

Title rules — make it irresistible:
- Power words: "Vanished", "Nobody Knows", "Covered Up", "They Never Found", "Still Unsolved", "Terrifying", "Disturbing"
- Curiosity gaps: "What Really Happened to...", "The Truth About...", "They Tried to Hide This", "The Mystery That Still Has No Answer"
- Can be a dramatic full sentence: "Three Men Vanished Without a Trace — Nobody Has Ever Explained What Happened"
- 70-100 characters. Longer titles perform better — use the full length. Must reflect actual content.

- 8 relevant tags
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
