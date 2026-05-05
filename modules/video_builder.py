import io
import os
import random
import subprocess
import tempfile
import textwrap
import requests as req
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT_PATH = "assets/fonts/Montserrat-Bold.ttf"
W, H = 1920, 1080
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (210, 40, 40)
CHANNEL_NAME = "History & Mysteries"
OUTRO_DURATION = 5.0

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
    'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been', 'have',
    'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'that', 'this', 'it', 'its', 'they', 'their', 'there', 'what', 'which',
    'who', 'how', 'when', 'where', 'not', 'no', 'so', 'if', 'as', 'into',
    'just', 'only', 'than', 'then', 'about', 'after', 'before', 'over', 'had',
}


def _extract_keywords(text: str, n: int = 3) -> str:
    import re
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    keywords = [w for w in words if len(w) > 4 and w.lower() not in STOP_WORDS]
    return ' '.join(keywords[:n]) or text[:30]


def _fetch_image(query: str, api_key: str, width: int, height: int) -> Image.Image:
    """Fetch a relevant photo from Pexels. Falls back to dark bg on any failure."""
    try:
        headers = {"Authorization": api_key}
        r = req.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params={"query": query, "per_page": 10, "orientation": "landscape"},
            timeout=10,
        )
        photos = r.json().get("photos", [])
        if photos:
            photo = random.choice(photos[:5])
            img_bytes = req.get(photo["src"]["original"], timeout=30).content
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            return ImageOps.fit(img, (width, height), Image.LANCZOS)
    except Exception:
        pass
    return Image.new("RGB", (width, height), (8, 10, 24))


def _dark_overlay(img: Image.Image, opacity: int) -> Image.Image:
    """Uniform dark overlay so text stays readable."""
    img.paste(Image.new("RGB", img.size, (0, 0, 0)), mask=Image.new("L", img.size, opacity))
    return img


def _gradient_overlay(img: Image.Image) -> Image.Image:
    """Gradient overlay: lighter at top, darker at bottom where text sits."""
    w, h = img.size
    grad = Image.new("L", (1, h))
    for y in range(h):
        grad.putpixel((0, y), int(50 + 160 * (y / h)))
    grad = grad.resize((w, h), Image.LANCZOS)
    img.paste(Image.new("RGB", (w, h), (0, 0, 0)), mask=grad)
    return img


def _shadow_text(draw, xy, text, font, fill, offset=4):
    x, y = xy
    draw.text((x + offset, y + offset), text, font=font, fill=(0, 0, 0), anchor="mm", align="center")
    draw.text((x, y), text, font=font, fill=fill, anchor="mm", align="center")


