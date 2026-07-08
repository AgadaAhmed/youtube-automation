# YouTube Automation Pipeline — Design Spec
*Date: 2026-05-03*

## Overview

A fully automated, faceless YouTube channel in the History & Mysteries niche. The pipeline runs daily via GitHub Actions at no cost, generating and uploading one video per day without any manual intervention after initial setup.

**Channel:** mymymysteryhist@gmail.com  
**Niche:** History & Mysteries — mix of dark/suspenseful (unsolved crimes, paranormal, conspiracies) and epic/cinematic (ancient civilizations, lost empires, forgotten wars)  
**Budget:** $0/month (entirely free tier)  
**Video style:** Slideshow with bold text overlays on dark atmospheric backgrounds  
**Target duration:** 5–8 minutes per video

---

## Architecture

```
GitHub Actions (daily cron 9am UTC)
        │
        ▼
  pipeline.py (orchestrator)
        │
        ├─ 1. topic_picker.py     → reads topics.json, picks next unused topic
        ├─ 2. script_writer.py    → Gemini API generates full script
        ├─ 3. voice_generator.py  → Edge TTS narrates script → audio.mp3
        ├─ 4. video_builder.py    → Pillow renders slides → FFmpeg assembles video.mp4
        ├─ 5. thumbnail_maker.py  → Pillow generates thumbnail.jpg
        └─ 6. uploader.py         → YouTube Data API v3 uploads video + thumbnail
```

---

## File Structure

```
youtube-automation/
├── pipeline.py
├── modules/
│   ├── topic_picker.py
│   ├── script_writer.py
│   ├── voice_generator.py
│   ├── video_builder.py
│   ├── thumbnail_maker.py
│   └── uploader.py
├── data/
│   └── topics.json           # 200+ pre-seeded topics, marked used after upload
├── assets/
│   ├── fonts/                # font files for Pillow text rendering
│   └── music/                # optional royalty-free background loops
├── auth/
│   └── get_refresh_token.py  # one-time script to generate YouTube refresh token
├── .github/
│   └── workflows/
│       └── daily_upload.yml
└── requirements.txt
```

---

## Tech Stack (100% Free)

| Component | Tool | Cost |
|---|---|---|
| Script generation | Google Gemini API (free tier) | $0 |
| Text-to-speech | Edge TTS (Microsoft neural voices) | $0 |
| Image/slide rendering | Pillow (Python) | $0 |
| Video assembly | FFmpeg | $0 |
| YouTube upload | YouTube Data API v3 | $0 |
| Scheduling & hosting | GitHub Actions | $0 |

---

## Data Flow

### topics.json format
```json
[
  { "topic": "The Dyatlov Pass Incident", "used": false },
  { "topic": "The Voynich Manuscript", "used": false }
]
```

### Script format (Gemini output)
```json
{
  "title": "The Vanishing of the Eilean Mor Lighthouse Keepers",
  "description": "In 1900, three lighthouse keepers vanished without a trace...",
  "tags": ["mystery", "history", "unsolved", "lighthouse", "scotland"],
  "sections": [
    {
      "text": "In December 1900, a supply boat arrived at a remote Scottish lighthouse. What they found inside would baffle investigators for over a century.",
      "duration": 18
    }
  ]
}
```

Each section = one slide + one narration chunk. The `duration` field is a hint for Gemini's pacing only — actual slide display duration is derived from the real TTS audio length for that section, measured after generation.

### Video style
- Background: deep navy/black gradient with subtle noise texture
- Title slide: large bold white text, channel name beneath
- Body slides: 2–3 lines of narration text, centered, amber/red accent on key words
- Outro slide: channel name + "Subscribe for more" prompt
- Thumbnail: bold title text, high contrast, dark background — no faces, no stock photos

---

## GitHub Actions Workflow

```yaml
name: Daily YouTube Upload
on:
  schedule:
    - cron: '0 9 * * *'   # 9am UTC daily
  workflow_dispatch:        # manual trigger from GitHub UI
jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: sudo apt-get install -y ffmpeg
      - run: python pipeline.py
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
      - name: Commit updated topics.json
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/topics.json
          git diff --staged --quiet || git commit -m "chore: mark topic as used"
          git push
```

---

## GitHub Secrets

| Secret | Description |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio free API key |
| `YOUTUBE_CLIENT_ID` | OAuth 2.0 Desktop app client ID |
| `YOUTUBE_CLIENT_SECRET` | OAuth 2.0 Desktop app client secret |
| `YOUTUBE_REFRESH_TOKEN` | Long-lived token from one-time auth flow |

---

## One-Time Setup Steps

1. Regenerate Gemini API key in Google AI Studio
2. Regenerate OAuth credentials in Google Cloud Console
3. Create GitHub repo, push code
4. Run `auth/get_refresh_token.py` locally — logs in as mymymysteryhist@gmail.com, saves refresh token
5. Add all 4 secrets to GitHub repo Settings → Secrets
6. Enable YouTube Data API v3 in Google Cloud Console
7. Trigger workflow manually once to verify end-to-end
8. Walk away

---

## Topics Seeding

`data/topics.json` is pre-loaded with 200 topics covering both content styles:

**Dark & Suspenseful:**
- The Dyatlov Pass Incident
- The Mary Celeste: A Ship Found Drifting With No Crew
- The Voynich Manuscript — The Book Nobody Can Read
- The Eilean Mor Lighthouse Keepers Disappearance
- The Zodiac Killer: Ciphers Never Cracked
- Unit 731: Japan's Secret Experiments
- The Tunguska Event
- The Bermuda Triangle — What Science Actually Says
- The Dancing Plague of 1518
- The Overtoun Bridge Dog Suicide Mystery
*(+90 more dark/mystery topics)*

**Epic & Cinematic:**
- The Lost City of Atlantis — What We Actually Know
- The Black Death: How It Wiped Out Half of Europe
- The Fall of Rome — And Why It Still Matters
- The Knights Templar: Rise and Mysterious End
- The Library of Alexandria — What Was Really Lost
- Genghis Khan: The Man Who Conquered the World
- The Aztec Empire's Final Days
- Pompeii: The City Frozen in Time
- The Easter Island Statues — Still Unsolved
- The Silk Road: Trade Route That Shaped the World
*(+90 more epic/history topics)*

Topics are worked through in order. `used: true` is set after each upload. New topics can be added anytime via GitHub file editor.

---

## Error Handling

- Any Python exception in pipeline.py causes GitHub Actions to mark the run as failed
- GitHub sends an email notification on failure automatically
- The topic is not marked as `used` until after successful upload — so a failed run retries the same topic next trigger
- Workflow can be re-triggered manually from GitHub UI at any time

---

## Success Criteria

- One video uploaded to mymymysteryhist channel every day at ~9am UTC
- Zero manual steps required after initial setup
- Total monthly cost: $0
- Videos are 5–8 minutes, properly titled, described, tagged, and thumbnailed
- Channel runs for 6+ months before topics list needs replenishing
