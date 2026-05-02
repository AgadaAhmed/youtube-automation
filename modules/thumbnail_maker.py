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

    draw.rectangle([(0, 0), (W, 10)], fill=ACCENT_COLOR)
    draw.rectangle([(0, H - 10), (W, H)], fill=ACCENT_COLOR)
    draw.rectangle([(60, 80), (68, H - 80)], fill=ACCENT_COLOR)

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

    label_font = ImageFont.truetype(FONT_PATH, 32)
    draw.text(
        (W // 2, H - 50),
        CHANNEL_LABEL,
        font=label_font,
        fill=ACCENT_COLOR,
        anchor="mm",
    )

    img.save(output_path, quality=95)