def render_title_slide(title: str, channel_name: str, output_path: str,
                       topic: str = "", pexels_key: str = "") -> None:
    img = _fetch_image(topic or title, pexels_key, W, H)
    img = _dark_overlay(img, opacity=145)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (W, 5)], fill=ACCENT_COLOR)
    draw.rectangle([(0, H - 5), (W, H)], fill=ACCENT_COLOR)
    draw.rectangle([(W//2 - 230, H//2 - 145), (W//2 + 230, H//2 - 141)], fill=ACCENT_COLOR)
    draw.rectangle([(W//2 - 230, H//2 + 105), (W//2 + 230, H//2 + 109)], fill=ACCENT_COLOR)

    font_title = ImageFont.truetype(FONT_PATH, 96)
    font_channel = ImageFont.truetype(FONT_PATH, 36)

    wrapped = textwrap.fill(title, width=26)
    _shadow_text(draw, (W // 2, H // 2 - 20), wrapped, font_title, TEXT_COLOR, offset=5)
    _shadow_text(draw, (W // 2, H - 80), channel_name.upper(), font_channel, ACCENT_COLOR, offset=3)

    img.save(output_path)


def render_body_slide(text: str, slide_number: int, total_slides: int,
                      output_path: str, pexels_key: str = "") -> None:
    query = _extract_keywords(text, n=3)
    img = _fetch_image(query, pexels_key, W, H)
    img = _gradient_overlay(img)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (W, 5)], fill=ACCENT_COLOR)
    draw.rectangle([(0, H - 5), (W, H)], fill=ACCENT_COLOR)

    font_body = ImageFont.truetype(FONT_PATH, 60)
    wrapped = textwrap.fill(text, width=38)
    _shadow_text(draw, (W // 2, H // 2), wrapped, font_body, TEXT_COLOR, offset=4)

    bar_x1, bar_x2 = int(W * 0.15), int(W * 0.85)
    bar_y = H - 38
    draw.rectangle([(bar_x1, bar_y - 3), (bar_x2, bar_y + 3)], fill=(60, 60, 80))
    prog_x = bar_x1 + int((bar_x2 - bar_x1) * slide_number / total_slides)
    draw.rectangle([(bar_x1, bar_y - 3), (prog_x, bar_y + 3)], fill=ACCENT_COLOR)

    img.save(output_path)


def render_outro_slide(channel_name: str, output_path: str, pexels_key: str = "") -> None:
    img = _fetch_image("epic landscape scenery", pexels_key, W, H)
    img = _dark_overlay(img, opacity=155)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (W, 5)], fill=ACCENT_COLOR)
    draw.rectangle([(0, H - 5), (W, H)], fill=ACCENT_COLOR)

    cx, cy = W // 2, H // 2 - 60
    draw.ellipse([(cx - 55, cy - 55), (cx + 55, cy + 55)], outline=ACCENT_COLOR, width=6)
    draw.ellipse([(cx - 8, cy - 8), (cx + 8, cy + 8)], fill=ACCENT_COLOR)

    font_main = ImageFont.truetype(FONT_PATH, 72)
    font_sub = ImageFont.truetype(FONT_PATH, 46)
    font_channel = ImageFont.truetype(FONT_PATH, 34)

    _shadow_text(draw, (W // 2, H // 2 + 40), "SUBSCRIBE", font_main, TEXT_COLOR, offset=5)
    _shadow_text(draw, (W // 2, H // 2 + 120), "for more history & mysteries", font_sub, ACCENT_COLOR, offset=3)
    _shadow_text(draw, (W // 2, H - 70), channel_name.upper(), font_channel, (200, 200, 220), offset=2)

    img.save(output_path)


def _image_to_video_segment(slide_path: str, audio_path: str, output_path: str) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-i", slide_path, "-i", audio_path,
         "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-r", "24",
         "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
         "-pix_fmt", "yuv420p", "-shortest", output_path],
        check=True, capture_output=True,
    )


def _render_outro_segment(slide_path: str, output_path: str, duration: float = OUTRO_DURATION) -> None:
    subprocess.run(
        ["ffmpeg", "-y",
         "-t", str(duration), "-loop", "1", "-i", slide_path,
         "-f", "lavfi", "-t", str(duration), "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-r", "24",
         "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
         "-pix_fmt", "yuv420p", "-shortest",
         output_path],
        check=True, capture_output=True,
    )


def _concat_segments(segment_paths: list, output_path: str) -> None:
    concat_list = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    try:
        for seg in segment_paths:
            concat_list.write(f"file '{os.path.abspath(seg)}'\n")
        concat_list.close()
        # Re-encode during concat to fix timestamp issues (especially outro duration)
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list.name,
             "-c:v", "libx264", "-crf", "18", "-preset", "fast",
             "-c:a", "aac", "-b:a", "192k",
             "-pix_fmt", "yuv420p",
             output_path],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(concat_list.name)


def create_short(main_video_path: str, output_path: str, duration: int = 58) -> None:
    """Crop main video to 9:16 vertical and trim to 58s for YouTube Shorts."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", main_video_path,
         "-vf", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920",
         "-t", str(duration),
         "-c:v", "libx264", "-crf", "18", "-preset", "fast",
         "-c:a", "aac", "-b:a", "192k",
         "-pix_fmt", "yuv420p",
         output_path],
        check=True, capture_output=True,
    )


def build_video(script: dict, audio_files: list, tmp_dir: str, output_path: str,
                pexels_key: str = "") -> None:
    sections = script["sections"]
    topic = script.get("title", "")
    segments = []

    title_slide = os.path.join(tmp_dir, "slide_title.png")
    render_title_slide(script["title"], CHANNEL_NAME, title_slide, topic=topic, pexels_key=pexels_key)
    seg_title = os.path.join(tmp_dir, "seg_title.mp4")
    _image_to_video_segment(title_slide, audio_files[0], seg_title)
    segments.append(seg_title)

    total_body = len(sections) - 1
    for i, section in enumerate(sections[1:], start=1):
        slide_path = os.path.join(tmp_dir, f"slide_{i:02d}.png")
        render_body_slide(section["text"], i, total_body, slide_path, pexels_key=pexels_key)
        seg_path = os.path.join(tmp_dir, f"seg_{i:02d}.mp4")
        _image_to_video_segment(slide_path, audio_files[i], seg_path)
        segments.append(seg_path)

    outro_slide = os.path.join(tmp_dir, "slide_outro.png")
    render_outro_slide(CHANNEL_NAME, outro_slide, pexels_key=pexels_key)
    seg_outro = os.path.join(tmp_dir, "seg_outro.mp4")
    _render_outro_segment(outro_slide, seg_outro, duration=OUTRO_DURATION)
    segments.append(seg_outro)

    _concat_segments(segments, output_path)
