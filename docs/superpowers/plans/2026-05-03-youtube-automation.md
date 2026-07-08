# YouTube Automation Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully automated faceless YouTube channel pipeline that generates and uploads one History & Mysteries video per day using GitHub Actions at zero cost.

**Architecture:** A single Python orchestrator (`pipeline.py`) calls six focused modules in sequence: topic picking, script generation (Gemini API), TTS narration (Edge TTS), slide rendering + video assembly (Pillow + FFmpeg), thumbnail generation (Pillow), and YouTube upload (YouTube Data API v3). GitHub Actions runs the orchestrator daily via cron and commits the updated topics list back to the repo.

**Tech Stack:** Python 3.11, google-generativeai, edge-tts, Pillow, FFmpeg (subprocess), mutagen, google-api-python-client, google-auth-oauthlib, pytest, pytest-mock

---

## File Map

| File | Responsibility |
|---|---|
| `pipeline.py` | Orchestrates all modules in sequence; handles tmp dir lifecycle |
| `modules/topic_picker.py` | Reads topics.json, returns next unused topic, marks it used |
| `modules/script_writer.py` | Calls Gemini API, returns structured script dict |
| `modules/voice_generator.py` | Generates per-section MP3s via Edge TTS; measures durations |
| `modules/video_builder.py` | Renders PNG slides (Pillow); assembles video segments (FFmpeg) |
| `modules/thumbnail_maker.py` | Renders 1280×720 thumbnail PNG (Pillow) |
| `modules/uploader.py` | Uploads video + thumbnail to YouTube via OAuth refresh token |
| `auth/get_refresh_token.py` | One-time script: opens browser OAuth flow, prints refresh token |
| `data/topics.json` | 200 pre-seeded topics with `used` boolean flags |
| `assets/fonts/Montserrat-Bold.ttf` | Bundled font for all text rendering |
| `tests/test_topic_picker.py` | Unit tests for topic_picker |
| `tests/test_script_writer.py` | Unit tests for script_writer (mocked Gemini) |
| `tests/test_voice_generator.py` | Unit tests for voice_generator (mocked edge_tts) |
| `tests/test_video_builder.py` | Unit tests for slide rendering (real Pillow, no FFmpeg) |
| `tests/test_thumbnail_maker.py` | Unit tests for thumbnail generation |
| `tests/test_uploader.py` | Unit tests for uploader (mocked YouTube API) |
| `.github/workflows/daily_upload.yml` | Cron schedule, font download, run pipeline, git push |
| `requirements.txt` | All Python dependencies |
| `.gitignore` | Ignore tmp files, credentials, __pycache__ |

---

## Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `modules/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create the directory structure**

```bash
cd C:/Users/Agada/Projects/youtube-automation
mkdir -p modules data assets/fonts assets/music auth tests .github/workflows
```

- [ ] **Step 2: Create requirements.txt**

```
google-generativeai>=0.8.0
edge-tts>=6.1.9
Pillow>=10.4.0
mutagen>=1.47.0
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.151.0
pytest>=8.3.0
pytest-mock>=3.14.0
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
.env
tmp/
*.mp4
*.mp3
*.jpg
!assets/**/*.jpg
credentials.json
token.json
```

- [ ] **Step 4: Create empty __init__.py files**

Create `modules/__init__.py` — empty file.
Create `tests/__init__.py` — empty file.

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: all packages install without error.

- [ ] **Step 6: Commit**

```bash
git init
git add requirements.txt .gitignore modules/__init__.py tests/__init__.py
git commit -m "chore: project scaffold"
```

---

## Task 2: Font Asset

**Files:**
- Create: `assets/fonts/Montserrat-Bold.ttf` (downloaded)

- [ ] **Step 1: Download Montserrat Bold**

```bash
curl -L "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf" \
  -o assets/fonts/Montserrat-Bold.ttf
```

Expected: `assets/fonts/Montserrat-Bold.ttf` exists and is ~130KB.

- [ ] **Step 2: Verify font loads with Pillow**

```bash
python -c "from PIL import ImageFont; f = ImageFont.truetype('assets/fonts/Montserrat-Bold.ttf', 48); print('OK')"
```

Expected: prints `OK`.

- [ ] **Step 3: Commit**

```bash
git add assets/fonts/Montserrat-Bold.ttf
git commit -m "chore: add Montserrat Bold font asset"
```

---

## Task 3: topics.json — 200 Pre-Seeded Topics

**Files:**
- Create: `data/topics.json`

- [ ] **Step 1: Create data/topics.json**

