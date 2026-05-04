import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FONT_PATH = "assets/fonts/Montserrat-Bold.ttf"
W, H = 1280, 720
TEXT_COLOR = (245, 245, 245)
ACCENT_COLOR = (210, 40, 40)
CHANNEL_LABEL = "HISTORY & MYSTERIES"


def _make_gradient_bg() -> Image.Image:
    """Deep cinematic gradient: dark navy corner to dark crimson."""
    s = 8
    c1, c2 = (4, 6, 24), (22, 4, 10)
    small = Image.new("RGB", (s, s))
    pixels = []
    for y in range(s):
        for x in range(s):
            t = x / (s - 1) * 0.5 + y / (s - 1) * 0.5
            pixels.append(tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    small.putdata(pixels)
    return small.resize((W, H), Image.LANCZOS)


def _add_vignette(img: Image.Image, strength: int = 200) -> Image.Image:
    sw, sh = 240, 135
    vig = Image.new("L", (sw, sh), 0)
    draw = ImageDraw.Draw(vig)
    mx, my = int(sw * 0.10), int(sh * 0.10)
    draw.ellipse([mx, my, sw - mx, sh - my], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(radius=int(sw * 0.20)))
    vig = vig.resize((W, H), Image.LANCZOS)
    inv = ImageChops.invert(vig).point(lambda x: int(x * strength / 255))
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), mask=inv)
    return img


def _add_text_glow(img: Image.Image, xy: tuple, text: str, font, color: tuple, blur: int = 22) -> Image.Image:
    """Draw a blurred colored glow behind text."""
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text(xy, text, font=font, fill=(*color, 180), anchor="mm", align="center")
    glow = glow.filter(ImageFilter.GaussianBlur(blur))
    base = img.convert("RGBA")
    base = Image.alpha_composite(base, glow)
    return base.convert("RGB")


def generate_thumbnail(title: str, output_path: str) -> None:
    img = _make_gradient_bg()
    img = _add_vignette(img)

    # Top and bottom accent bars
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (W, 8)], fill=ACCENT_COLOR)
    draw.rectangle([(0, H - 8), (W, H)], fill=ACCENT_COLOR)

    # Left vertical accent bar
    draw.rectangle([(48, 60), (56, H - 60)], fill=ACCENT_COLOR)

    # Fit title text
    font_size = 110
    while font_size > 40:
        font = ImageFont.truetype(FONT_PATH, font_size)
        char_width = max(10, int(22 * (110 / font_size)))
        wrapped = textwrap.fill(title, width=char_width)
        bbox = draw.textbbox((0, 0), wrapped, font=font)
        if (bbox[3] - bbox[1]) < H - 200:
            break
        font_size -= 6

    text_y = H // 2 - 20

    # Glow pass
    img = _add_text_glow(img, (W // 2, text_y), wrapped, font, ACCENT_COLOR, blur=28)

    # Redraw after glow (glow converts to RGB, need fresh draw)
    draw = ImageDraw.Draw(img)

    # Redraw accent bars (glow may have altered edges slightly)
    draw.rectangle([(0, 0), (W, 8)], fill=ACCENT_COLOR)
    draw.rectangle([(0, H - 8), (W, H)], fill=ACCENT_COLOR)
    draw.rectangle([(48, 60), (56, H - 60)], fill=ACCENT_COLOR)

    # Shadow
    draw.text((W // 2 + 5, text_y + 5), wrapped, font=font, fill=(0, 0, 0), anchor="mm", align="center")
    # Main text
    draw.text((W // 2, text_y), wrapped, font=font, fill=TEXT_COLOR, anchor="mm", align="center")

    # Channel label
    label_font = ImageFont.truetype(FONT_PATH, 30)
    draw.text((W // 2, H - 30), CHANNEL_LABEL, font=label_font, fill=ACCENT_COLOR, anchor="mm")

    img.save(output_path, quality=95)
