import json


def pick_next_topic(topics_path: str) -> str:
    with open(topics_path, "r", encoding="utf-8") as f:
        topics = json.load(f)
    for entry in topics:
        if not entry["used"]:
            return entry["topic"]
    raise RuntimeError("All topics have been used. Add more topics to data/topics.json.")


def mark_topic_used(topics_path: str, topic: str) -> None:
    with open(topics_path, "r", encoding="utf-8") as f:
        topics = json.load(f)
    for entry in topics:
        if entry["topic"] == topic:
            entry["used"] = True
            break
    with open(topics_path, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)