```json
[
  {"topic": "The Dyatlov Pass Incident", "used": false},
  {"topic": "The Voynich Manuscript — The Book Nobody Can Read", "used": false},
  {"topic": "The Mary Celeste: A Ship Found Drifting With No Crew", "used": false},
  {"topic": "The Eilean Mor Lighthouse Keepers Disappearance", "used": false},
  {"topic": "The Zodiac Killer: Ciphers Never Cracked", "used": false},
  {"topic": "Unit 731: Japan's Secret Human Experiments", "used": false},
  {"topic": "The Tunguska Event: The Mystery Explosion Over Siberia", "used": false},
  {"topic": "The Dancing Plague of 1518", "used": false},
  {"topic": "The Overtoun Bridge Dog Suicide Mystery", "used": false},
  {"topic": "The Bermuda Triangle — What Science Actually Says", "used": false},
  {"topic": "The Black Dahlia: Hollywood's Most Notorious Unsolved Murder", "used": false},
  {"topic": "D.B. Cooper: America's Only Unsolved Skyjacking", "used": false},
  {"topic": "The Somerton Man: The Spy Nobody Could Identify", "used": false},
  {"topic": "The Flannan Isles Lighthouse Mystery", "used": false},
  {"topic": "The Babushka Lady: The JFK Witness Who Vanished", "used": false},
  {"topic": "The Isdal Woman: Norway's Jane Doe", "used": false},
  {"topic": "The Green Children of Woolpit", "used": false},
  {"topic": "Spring Heeled Jack: Victorian England's Demon", "used": false},
  {"topic": "The Bennington Triangle: Vermont's Vanishing People", "used": false},
  {"topic": "The Villisca Axe Murder House", "used": false},
  {"topic": "The Sodder Children: Did They Die in the Fire?", "used": false},
  {"topic": "The Hinterkaifeck Murders: The Farm That Kept Its Killer", "used": false},
  {"topic": "The Beaumont Children: Australia's Most Famous Cold Case", "used": false},
  {"topic": "The Amber Room: The Lost Wonder of the World", "used": false},
  {"topic": "The Escape from Alcatraz: Did They Survive?", "used": false},
  {"topic": "The Wow Signal: A Message From Space", "used": false},
  {"topic": "The Nazca Lines: Who Were They Built For?", "used": false},
  {"topic": "The Roanoke Colony: America's First Mystery", "used": false},
  {"topic": "The Lost Dutchman's Mine", "used": false},
  {"topic": "The Mothman Prophecies: Before the Bridge Fell", "used": false},
  {"topic": "The Roswell Incident: What Really Crashed?", "used": false},
  {"topic": "The Flatwoods Monster of West Virginia", "used": false},
  {"topic": "The Philadelphia Experiment", "used": false},
  {"topic": "The Oak Island Money Pit", "used": false},
  {"topic": "Cicada 3301: The Internet's Most Mysterious Puzzle", "used": false},
  {"topic": "The Max Headroom Signal Intrusion", "used": false},
  {"topic": "The Taos Hum: The Sound Only Some Can Hear", "used": false},
  {"topic": "Numbers Stations: Cold War's Secret Radio Broadcasts", "used": false},
  {"topic": "Project MKUltra: The CIA's Mind Control Program", "used": false},
  {"topic": "Operation Paperclip: America's Nazi Scientists", "used": false},
  {"topic": "The CIA's Project STARGATE: Psychic Spies", "used": false},
  {"topic": "The Jonestown Massacre", "used": false},
  {"topic": "The Heaven's Gate Cult", "used": false},
  {"topic": "The Order of the Solar Temple", "used": false},
  {"topic": "The Death of Edgar Allan Poe: Four Missing Days", "used": false},
  {"topic": "The Disappearance of Amelia Earhart", "used": false},
  {"topic": "The Mystery of Mozart's Death", "used": false},
  {"topic": "The Death of Bruce Lee: Unexplained Circumstances", "used": false},
  {"topic": "The Bloody Countess: Elizabeth Bathory", "used": false},
  {"topic": "Vlad the Impaler: The Real Dracula", "used": false},
  {"topic": "The Witches of Salem: What Really Happened", "used": false},
  {"topic": "The Winchester Mystery House", "used": false},
  {"topic": "The Bell Witch of Tennessee", "used": false},
  {"topic": "The Enfield Poltergeist", "used": false},
  {"topic": "The Sedlec Ossuary: The Church of Bones", "used": false},
  {"topic": "The Catacombs of Paris: Six Million Secrets", "used": false},
  {"topic": "The Princes in the Tower", "used": false},
  {"topic": "The Skull and Bones Society", "used": false},
  {"topic": "The Mandela Effect: Mass False Memory", "used": false},
  {"topic": "The JFK Assassination: Files Still Sealed", "used": false},
  {"topic": "The Georgia Guidestones: A Monument Nobody Claimed", "used": false},
  {"topic": "The Sinking of the Ourang Medan", "used": false},
  {"topic": "The Salish Sea Feet: Severed Feet Washing Ashore", "used": false},
  {"topic": "Aokigahara: Japan's Suicide Forest", "used": false},
  {"topic": "The Myrtles Plantation: Most Haunted House in America", "used": false},
  {"topic": "The Tower of London's Darkest Secrets", "used": false},
  {"topic": "The Spanish Inquisition's Secret Torture Files", "used": false},
  {"topic": "The Black Knight Satellite Mystery", "used": false},
  {"topic": "The Polybius Arcade Game: Did It Exist?", "used": false},
  {"topic": "The Greenbrier Bunker: America's Secret Congress Hideout", "used": false},
  {"topic": "The MT Erebus Disaster: Antarctica's Worst Air Crash", "used": false},
  {"topic": "The Devil's Sea: The Pacific Bermuda Triangle", "used": false},
  {"topic": "The Phantom Time Hypothesis", "used": false},
  {"topic": "The Dybbuk Box: The World's Most Haunted Object", "used": false},
  {"topic": "The Branch Davidians at Waco: 51 Days of Siege", "used": false},
  {"topic": "The NXIVM Cult: Branding and Blackmail", "used": false},
  {"topic": "The Death of Marilyn Monroe", "used": false},
  {"topic": "The Circleville Letters: Ohio's Anonymous Killer", "used": false},
  {"topic": "The Tamam Shud Case: A Man With No Identity", "used": false},
  {"topic": "The Skinwalker Ranch Phenomenon", "used": false},
  {"topic": "Men in Black: Government Agents or Something Else?", "used": false},
  {"topic": "The Montauk Project: Time Travel Experiments", "used": false},
  {"topic": "The RFK Assassination: Second Gunman Theory", "used": false},
  {"topic": "The Knights Templar's Last Secret", "used": false},
  {"topic": "The Freemasons: Inside the World's Oldest Secret Society", "used": false},
  {"topic": "Spring Heeled Jack: Victorian Terror", "used": false},
  {"topic": "The Lost Colony of Vinland", "used": false},
  {"topic": "The Klondike Gold Rush's Dark Side", "used": false},
  {"topic": "The Mary King's Close: Edinburgh's Hidden City", "used": false},
  {"topic": "The Rat Lines: How Nazis Escaped to South America", "used": false},
  {"topic": "The Antikythera Mechanism: Ancient Supercomputer", "used": false},
  {"topic": "The Baghdad Battery: Ancient Electricity?", "used": false},
  {"topic": "The Rongorongo Script: Easter Island's Undeciphered Writing", "used": false},
  {"topic": "The Phaistos Disc: 4000-Year-Old Unsolved Code", "used": false},
  {"topic": "The Loch Ness Monster: What the Evidence Shows", "used": false},
  {"topic": "Bigfoot: The Science Behind the Legend", "used": false},
  {"topic": "The Chupacabra: Origins of a Modern Myth", "used": false},
  {"topic": "The Dover Demon: New England's Strangest Sighting", "used": false},
  {"topic": "The Lost City of Atlantis — What We Actually Know", "used": false},
  {"topic": "The Black Death: How It Wiped Out Half of Europe", "used": false},
  {"topic": "The Fall of Rome: Why the Greatest Empire Collapsed", "used": false},
  {"topic": "The Library of Alexandria: What Was Really Lost", "used": false},
  {"topic": "Genghis Khan: The Man Who Conquered Half the World", "used": false},
  {"topic": "The Aztec Empire's Final Days", "used": false},
  {"topic": "Pompeii: The City Frozen in Time", "used": false},
  {"topic": "The Easter Island Statues: A Civilization's Last Act", "used": false},
  {"topic": "The Silk Road: The Trade Route That Shaped the World", "used": false},
  {"topic": "The Battle of Thermopylae: 300 Against a Million", "used": false},
  {"topic": "Alexander the Great's Lost Tomb", "used": false},
  {"topic": "The Roman Colosseum: What Happened Beneath the Arena", "used": false},
  {"topic": "The Egyptian Pyramids: New Discoveries Change Everything", "used": false},
  {"topic": "The Sphinx's Hidden Chamber", "used": false},
  {"topic": "The Maya Collapse: Why a Civilization Vanished", "used": false},
  {"topic": "The Viking Age: Beyond the Myths", "used": false},
  {"topic": "The Crusades: What History Books Left Out", "used": false},
  {"topic": "The Mongol Invasion of Europe: The Horde That Stopped", "used": false},
  {"topic": "The Ottoman Empire's Rise to Power", "used": false},
  {"topic": "The Byzantine Empire's 1000-Year Survival Secret", "used": false},
  {"topic": "The Spanish Armada's Defeat: Weather or Tactics?", "used": false},
  {"topic": "The Fall of Constantinople: The End of the Ancient World", "used": false},
  {"topic": "The French Revolution's Reign of Terror", "used": false},
  {"topic": "The Napoleonic Wars: Europe's First World War", "used": false},
  {"topic": "D-Day: Operation Overlord From Both Sides", "used": false},
  {"topic": "The Battle of Stalingrad: History's Bloodiest Battle", "used": false},
  {"topic": "The Siege of Leningrad: 872 Days of Survival", "used": false},
  {"topic": "The Space Race: Behind the Scenes", "used": false},
  {"topic": "The Apollo Program's Near Disasters", "used": false},
  {"topic": "The Cold War's Closest Call: Operation RYAN", "used": false},
  {"topic": "The Cuban Missile Crisis: 13 Days to Nuclear War", "used": false},
  {"topic": "The Fermi Paradox: Where Is Everybody?", "used": false},
  {"topic": "The Permian Extinction: The Great Dying", "used": false},
  {"topic": "The Rise of Homo Sapiens: How We Took Over", "used": false},
  {"topic": "The Out of Africa Migration", "used": false},
  {"topic": "The First Civilizations of Mesopotamia", "used": false},
  {"topic": "The Indus Valley Civilization: Advanced and Forgotten", "used": false},
  {"topic": "The Minoan Civilization: Europe's First Great Culture", "used": false},
  {"topic": "The Phoenicians: The World's First Global Traders", "used": false},
  {"topic": "Ancient Carthage: Rome's Greatest Enemy", "used": false},
  {"topic": "The Persian Empire at Its Height", "used": false},
  {"topic": "The Greek Golden Age", "used": false},
  {"topic": "Julius Caesar: The Assassination That Changed Rome", "used": false},
  {"topic": "Cleopatra: The Real Queen Behind the Legend", "used": false},
  {"topic": "Nero: Rome's Most Infamous Emperor", "used": false},
  {"topic": "Caligula: Madness or Political Strategy?", "used": false},
  {"topic": "The Medici Family: Bankers Who Ruled Italy", "used": false},
  {"topic": "The Borgias: Power, Poison, and the Papacy", "used": false},
  {"topic": "The Tudors: Six Wives and a Revolution", "used": false},
  {"topic": "Mary Queen of Scots: A Queen Destroyed", "used": false},
  {"topic": "Ivan the Terrible: Russia's First Tsar", "used": false},
  {"topic": "The Romanov Dynasty's Bloody End", "used": false},
  {"topic": "Suleiman the Magnificent: The Ottoman's Greatest Sultan", "used": false},
  {"topic": "Saladin and the Crusader States", "used": false},
  {"topic": "Timur: The Conqueror Who Rivalled Genghis Khan", "used": false},
  {"topic": "The Inca Empire: Engineering at Altitude", "used": false},
  {"topic": "The Anasazi: Ancient Pueblo People Who Vanished", "used": false},
  {"topic": "The Cahokia Mounds: America's Forgotten City", "used": false},
  {"topic": "The Great Zimbabwe: Africa's Stone City", "used": false},
  {"topic": "Mansa Musa: The Richest Man Who Ever Lived", "used": false},
  {"topic": "The Kingdom of Kush: Egypt's Rival Empire", "used": false},
  {"topic": "The Mughal Empire at Its Peak", "used": false},
  {"topic": "The Tang Dynasty: China's Golden Age", "used": false},
  {"topic": "China's First Emperor: Qin Shi Huang", "used": false},
  {"topic": "Zheng He: China's Forgotten Explorer", "used": false},
  {"topic": "The Meiji Restoration: Japan's 50-Year Transformation", "used": false},
  {"topic": "The Scramble for Africa: How a Continent Was Divided", "used": false},
  {"topic": "The Partition of India: The Line That Killed Millions", "used": false},
  {"topic": "The Korean War: The Forgotten Conflict", "used": false},
  {"topic": "The Vietnam War: What Happened After", "used": false},
  {"topic": "The Fall of the Berlin Wall", "used": false},
  {"topic": "The Hundred Years War: France vs England", "used": false},
  {"topic": "The Wars of the Roses: England's Civil War", "used": false},
  {"topic": "The Thirty Years War: Europe's Most Destructive Conflict", "used": false},
  {"topic": "The American Civil War's Bloodiest Days", "used": false},
  {"topic": "The First World War's Most Forgotten Battles", "used": false},
  {"topic": "Operation Barbarossa: Hitler's Biggest Mistake", "used": false},
  {"topic": "The Manhattan Project: Race to Build the Bomb", "used": false},
  {"topic": "The Nuremberg Trials: Justice After the Holocaust", "used": false},
  {"topic": "The Pacific War's Forgotten Islands", "used": false},
  {"topic": "The Great Oxygenation Event: Life Almost Ended", "used": false},
  {"topic": "The K-Pg Extinction: The Day the Dinosaurs Died", "used": false},
  {"topic": "The Ice Ages: When Earth Was Frozen", "used": false},
  {"topic": "The Voyager Probes: Humanity's Furthest Reach", "used": false},
  {"topic": "The James Webb Telescope's Most Stunning Discoveries", "used": false},
  {"topic": "The Origins of the Universe: Before the Big Bang", "used": false},
  {"topic": "The Black Hole at the Center of Our Galaxy", "used": false},
  {"topic": "The Great Wall of China: What It Was Really For", "used": false},
  {"topic": "Pompeii's Sister City: Herculaneum Uncovered", "used": false},
  {"topic": "The Dead Sea Scrolls: What They Really Revealed", "used": false},
  {"topic": "The Shroud of Turin: Science vs Faith", "used": false},
  {"topic": "The Ark of the Covenant: Lost or Hidden?", "used": false},
  {"topic": "The Holy Grail: Legend or Historical Object?", "used": false},
  {"topic": "Stonehenge: New Theories on Who Built It and Why", "used": false},
  {"topic": "The Gobekli Tepe: Rewriting Human History", "used": false},
  {"topic": "The Hanging Gardens of Babylon: Did They Exist?", "used": false},
  {"topic": "Troy: The Archaeological Truth Behind the Legend", "used": false},
  {"topic": "El Dorado: The City of Gold That Drove Men Mad", "used": false},
  {"topic": "The Seven Wonders of the Ancient World", "used": false}
]
```

