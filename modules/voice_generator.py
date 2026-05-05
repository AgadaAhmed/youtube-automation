import asyncio
import edge_tts
from mutagen.mp3 import MP3

VOICE = "en-GB-RyanNeural"

PACE_SETTINGS = {
    "normal":   {"rate": "+0%",   "pitch": "+0Hz"},
    "slow":     {"rate": "-18%",  "pitch": "-4Hz"},
    "fast":     {"rate": "+18%",  "pitch": "+2Hz"},
    "dramatic": {"rate": "-25%",  "pitch": "-8Hz"},
}


async def _speak(text: str, output_path: str, rate: str, pitch: str) -> None:
    communicate = edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch)
    await communicate.save(output_path)


def generate_section_audio(text: str, output_path: str, pace: str = "normal") -> None:
    settings = PACE_SETTINGS.get(pace, PACE_SETTINGS["normal"])
    asyncio.run(_speak(text, output_path, settings["rate"], settings["pitch"]))


def get_audio_duration(audio_path: str) -> float:
    audio = MP3(audio_path)
    return float(audio.info.length)
