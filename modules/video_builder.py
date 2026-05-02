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
    wrapped = textwrap.fill(text, width=42)
    draw.text((W // 2, H // 2), wrapped, font=font_body, fill=TEXT_COLOR, anchor="mm", align="center")
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
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-t", str(duration), "-codec:a", "libmp3lame", "-q:a", "9", output_path],
        check=True, capture_output=True,
    )


def _image_to_video_segment(slide_path: str, audio_path: str, output_path: str) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-i", slide_path, "-i", audio_path,
         "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
         "-pix_fmt", "yuv420p", "-shortest", output_path],
        check=True, capture_output=True,
    )


def _concat_segments(segment_paths: list, output_path: str) -> None:
    concat_list = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    try:
        for seg in segment_paths:
            concat_list.write(f"file '{os.path.abspath(seg)}'\n")
        concat_list.close()
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list.name, "-c", "copy", output_path],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(concat_list.name)


def build_video(script: dict, audio_files: list, tmp_dir: str, output_path: str) -> None:
    sections = script["sections"]
    channel_name = "History & Mysteries"
    segments = []

    title_slide = os.path.join(tmp_dir, "slide_title.png")
    render_title_slide(script["title"], channel_name, title_slide)
    seg_title = os.path.join(tmp_dir, "seg_title.mp4")
    _image_to_video_segment(title_slide, audio_files[0], seg_title)
    segments.append(seg_title)

    total_body = len(sections) - 1
    for i, section in enumerate(sections[1:], start=1):
        slide_path = os.path.join(tmp_dir, f"slide_{i:02d}.png")
        render_body_slide(section["text"], i, total_body, slide_path)
        seg_path = os.path.join(tmp_dir, f"seg_{i:02d}.mp4")
        _image_to_video_segment(slide_path, audio_files[i], seg_path)
        segments.append(seg_path)

    outro_slide = os.path.join(tmp_dir, "slide_outro.png")
    render_outro_slide(channel_name, outro_slide)
    outro_audio = os.path.join(tmp_dir, "outro_silence.mp3")
    _create_silence_mp3(outro_audio, duration=3.0)
    seg_outro = os.path.join(tmp_dir, "seg_outro.mp4")
    _image_to_video_segment(outro_slide, outro_audio, seg_outro)
    segments.append(seg_outro)

    _concat_segments(segments, output_path)