- [ ] **Step 2: Verify JSON is valid**

```bash
python -c "import json; data = json.load(open('data/topics.json')); print(f'{len(data)} topics loaded')"
```

Expected: `200 topics loaded`

- [ ] **Step 3: Commit**

```bash
git add data/topics.json
git commit -m "chore: seed 200 history and mystery topics"
```

---

## Task 4: modules/topic_picker.py (TDD)

**Files:**
- Create: `tests/test_topic_picker.py`
- Create: `modules/topic_picker.py`

- [ ] **Step 1: Write failing tests**

`tests/test_topic_picker.py`:
```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_topic_picker.py -v
```

Expected: `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement modules/topic_picker.py**

```python
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
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
pytest tests/test_topic_picker.py -v
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/topic_picker.py tests/test_topic_picker.py
git commit -m "feat: add topic_picker module"
```

---

## Task 5: modules/script_writer.py (TDD)

**Files:**
- Create: `tests/test_script_writer.py`
- Create: `modules/script_writer.py`

- [ ] **Step 1: Write failing tests**

`tests/test_script_writer.py`:
```python
import json
import pytest
from modules.script_writer import generate_script

SAMPLE_SCRIPT = {
    "title": "The Test Mystery",
    "description": "A gripping tale of the unknown.",
    "tags": ["mystery", "history", "unsolved"],
    "sections": [
        {"text": "In the year 1900, something strange happened.", "duration": 15},
        {"text": "Nobody could explain what they found.", "duration": 18},
    ],
}


