import io
import random
import textwrap
import requests as req
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps

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


def _add_glow(img: Image.Image, xy: tuple, text: str, font, color: tuple) -> Image.Image:
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text(xy, text, font=font, fill=(*color, 160), anchor="mm", align="center")
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, glow).convert("RGB")


def generate_thumbnail(title: str, output_path: str, topic: str = "", pexels_key: str = "") -> None:
    img = _fetch_image(topic or title, pexels_key)

    # Dark gradient overlay: heavier at bottom for text area
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(80 + 140 * (y / H)))
    grad = grad.resize((W, H), Image.LANCZOS)
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), mask=grad)

    # Fit title
    font_size = 110
    draw = ImageDraw.Draw(img)
    while font_size > 40:
        font = ImageFont.truetype(FONT_PATH, font_size)
        char_w = max(10, int(22 * (110 / font_size)))
        wrapped = textwrap.fill(title, width=char_w)
        bbox = draw.textbbox((0, 0), wrapped, font=font)
        if (bbox[3] - bbox[1]) < H - 180:
            break
        font_size -= 6

    text_y = H // 2 - 20

    # Glow pass
    img = _add_glow(img, (W // 2, text_y), wrapped, font, ACCENT_COLOR)
    draw = ImageDraw.Draw(img)

    # Accent bars
    draw.rectangle([(0, 0), (W, 7)], fill=ACCENT_COLOR)
    draw.rectangle([(0, H - 7), (W, H)], fill=ACCENT_COLOR)
    draw.rectangle([(46, 55), (53, H - 55)], fill=ACCENT_COLOR)

    # Text shadow + main
    draw.text((W // 2 + 5, text_y + 5), wrapped, font=font, fill=(0, 0, 0), anchor="mm", align="center")
    draw.text((W // 2, text_y), wrapped, font=font, fill=TEXT_COLOR, anchor="mm", align="center")

    # Channel label
    label_font = ImageFont.truetype(FONT_PATH, 30)
    draw.text((W // 2, H - 28), CHANNEL_LABEL, font=label_font, fill=ACCENT_COLOR, anchor="mm")

    img.save(output_path, quality=95)
