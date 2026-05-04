import os
import random
import subprocess
import tempfile
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FONT_PATH = "assets/fonts/Montserrat-Bold.ttf"
W, H = 1920, 1080
TEXT_COLOR = (238, 238, 238)
CHANNEL_NAME = "History & Mysteries"
OUTRO_DURATION = 5.0

# Cinematic dark palettes: (bg_dark, bg_light, accent)
PALETTES = [
    ((4, 6, 22),  (20, 4, 18),  (190, 35, 35)),   # navy/dark purple — red
    ((6, 4, 16),  (24, 6, 6),   (210, 85, 15)),    # dark indigo/crimson — orange
    ((4, 16, 24), (6, 6, 16),   (15, 105, 125)),   # dark teal/navy — cyan
    ((12, 7, 4),  (4, 4, 14),   (150, 110, 12)),   # dark amber/navy — gold
    ((6, 4, 18),  (18, 4, 8),   (100, 15, 130)),   # indigo/dark crimson — purple
    ((4, 12, 10), (8, 4, 18),   (20, 130, 80)),    # dark forest/indigo — green
]


def _make_gradient_bg(color1: tuple, color2: tuple) -> Image.Image:
    """Fast diagonal gradient via small image + resize."""
    s = 8
    small = Image.new("RGB", (s, s))
    pixels = []
    for y in range(s):
        for x in range(s):
            t = (x / (s - 1) * 0.55 + y / (s - 1) * 0.45)
            r = int(color1[0] + (color2[0] - color1[0]) * t)
            g = int(color1[1] + (color2[1] - color1[1]) * t)
            b = int(color1[2] + (color2[2] - color1[2]) * t)
            pixels.append((r, g, b))
    small.putdata(pixels)
    return small.resize((W, H), Image.LANCZOS)


def _add_vignette(img: Image.Image, strength: int = 160) -> Image.Image:
    """Dark vignette around edges."""
    sw, sh = 240, 135
    vig = Image.new("L", (sw, sh), 0)
    draw = ImageDraw.Draw(vig)
    mx, my = int(sw * 0.12), int(sh * 0.12)
    draw.ellipse([mx, my, sw - mx, sh - my], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(radius=int(sw * 0.18)))
    vig = vig.resize((W, H), Image.LANCZOS)
    inv = ImageChops.invert(vig).point(lambda x: int(x * strength / 255))
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), mask=inv)
    return img


def _add_grain(img: Image.Image, seed: int = 0, intensity: int = 18) -> Image.Image:
    """Subtle film grain overlay."""
    rng = random.Random(seed)
    tile = 256
    data = [rng.randint(0, intensity) for _ in range(tile * tile)]
    noise_tile = Image.new("L", (tile, tile))
    noise_tile.putdata(data)
    tx = (W + tile - 1) // tile
    ty = (H + tile - 1) // tile
    tiled = Image.new("L", (tx * tile, ty * tile))
    for row in range(ty):
        for col in range(tx):
            tiled.paste(noise_tile, (col * tile, row * tile))
    noise = tiled.crop((0, 0, W, H)).convert("RGB")
    return ImageChops.add(img, noise)


def _draw_shadowed(draw: ImageDraw.Draw, xy: tuple, text: str, font, fill: tuple, offset: int = 4) -> None:
    x, y = xy
    draw.text((x + offset, y + offset), text, font=font, fill=(0, 0, 0), anchor="mm", align="center")
    draw.text((x, y), text, font=font, fill=fill, anchor="mm", align="center")


def _make_base_image(palette_idx: int = 0) -> Image.Image:
    p = PALETTES[palette_idx % len(PALETTES)]
    img = _make_gradient_bg(p[0], p[1])
    img = _add_vignette(img)
    img = _add_grain(img, seed=palette_idx)
    return img, p[2]  # return image and accent color