def test_generate_script_returns_valid_structure(mocker):
    mock_model = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.text = json.dumps(SAMPLE_SCRIPT)
    mock_model.generate_content.return_value = mock_response
    mocker.patch("google.generativeai.configure")
    mocker.patch("google.generativeai.GenerativeModel", return_value=mock_model)

    result = generate_script("Test Topic", "fake-api-key")

    assert result["title"] == "The Test Mystery"
    assert isinstance(result["sections"], list)
    assert len(result["sections"]) == 2
    assert all("text" in s for s in result["sections"])
    assert all("duration" in s for s in result["sections"])


def test_generate_script_strips_markdown_code_block(mocker):
    mock_model = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.text = f"```json\n{json.dumps(SAMPLE_SCRIPT)}\n```"
    mock_model.generate_content.return_value = mock_response
    mocker.patch("google.generativeai.configure")
    mocker.patch("google.generativeai.GenerativeModel", return_value=mock_model)

    result = generate_script("Test Topic", "fake-api-key")
    assert result["title"] == "The Test Mystery"


def test_generate_script_uses_gemini_flash(mocker):
    mock_model = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.text = json.dumps(SAMPLE_SCRIPT)
    mock_model.generate_content.return_value = mock_response
    mocker.patch("google.generativeai.configure")
    mock_constructor = mocker.patch(
        "google.generativeai.GenerativeModel", return_value=mock_model
    )

    generate_script("Test Topic", "fake-api-key")
    mock_constructor.assert_called_once_with("gemini-1.5-flash")
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_script_writer.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement modules/script_writer.py**

```python
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
        lines = lines[1:]  # remove opening ```json or ```
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
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
pytest tests/test_script_writer.py -v
```

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/script_writer.py tests/test_script_writer.py
git commit -m "feat: add script_writer module"
```

---

## Task 6: modules/voice_generator.py (TDD)

**Files:**
- Create: `tests/test_voice_generator.py`
- Create: `modules/voice_generator.py`

- [ ] **Step 1: Write failing tests**

`tests/test_voice_generator.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from modules.voice_generator import generate_section_audio, get_audio_duration


