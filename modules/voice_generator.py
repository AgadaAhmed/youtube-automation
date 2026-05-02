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