def render_title_slide(title: str, channel_name: str, output_path: str) -> None:
    img, accent = _make_base_image(0)
    draw = ImageDraw.Draw(img)

    # Accent bars
    draw.rectangle([(0, 0), (W, 5)], fill=accent)
    draw.rectangle([(0, H - 5), (W, H)], fill=accent)

    # Thin horizontal divider lines
    draw.rectangle([(W // 2 - 200, H // 2 - 130), (W // 2 + 200, H // 2 - 126)], fill=accent)
    draw.rectangle([(W // 2 - 200, H // 2 + 90), (W // 2 + 200, H // 2 + 94)], fill=accent)

    font_title = ImageFont.truetype(FONT_PATH, 96)
    font_channel = ImageFont.truetype(FONT_PATH, 36)

    wrapped = textwrap.fill(title, width=26)
    _draw_shadowed(draw, (W // 2, H // 2 - 20), wrapped, font_title, TEXT_COLOR, offset=5)
    _draw_shadowed(draw, (W // 2, H - 90), channel_name.upper(), font_channel, accent, offset=3)

    img.save(output_path)


def render_body_slide(text: str, slide_number: int, total_slides: int, output_path: str) -> None:
    palette_idx = (slide_number % len(PALETTES))
    img, accent = _make_base_image(palette_idx)
    draw = ImageDraw.Draw(img)

    # Accent bars
    draw.rectangle([(0, 0), (W, 5)], fill=accent)
    draw.rectangle([(0, H - 5), (W, H)], fill=accent)

    # Left accent bar
    draw.rectangle([(60, 100), (66, H - 100)], fill=accent)

    font_body = ImageFont.truetype(FONT_PATH, 60)
    wrapped = textwrap.fill(text, width=38)
    _draw_shadowed(draw, (W // 2 + 20, H // 2), wrapped, font_body, TEXT_COLOR, offset=4)

    # Progress bar
    bar_x1 = int(W * 0.15)
    bar_x2 = int(W * 0.85)
    bar_y = H - 38
    draw.rectangle([(bar_x1, bar_y - 3), (bar_x2, bar_y + 3)], fill=(60, 60, 80))
    prog_x = bar_x1 + int((bar_x2 - bar_x1) * slide_number / total_slides)
    draw.rectangle([(bar_x1, bar_y - 3), (prog_x, bar_y + 3)], fill=accent)

    img.save(output_path)


def render_outro_slide(channel_name: str, output_path: str) -> None:
    img, accent = _make_base_image(1)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (W, 5)], fill=accent)
    draw.rectangle([(0, H - 5), (W, H)], fill=accent)

    # Bell icon substitute — decorative ring
    cx, cy = W // 2, H // 2 - 60
    r = 55
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=accent, width=6)
    draw.ellipse([(cx - 8, cy - 8), (cx + 8, cy + 8)], fill=accent)

    font_main = ImageFont.truetype(FONT_PATH, 72)
    font_sub = ImageFont.truetype(FONT_PATH, 46)
    font_channel = ImageFont.truetype(FONT_PATH, 34)

    _draw_shadowed(draw, (W // 2, H // 2 + 40), "SUBSCRIBE", font_main, TEXT_COLOR, offset=5)
    _draw_shadowed(draw, (W // 2, H // 2 + 120), "for more history & mysteries", font_sub, accent, offset=3)
    _draw_shadowed(draw, (W // 2, H - 70), channel_name.upper(), font_channel, (160, 160, 180), offset=2)

    img.save(output_path)


def _create_silence_mp3(output_path: str, duration: float = OUTRO_DURATION) -> None:
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
    segments = []

    title_slide = os.path.join(tmp_dir, "slide_title.png")
    render_title_slide(script["title"], CHANNEL_NAME, title_slide)
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
    render_outro_slide(CHANNEL_NAME, outro_slide)
    outro_audio = os.path.join(tmp_dir, "outro_silence.mp3")
    _create_silence_mp3(outro_audio, duration=OUTRO_DURATION)
    seg_outro = os.path.join(tmp_dir, "seg_outro.mp4")
    _image_to_video_segment(outro_slide, outro_audio, seg_outro)
    segments.append(seg_outro)

    _concat_segments(segments, output_path)