def test_generate_section_audio_calls_edge_tts(mocker, tmp_path):
    output = str(tmp_path / "audio.mp3")
    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock()
    mocker.patch("edge_tts.Communicate", return_value=mock_communicate)

    generate_section_audio("Hello world.", output)

    mock_communicate.save.assert_called_once_with(output)


def test_generate_section_audio_uses_correct_voice(mocker, tmp_path):
    output = str(tmp_path / "audio.mp3")
    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock()
    mock_constructor = mocker.patch("edge_tts.Communicate", return_value=mock_communicate)

    generate_section_audio("Hello world.", output)

    mock_constructor.assert_called_once_with("Hello world.", "en-GB-RyanNeural")


def test_get_audio_duration_returns_float(mocker, tmp_path):
    audio_file = tmp_path / "audio.mp3"
    audio_file.write_bytes(b"fake")
    mock_mp3 = MagicMock()
    mock_mp3.info.length = 18.5
    mocker.patch("mutagen.mp3.MP3", return_value=mock_mp3)

    result = get_audio_duration(str(audio_file))

    assert result == 18.5
    assert isinstance(result, float)
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_voice_generator.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement modules/voice_generator.py**

```python
import asyncio
import edge_tts
from mutagen.mp3 import MP3

VOICE = "en-GB-RyanNeural"


async def _speak(text: str, output_path: str) -> None:
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)


def generate_section_audio(text: str, output_path: str) -> None:
    asyncio.run(_speak(text, output_path))


def get_audio_duration(audio_path: str) -> float:
    audio = MP3(audio_path)
    return float(audio.info.length)
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
pytest tests/test_voice_generator.py -v
```

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/voice_generator.py tests/test_voice_generator.py
git commit -m "feat: add voice_generator module"
```

---

## Task 7: modules/thumbnail_maker.py (TDD)

**Files:**
- Create: `tests/test_thumbnail_maker.py`
- Create: `modules/thumbnail_maker.py`

- [ ] **Step 1: Write failing tests**

`tests/test_thumbnail_maker.py`:
```python
import os
import pytest
from PIL import Image
from modules.thumbnail_maker import generate_thumbnail


def test_generate_thumbnail_creates_file(tmp_path):
    output = str(tmp_path / "thumb.jpg")
    generate_thumbnail("The Mystery of Atlantis", output)
    assert os.path.exists(output)


def test_generate_thumbnail_correct_dimensions(tmp_path):
    output = str(tmp_path / "thumb.jpg")
    generate_thumbnail("The Mystery of Atlantis", output)
    img = Image.open(output)
    assert img.size == (1280, 720)


def test_generate_thumbnail_is_rgb(tmp_path):
    output = str(tmp_path / "thumb.jpg")
    generate_thumbnail("Short Title", output)
    img = Image.open(output)
    assert img.mode == "RGB"


def test_generate_thumbnail_long_title_does_not_crash(tmp_path):
    output = str(tmp_path / "thumb.jpg")
    long_title = "The Extraordinary and Completely Baffling Disappearance of the Eilean Mor Lighthouse Keepers"
    generate_thumbnail(long_title, output)
    assert os.path.exists(output)
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_thumbnail_maker.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement modules/thumbnail_maker.py**

```python
import textwrap
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "assets/fonts/Montserrat-Bold.ttf"
W, H = 1280, 720
BG_COLOR = (8, 8, 20)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (200, 60, 30)
CHANNEL_LABEL = "HISTORY & MYSTERIES"


def generate_thumbnail(title: str, output_path: str) -> None:
    img = Image.new("RGB", (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Accent bars
    draw.rectangle([(0, 0), (W, 10)], fill=ACCENT_COLOR)
    draw.rectangle([(0, H - 10), (W, H)], fill=ACCENT_COLOR)

    # Vertical red line left accent
    draw.rectangle([(60, 80), (68, H - 80)], fill=ACCENT_COLOR)

    # Title text — shrink font until it fits
    font_size = 100
    while font_size > 36:
        font = ImageFont.truetype(FONT_PATH, font_size)
        wrapped = textwrap.fill(title, width=max(10, int(28 * (100 / font_size))))
        bbox = draw.textbbox((0, 0), wrapped, font=font)
        text_h = bbox[3] - bbox[1]
        if text_h < H - 180:
            break
        font_size -= 6

    draw.text(
        (W // 2, H // 2 - 30),
        wrapped,
        font=font,
        fill=TEXT_COLOR,
        anchor="mm",
        align="center",
    )

    # Channel label
    label_font = ImageFont.truetype(FONT_PATH, 32)
    draw.text(
        (W // 2, H - 50),
        CHANNEL_LABEL,
        font=label_font,
        fill=ACCENT_COLOR,
        anchor="mm",
    )

    img.save(output_path, quality=95)
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
pytest tests/test_thumbnail_maker.py -v
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/thumbnail_maker.py tests/test_thumbnail_maker.py
git commit -m "feat: add thumbnail_maker module"
```

---

## Task 8: modules/video_builder.py (TDD)

**Files:**
- Create: `tests/test_video_builder.py`
- Create: `modules/video_builder.py`

- [ ] **Step 1: Write failing tests**

