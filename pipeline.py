"""
Main pipeline orchestrator.
Run: python pipeline.py
Env vars required: GROQ_API_KEY, PEXELS_API_KEY, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN
"""
import os
import shutil
import tempfile

from modules.topic_picker import pick_next_topic, mark_topic_used
from modules.script_writer import generate_script, generate_short_script
from modules.voice_generator import generate_section_audio
from modules.video_builder import build_video, build_short_video
from modules.thumbnail_maker import generate_thumbnail
from modules.uploader import upload_video, upload_short

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
        script = generate_script(topic, os.environ["GROQ_API_KEY"])
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
        pexels_key = os.environ.get("PEXELS_API_KEY", "")
        video_path = os.path.join(tmp_dir, "output.mp4")
        build_video(script, audio_files, tmp_dir, video_path, pexels_key=pexels_key)
        print(f"      Video: {video_path}")

        print("[5/6] Generating thumbnail...")
        thumbnail_path = os.path.join(tmp_dir, "thumbnail.jpg")
        generate_thumbnail(script["title"], thumbnail_path, topic=topic, pexels_key=pexels_key)

        print("[6/6] Uploading to YouTube...")
        credentials = _get_credentials()
        video_id = upload_video(video_path, thumbnail_path, script, credentials)
        print(f"      Uploaded: https://youtube.com/watch?v={video_id}")

        print("      Generating Short script...")
        short_script = generate_short_script(topic, os.environ["GROQ_API_KEY"])
        print(f"      Short sections: {len(short_script['sections'])}")

        print("      Building Short video...")
        short_path = os.path.join(tmp_dir, "short.mp4")
        build_short_video(short_script, tmp_dir, short_path, pexels_key=pexels_key)

        short_id = upload_short(short_path, script, credentials)
        print(f"      Short: https://youtube.com/shorts/{short_id}")

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
