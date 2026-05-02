import json
import pytest
from modules.topic_picker import pick_next_topic, mark_topic_used


def test_pick_next_topic_returns_first_unused(tmp_path):
    topics_file = tmp_path / "topics.json"
    topics_file.write_text(json.dumps([
        {"topic": "Topic A", "used": True},
        {"topic": "Topic B", "used": False},
        {"topic": "Topic C", "used": False},
    ]))
    result = pick_next_topic(str(topics_file))
    assert result == "Topic B"


def test_pick_next_topic_raises_when_all_used(tmp_path):
    topics_file = tmp_path / "topics.json"
    topics_file.write_text(json.dumps([
        {"topic": "Topic A", "used": True},
    ]))
    with pytest.raises(RuntimeError, match="All topics have been used"):
        pick_next_topic(str(topics_file))


def test_mark_topic_used_updates_file(tmp_path):
    topics_file = tmp_path / "topics.json"
    topics_file.write_text(json.dumps([
        {"topic": "Topic A", "used": False},
        {"topic": "Topic B", "used": False},
    ]))
    mark_topic_used(str(topics_file), "Topic A")
    data = json.loads(topics_file.read_text())
    assert data[0]["used"] is True
    assert data[1]["used"] is False


def test_mark_topic_used_does_not_mark_wrong_topic(tmp_path):
    topics_file = tmp_path / "topics.json"
    topics_file.write_text(json.dumps([
        {"topic": "Topic A", "used": False},
        {"topic": "Topic B", "used": False},
    ]))
    mark_topic_used(str(topics_file), "Topic A")
    data = json.loads(topics_file.read_text())
    assert data[1]["used"] is False