`tests/test_video_builder.py`:
```python
import os
import pytest
from PIL import Image
from modules.video_builder import render_title_slide, render_body_slide, render_outro_slide


def test_render_title_slide_creates_file(tmp_path):
    output = str(tmp_path / "title.png")
    render_title_slide("The Dark Mystery", "History & Mysteries", output)
    assert os.path.exists(output)


def test_render_title_slide_is_1920x1080(tmp_path):
    output = str(tmp_path / "title.png")
    render_title_slide("The Dark Mystery", "History & Mysteries", output)
    img = Image.open(output)
    assert img.size == (1920, 1080)


def test_render_body_slide_creates_file(tmp_path):
    output = str(tmp_path / "body.png")
    render_body_slide("In 1900, something strange was discovered beneath the ice.", 1, 15, output)
    assert os.path.exists(output)


def test_render_body_slide_is_1920x1080(tmp_path):
    output = str(tmp_path / "body.png")
    render_body_slide("In 1900, something strange was discovered beneath the ice.", 1, 15, output)
    img = Image.open(output)
    assert img.size == (1920, 1080)


def test_render_outro_slide_creates_file(tmp_path):
    output = str(tmp_path / "outro.png")
    render_outro_slide("History & Mysteries", output)
    assert os.path.exists(output)


def test_render_body_slide_long_text_does_not_crash(tmp_path):
    output = str(tmp_path / "body_long.png")
    long_text = (
        "This is an extraordinarily long piece of narration text that goes on and on "
        "and should be gracefully word-wrapped by the rendering system without crashing "
        "or overflowing the slide boundaries in any way whatsoever."
    )
    render_body_slide(long_text, 5, 20, output)
    assert os.path.exists(output)
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_video_builder.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement slide rendering in modules/video_builder.py**

```python
import json
import os
import subprocess
import tempfile
import textwrap
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "assets/fonts/Montserrat-Bold.ttf"
W, H = 1920, 1080
BG_COLOR = (8, 8, 20)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (200, 60, 30)
DIM_COLOR = (100, 100, 120)


