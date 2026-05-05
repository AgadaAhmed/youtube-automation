import io
import random
import textwrap
import requests as req
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT_PATH = "assets/fonts/Montserrat-Bold.ttf"
W, H = 1280, 720
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (210, 40, 40)
CHANNEL_LABEL = "HISTORY & MYSTERIES"


def _fetch_image(query: str, api_key: str) -> Image.Image:
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
            return ImageOps.fit(img, (W, H), Image.LANCZOS)
    except Exception:
        pass
    return Image.new("RGB", (W, H), (8, 10, 24))


def generate_thumbnail(title: str, output_path: str, topic: str = "", pexels_key: str = "") -> None:
    img = _fetch_image(topic or title, pexels_key)

    # Light vignette — keep photo visible, darken edges
    vignette = Image.new("L", (W, H))
    vd = ImageDraw.Draw(vignette)
    for i in range(120):
        alpha = int(180 * (1 - i / 120))
        vd.rectangle([(i, i), (W - i, H - i)], outline=alpha)
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), mask=vignette)

    # Dark strip at bottom for text legibility (~40% of height)
    strip_y = int(H * 0.52)
    strip = Image.new("RGBA", (W, H - strip_y), (0, 0, 0, 200))
    img.paste(strip.convert("RGB"),
              (0, strip_y),
              mask=strip.split()[3])

    draw = ImageDraw.Draw(img)

    # --- Title text: auto-size to fit ---
    font_size = 100
    while font_size > 40:
        font = ImageFont.truetype(FONT_PATH, font_size)
        char_w = max(12, int(24 * (100 / font_size)))
        wrapped = textwrap.fill(title, width=char_w)
        bbox = draw.textbbox((0, 0), wrapped, font=font)
        text_h = bbox[3] - bbox[1]
        text_w = bbox[2] - bbox[0]
        if text_h < (H - strip_y - 60) and text_w < W - 60:
            break
        font_size -= 6

    text_cx = W // 2
    text_cy = strip_y + (H - strip_y) // 2 - 10

    # Red accent bar above text
    bar_y = text_cy - text_h // 2 - 22
    draw.rectangle([(text_cx - 60, bar_y), (text_cx + 60, bar_y + 6)], fill=ACCENT_COLOR)

    # Shadow
    draw.text(
        (text_cx + 4, text_cy + 4), wrapped,
        font=font, fill=(0, 0, 0), anchor="mm", align="center",
    )
    # Main title
    draw.text(
        (text_cx, text_cy), wrapped,
        font=font, fill=TEXT_COLOR, anchor="mm", align="center",
    )

    # Top accent bar
    draw.rectangle([(0, 0), (W, 7)], fill=ACCENT_COLOR)
    # Bottom accent bar + channel label
    draw.rectangle([(0, H - 36), (W, H)], fill=ACCENT_COLOR)
    label_font = ImageFont.truetype(FONT_PATH, 22)
    draw.text((W // 2, H - 18), CHANNEL_LABEL, font=label_font, fill=TEXT_COLOR, anchor="mm")

    img.save(output_path, quality=95)
