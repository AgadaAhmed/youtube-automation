import pytest
from unittest.mock import AsyncMock, MagicMock
from modules.voice_generator import generate_section_audio, get_audio_duration


def test_generate_section_audio_calls_edge_tts(mocker, tmp_path):
    output = str(tmp_path / "audio.mp3")
    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock()
    mocker.patch("edge_tts.Communicate", return_value=mock_communicate)

    generate_section_audio("Hello world.", output)

    mock_communicate.save.assert_called_once_with(output)


def test_generate_section_audio_uses_correct_voice(mocker, tmp_path):
    output = str(tmp_path / "audio.mp3")
    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock()
    mock_constructor = mocker.patch("edge_tts.Communicate", return_value=mock_communicate)

    generate_section_audio("Hello world.", output)

    mock_constructor.assert_called_once_with("Hello world.", "en-GB-RyanNeural")


def test_get_audio_duration_returns_float(mocker, tmp_path):
    audio_file = tmp_path / "audio.mp3"
    audio_file.write_bytes(b"fake")
    mock_mp3 = MagicMock()
    mock_mp3.info.length = 18.5
    mocker.patch("mutagen.mp3.MP3", return_value=mock_mp3)
    mocker.patch("modules.voice_generator.MP3", return_value=mock_mp3)

    result = get_audio_duration(str(audio_file))

    assert result == 18.5
    assert isinstance(result, float)