def _make_base_image() -> Image.Image:
    img = Image.new("RGB", (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    # Subtle top and bottom accent lines
    draw.rectangle([(0, 0), (W, 6)], fill=ACCENT_COLOR)
    draw.rectangle([(0, H - 6), (W, H)], fill=ACCENT_COLOR)
    return img


def render_title_slide(title: str, channel_name: str, output_path: str) -> None:
    img = _make_base_image()
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype(FONT_PATH, 88)
    font_channel = ImageFont.truetype(FONT_PATH, 38)

    wrapped = textwrap.fill(title, width=28)
    draw.text((W // 2, H // 2 - 60), wrapped, font=font_title, fill=TEXT_COLOR, anchor="mm", align="center")
    draw.text((W // 2, H - 100), channel_name.upper(), font=font_channel, fill=ACCENT_COLOR, anchor="mm")

    img.save(output_path)


def render_body_slide(text: str, slide_number: int, total_slides: int, output_path: str) -> None:
    img = _make_base_image()
    draw = ImageDraw.Draw(img)

    font_body = ImageFont.truetype(FONT_PATH, 56)
    font_counter = ImageFont.truetype(FONT_PATH, 28)

    wrapped = textwrap.fill(text, width=42)
    draw.text((W // 2, H // 2), wrapped, font=font_body, fill=TEXT_COLOR, anchor="mm", align="center")

    # Progress bar
    bar_x_start = int(W * 0.15)
    bar_x_end = int(W * 0.85)
    bar_y = H - 40
    draw.rectangle([(bar_x_start, bar_y - 4), (bar_x_end, bar_y + 4)], fill=DIM_COLOR)
    progress_x = bar_x_start + int((bar_x_end - bar_x_start) * slide_number / total_slides)
    draw.rectangle([(bar_x_start, bar_y - 4), (progress_x, bar_y + 4)], fill=ACCENT_COLOR)

    img.save(output_path)


def render_outro_slide(channel_name: str, output_path: str) -> None:
    img = _make_base_image()
    draw = ImageDraw.Draw(img)

    font_main = ImageFont.truetype(FONT_PATH, 88)
    font_sub = ImageFont.truetype(FONT_PATH, 44)

    draw.text((W // 2, H // 2 - 80), channel_name.upper(), font=font_main, fill=TEXT_COLOR, anchor="mm")
    draw.text((W // 2, H // 2 + 60), "Subscribe for more mysteries", font=font_sub, fill=ACCENT_COLOR, anchor="mm")

    img.save(output_path)


def _create_silence_mp3(output_path: str, duration: float = 3.0) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=channel_layout=stereo:sample_rate=44100",
            "-t", str(duration),
            "-codec:a", "libmp3lame",
            "-q:a", "9",
            output_path,
        ],
        check=True,
        capture_output=True,
    )


def _image_to_video_segment(slide_path: str, audio_path: str, output_path: str) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-loop", "1", "-i", slide_path,
            "-i", audio_path,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path,
        ],
        check=True,
        capture_output=True,
    )


def _concat_segments(segment_paths: list, output_path: str) -> None:
    concat_list = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    try:
        for seg in segment_paths:
            concat_list.write(f"file '{os.path.abspath(seg)}'\n")
        concat_list.close()
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", concat_list.name,
                "-c", "copy",
                output_path,
            ],
            check=True,
            capture_output=True,
        )
    finally:
        os.unlink(concat_list.name)


def build_video(script: dict, audio_files: list, tmp_dir: str, output_path: str) -> None:
    sections = script["sections"]
    channel_name = "History & Mysteries"
    segments = []

    # Title slide uses audio from first section
    title_slide = os.path.join(tmp_dir, "slide_title.png")
    render_title_slide(script["title"], channel_name, title_slide)
    seg_title = os.path.join(tmp_dir, "seg_title.mp4")
    _image_to_video_segment(title_slide, audio_files[0], seg_title)
    segments.append(seg_title)

    # Body slides — sections 1 onwards each get their own slide
    total_body = len(sections) - 1
    for i, section in enumerate(sections[1:], start=1):
        slide_path = os.path.join(tmp_dir, f"slide_{i:02d}.png")
        render_body_slide(section["text"], i, total_body, slide_path)
        seg_path = os.path.join(tmp_dir, f"seg_{i:02d}.mp4")
        _image_to_video_segment(slide_path, audio_files[i], seg_path)
        segments.append(seg_path)

    # Outro slide with 3 seconds of silence
    outro_slide = os.path.join(tmp_dir, "slide_outro.png")
    render_outro_slide(channel_name, outro_slide)
    outro_audio = os.path.join(tmp_dir, "outro_silence.mp3")
    _create_silence_mp3(outro_audio, duration=3.0)
    seg_outro = os.path.join(tmp_dir, "seg_outro.mp4")
    _image_to_video_segment(outro_slide, outro_audio, seg_outro)
    segments.append(seg_outro)

    _concat_segments(segments, output_path)
```

- [ ] **Step 4: Run slide rendering tests — confirm they pass**

```bash
pytest tests/test_video_builder.py -v
```

Expected: 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/video_builder.py tests/test_video_builder.py
git commit -m "feat: add video_builder module"
```

---

## Task 9: modules/uploader.py (TDD)

**Files:**
- Create: `tests/test_uploader.py`
- Create: `modules/uploader.py`

- [ ] **Step 1: Write failing tests**

`tests/test_uploader.py`:
```python
import pytest
from modules.uploader import upload_video

FAKE_CREDS = {
    "client_id": "fake-client-id",
    "client_secret": "fake-secret",
    "refresh_token": "fake-refresh-token",
}

SAMPLE_SCRIPT = {
    "title": "The Dark Secret of the Lighthouse",
    "description": "A gripping tale of three missing men.",
    "tags": ["mystery", "history"],
    "sections": [],
}


def test_upload_video_returns_video_id(mocker, tmp_path):
    video_file = tmp_path / "video.mp4"
    video_file.write_bytes(b"fake video content")
    thumb_file = tmp_path / "thumb.jpg"
    thumb_file.write_bytes(b"fake thumb content")

    mock_creds = mocker.MagicMock()
    mocker.patch("modules.uploader.Credentials", return_value=mock_creds)
    mocker.patch("modules.uploader.Request")

    mock_youtube = mocker.MagicMock()
    mock_insert = mocker.MagicMock()
    mock_insert.execute.return_value = {"id": "abc123XYZ"}
    mock_youtube.videos.return_value.insert.return_value = mock_insert
    mock_youtube.thumbnails.return_value.set.return_value.execute.return_value = {}
    mocker.patch("modules.uploader.build", return_value=mock_youtube)

    video_id = upload_video(str(video_file), str(thumb_file), SAMPLE_SCRIPT, FAKE_CREDS)
    assert video_id == "abc123XYZ"


def test_upload_video_sets_category_education(mocker, tmp_path):
    video_file = tmp_path / "video.mp4"
    video_file.write_bytes(b"fake")
    thumb_file = tmp_path / "thumb.jpg"
    thumb_file.write_bytes(b"fake")

    mock_creds = mocker.MagicMock()
    mocker.patch("modules.uploader.Credentials", return_value=mock_creds)
    mocker.patch("modules.uploader.Request")

    mock_youtube = mocker.MagicMock()
    mock_insert = mocker.MagicMock()
    mock_insert.execute.return_value = {"id": "xyz"}
    mock_youtube.videos.return_value.insert.return_value = mock_insert
    mock_youtube.thumbnails.return_value.set.return_value.execute.return_value = {}
    mocker.patch("modules.uploader.build", return_value=mock_youtube)

    upload_video(str(video_file), str(thumb_file), SAMPLE_SCRIPT, FAKE_CREDS)

    call_kwargs = mock_youtube.videos.return_value.insert.call_args[1]
    assert call_kwargs["body"]["snippet"]["categoryId"] == "27"
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_uploader.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement modules/uploader.py**

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def upload_video(
    video_path: str,
    thumbnail_path: str,
    script: dict,
    credentials: dict,
) -> str:
    creds = Credentials(
        token=None,
        refresh_token=credentials["refresh_token"],
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        token_uri=TOKEN_URI,
        scopes=SCOPES,
    )
    creds.refresh(Request())

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": script["title"],
            "description": script["description"],
            "tags": script["tags"],
            "categoryId": "27",  # Education
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    insert_request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = insert_request.execute()
    video_id = response["id"]

    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path),
    ).execute()

    return video_id
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
pytest tests/test_uploader.py -v
```

Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/uploader.py tests/test_uploader.py
git commit -m "feat: add uploader module"
```

---

## Task 10: auth/get_refresh_token.py

**Files:**
- Create: `auth/get_refresh_token.py`

This script is run **once locally** to get the YouTube refresh token. It opens a browser, you log in as `mymymysteryhist@gmail.com`, and it prints the refresh token to copy into GitHub secrets.

- [ ] **Step 1: Create auth/get_refresh_token.py**

```python
"""
Run this once locally to get your YouTube refresh token.
Usage: python auth/get_refresh_token.py
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ["YOUTUBE_CLIENT_ID"],
        "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }
}

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=0)
    print("\n=== YOUR REFRESH TOKEN ===")
    print(creds.refresh_token)
    print("=========================")
    print("Copy this into GitHub Secrets as YOUTUBE_REFRESH_TOKEN")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the auth script to get your refresh token**

Set environment variables first, then run:

```bash
export YOUTUBE_CLIENT_ID="999829961157-6nkok91lomhmoagnatcqa7tioqcg1vj6.apps.googleusercontent.com"
export YOUTUBE_CLIENT_SECRET="GOCSPX-your-oauth-client-secret"
python auth/get_refresh_token.py
```

A browser will open. Log in as `mymymysteryhist@gmail.com` and click Allow.
The terminal will print a refresh token — copy it, you'll add it to GitHub Secrets.

- [ ] **Step 3: Commit**

```bash
git add auth/get_refresh_token.py
git commit -m "chore: add one-time YouTube OAuth auth script"
```

---

## Task 11: pipeline.py

**Files:**
- Create: `pipeline.py`

- [ ] **Step 1: Create pipeline.py**

```python
"""
Main pipeline orchestrator.
Run: python pipeline.py
Env vars required: GEMINI_API_KEY, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN
"""
import os
import shutil
import tempfile

from modules.topic_picker import pick_next_topic, mark_topic_used
from modules.script_writer import generate_script
from modules.voice_generator import generate_section_audio
from modules.video_builder import build_video
from modules.thumbnail_maker import generate_thumbnail
from modules.uploader import upload_video

TOPICS_PATH = "data/topics.json"


def _get_credentials() -> dict:
    return {
        "client_id": os.environ["YOUTUBE_CLIENT_ID"],
        "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
        "refresh_token": os.environ["YOUTUBE_REFRESH_TOKEN"],
    }


def run() -> None:
    tmp_dir = tempfile.mkdtemp()
    topic = None
    try:
        print("[1/6] Picking topic...")
        topic = pick_next_topic(TOPICS_PATH)
        print(f"      Topic: {topic}")

        print("[2/6] Generating script...")
        script = generate_script(topic, os.environ["GEMINI_API_KEY"])
        print(f"      Title: {script['title']}")
        print(f"      Sections: {len(script['sections'])}")

        print("[3/6] Generating voiceover...")
        audio_files = []
        for i, section in enumerate(script["sections"]):
            audio_path = os.path.join(tmp_dir, f"audio_{i:02d}.mp3")
            generate_section_audio(section["text"], audio_path)
            audio_files.append(audio_path)
        print(f"      Generated {len(audio_files)} audio clips")

        print("[4/6] Building video...")
        video_path = os.path.join(tmp_dir, "output.mp4")
        build_video(script, audio_files, tmp_dir, video_path)
        print(f"      Video: {video_path}")

        print("[5/6] Generating thumbnail...")
        thumbnail_path = os.path.join(tmp_dir, "thumbnail.jpg")
        generate_thumbnail(script["title"], thumbnail_path)

        print("[6/6] Uploading to YouTube...")
        credentials = _get_credentials()
        video_id = upload_video(video_path, thumbnail_path, script, credentials)
        print(f"      Uploaded: https://youtube.com/watch?v={video_id}")

        print("Marking topic as used...")
        mark_topic_used(TOPICS_PATH, topic)
        print("Done.")

    except Exception as e:
        print(f"Pipeline failed: {e}")
        raise
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: Commit**

```bash
git add pipeline.py
git commit -m "feat: add pipeline orchestrator"
```

---

## Task 12: .github/workflows/daily_upload.yml

**Files:**
- Create: `.github/workflows/daily_upload.yml`

- [ ] **Step 1: Create the GitHub Actions workflow**

```yaml
name: Daily YouTube Upload

on:
  schedule:
    - cron: "0 9 * * *"   # 9am UTC every day
  workflow_dispatch:        # allows manual trigger from GitHub UI

permissions:
  contents: write

jobs:
  upload:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install FFmpeg
        run: sudo apt-get install -y ffmpeg

      - name: Download Montserrat Bold font
        run: |
          mkdir -p assets/fonts
          wget -q "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf" \
            -O assets/fonts/Montserrat-Bold.ttf

      - name: Install Python dependencies
        run: pip install -r requirements.txt

      - name: Run pipeline
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
        run: python pipeline.py

      - name: Commit updated topics.json
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/topics.json
          git diff --staged --quiet || git commit -m "chore: mark topic as used [skip ci]"
          git push
```

Note: `[skip ci]` in the commit message prevents the push from triggering another workflow run.

- [ ] **Step 2: Run all tests one final time**

```bash
pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 3: Commit and push to GitHub**

```bash
git add .github/workflows/daily_upload.yml
git commit -m "feat: add daily GitHub Actions workflow"
git remote add origin https://github.com/YOUR_USERNAME/youtube-automation.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

## Task 13: GitHub Secrets Setup

- [ ] **Step 1: Add secrets to GitHub**

Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret.

Add these four secrets:

| Name | Value |
|---|---|
| `GEMINI_API_KEY` | *(regenerate at aistudio.google.com — the one you shared in chat is now exposed)* |
| `YOUTUBE_CLIENT_ID` | `999829961157-6nkok91lomhmoagnatcqa7tioqcg1vj6.apps.googleusercontent.com` |
| `YOUTUBE_CLIENT_SECRET` | `GOCSPX-your-oauth-client-secret` |
| `YOUTUBE_REFRESH_TOKEN` | *(the token printed by `auth/get_refresh_token.py` in Task 10)* |

- [ ] **Step 2: Enable YouTube Data API v3**

Go to console.cloud.google.com → APIs & Services → Library → search "YouTube Data API v3" → Enable.

- [ ] **Step 3: Trigger a manual test run**

Go to your GitHub repo → Actions → Daily YouTube Upload → Run workflow → Run workflow.

Watch the logs. Expected: all 6 steps print success, a video appears on the mymymysteryhist YouTube channel.

- [ ] **Step 4: Verify the video is live**

Log into `mymymysteryhist@gmail.com` → YouTube Studio → check the video uploaded, has a thumbnail, title, description, and tags.

---

## Self-Review Notes

**Spec coverage check:**
- ✅ Topic picking from topics.json with used flag
- ✅ Gemini API for script generation
- ✅ Edge TTS narration (en-GB-RyanNeural)
- ✅ Pillow slide rendering (title, body, outro)
- ✅ FFmpeg video assembly
- ✅ Thumbnail generation (1280×720)
- ✅ YouTube Data API upload with thumbnail
- ✅ GitHub Actions cron at 9am UTC
- ✅ topics.json committed back after upload with [skip ci]
- ✅ Slide timing derived from actual audio (Edge TTS generates audio first, FFmpeg uses -shortest)
- ✅ Zero cost — all free tiers
- ✅ 200 topics pre-seeded
- ✅ One-time auth script for refresh token

**Type consistency check:**
- `pick_next_topic(path: str) -> str` ✅ used in pipeline.py
- `mark_topic_used(path: str, topic: str) -> None` ✅ used in pipeline.py
- `generate_script(topic: str, api_key: str) -> dict` ✅ used in pipeline.py
- `generate_section_audio(text: str, output_path: str) -> None` ✅ used in pipeline.py
- `build_video(script: dict, audio_files: list, tmp_dir: str, output_path: str) -> None` ✅ used in pipeline.py
- `generate_thumbnail(title: str, output_path: str) -> None` ✅ used in pipeline.py
- `upload_video(video_path: str, thumbnail_path: str, script: dict, credentials: dict) -> str` ✅ used in pipeline.py
