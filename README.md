# YouTube Automation

An end-to-end pipeline that produces and uploads YouTube Shorts automatically, built in **Python** and run on a schedule via **GitHub Actions**. It takes a topic and turns it into a finished, uploaded short with script, voiceover, video, and thumbnail — no manual steps.

## Pipeline

```
topic_picker  →  script_writer  →  voice_generator  →  video_builder  →  thumbnail_maker  →  uploader
```

- **topic_picker** — selects the next topic from `data/topics.json` and marks used ones.
- **script_writer** — generates the short's script (LLM-driven).
- **voice_generator** — synthesizes the voiceover.
- **video_builder** — assembles the video with captions and assets.
- **thumbnail_maker** — renders a thumbnail.
- **uploader** — publishes to YouTube via the Data API using an OAuth refresh token.

`pipeline.py` orchestrates the run; each module has its own unit tests under `tests/`.

## Configuration

All credentials are supplied via environment variables / GitHub Actions secrets — nothing is committed:

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Script generation |
| `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` | YouTube OAuth app |
| `YOUTUBE_REFRESH_TOKEN` | Long-lived upload auth (see `auth/get_refresh_token.py`) |

## Running

```bash
pip install -r requirements.txt
python pipeline.py
```

Scheduled runs are defined in `.github/workflows/`. Design and implementation plans live in `docs/`.

## Tech

Python · Google Gemini · YouTube Data API · GitHub Actions · pytest.

---

*Designed and built by Agada Ahmed, with development assisted by Claude.*
