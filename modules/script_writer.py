import json
from groq import Groq

PROMPT_TEMPLATE = """You are a scriptwriter for a viral faceless YouTube channel about history and mysteries.
Write a single, cohesive, narrative-driven video script about: {topic}

This must read like ONE continuous documentary — not a list of facts. Every section flows into the next.

Return ONLY valid JSON — no markdown, no explanation:
{{
  "title": "Captivating YouTube title — dramatic full sentence, 70-100 characters",
  "description": "YouTube description 150-200 words. Do NOT repeat the title verbatim.",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "sections": [
    {{
      "text": "Narration text. STRICTLY 25-35 words. One story beat. Flows from previous section.",
      "pace": "normal"
    }}
  ]
}}

SECTION RULES:
- Exactly 12 sections
- STRICTLY 25-35 words per section — count them
- pace must be one of: "normal", "slow", "fast", "dramatic"
  - "slow" = eerie build-up, creeping dread
  - "dramatic" = key reveal, shocking moment — use sparingly (2-3 times max)
  - "fast" = momentum, escalating tension
  - "normal" = story connective tissue
- Use narrative transitions between sections: "But nobody could explain...", "What happened next changed everything.", "And then — silence.", "That was only the beginning."
- Story arc: Hook → Setup → Rising dread → First anomaly → Deeper mystery → Revelation → Unanswered questions → Haunting close
- Section 1 MUST open mid-action — drop the viewer straight into the most shocking moment. No slow intros.
- Section 12 MUST end with a chilling thought or haunting open question

TITLE RULES:
- Power words: "Vanished", "Nobody Knows", "Covered Up", "They Never Found", "Still Unsolved", "Terrifying"
- Curiosity gap: "What Really Happened to...", "The Truth About...", "They Tried to Hide This"
- Write as a dramatic full sentence. 70-100 characters. Must reflect actual content.

- 5 strategic tags only (no spam)
- description must earn its own read — not a title rewrite"""

SHORT_PROMPT_TEMPLATE = """You are writing a YouTube Shorts script for a history and mystery channel.
Topic: {topic}

This is a 45-55 second vertical video. Every word must earn its place.
The FIRST sentence must be so shocking the viewer physically cannot scroll away.

Return ONLY valid JSON — no markdown, no explanation:
{{
  "sections": [
    {{
      "text": "Maximum 20 words. One punchy idea. Pure cinematic narration.",
      "pace": "normal"
    }}
  ]
}}

RULES:
- Exactly 5 sections
- Maximum 20 words per section
- pace: "dramatic" for hook and reveal, "slow" for dread, "normal" for connective tissue, "fast" for escalation
- Section 1 (Hook/dramatic): Drop mid-action. Most shocking moment first. "Three men walked into that lighthouse. None of them ever came out."
- Section 2 (slow): The eerie setup — what should have been normal
- Section 3 (fast): The moment everything went wrong
- Section 4 (dramatic): The one detail that has never been explained
- Section 5 (normal): Haunting open question + "Follow for more dark history."
- NO filler. NO "in this video". Pure cinematic narration only."""


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
    script = json.loads(cleaned)

    # Enforce hook: section 1 must not start with "The" or generic openers
    sections = script.get("sections", [])
    if sections and len(sections[0]["text"].split()) < 10:
        sections[0]["pace"] = "dramatic"

    return script


def generate_short_script(topic: str, api_key: str) -> dict:
    client = Groq(api_key=api_key)
    prompt = SHORT_PROMPT_TEMPLATE.format(topic=topic)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    cleaned = _strip_markdown(response.choices[0].message.content)
    return json.loads(cleaned)
