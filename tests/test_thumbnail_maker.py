import os
from PIL import Image
from modules.thumbnail_maker import generate_thumbnail


def test_generate_thumbnail_creates_file(tmp_path):
    output = str(tmp_path / "thumb.jpg")
    generate_thumbnail("The Mystery of Atlantis", output)
    assert os.path.exists(output)


def test_generate_thumbnail_correct_dimensions(tmp_path):
    output = str(tmp_path / "thumb.jpg")
    generate_thumbnail("The Mystery of Atlantis", output)
    img = Image.open(output)
    assert img.size == (1280, 720)


def test_generate_thumbnail_is_rgb(tmp_path):
    output = str(tmp_path / "thumb.jpg")
    generate_thumbnail("Short Title", output)
    img = Image.open(output)
    assert img.mode == "RGB"


def test_generate_thumbnail_long_title_does_not_crash(tmp_path):
    output = str(tmp_path / "thumb.jpg")
    long_title = "The Extraordinary and Completely Baffling Disappearance of the Eilean Mor Lighthouse Keepers"
    generate_thumbnail(long_title, output)
    assert os.path.exists(output)
