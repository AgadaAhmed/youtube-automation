import os
from PIL import Image
from modules.video_builder import render_title_slide, render_body_slide, render_outro_slide


def test_render_title_slide_creates_file(tmp_path):
    output = str(tmp_path / "title.png")
    render_title_slide("The Dark Mystery", "History & Mysteries", output)
    assert os.path.exists(output)


def test_render_title_slide_is_1920x1080(tmp_path):
    output = str(tmp_path / "title.png")
    render_title_slide("The Dark Mystery", "History & Mysteries", output)
    img = Image.open(output)
    assert img.size == (1920, 1080)


def test_render_body_slide_creates_file(tmp_path):
    output = str(tmp_path / "body.png")
    render_body_slide("In 1900, something strange was discovered beneath the ice.", 1, 15, output)
    assert os.path.exists(output)


def test_render_body_slide_is_1920x1080(tmp_path):
    output = str(tmp_path / "body.png")
    render_body_slide("In 1900, something strange was discovered beneath the ice.", 1, 15, output)
    img = Image.open(output)
    assert img.size == (1920, 1080)


def test_render_outro_slide_creates_file(tmp_path):
    output = str(tmp_path / "outro.png")
    render_outro_slide("History & Mysteries", output)
    assert os.path.exists(output)


def test_render_body_slide_long_text_does_not_crash(tmp_path):
    output = str(tmp_path / "body_long.png")
    long_text = (
        "This is an extraordinarily long piece of narration text that goes on and on "
        "and should be gracefully word-wrapped by the rendering system without crashing "
        "or overflowing the slide boundaries in any way whatsoever."
    )
    render_body_slide(long_text, 5, 20, output)
    assert os.path.exists(output)
