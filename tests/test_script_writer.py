import json
import pytest
from modules.script_writer import generate_script

SAMPLE_SCRIPT = {
    "title": "The Test Mystery",
    "description": "A gripping tale of the unknown.",
    "tags": ["mystery", "history", "unsolved"],
    "sections": [
        {"text": "In the year 1900, something strange happened.", "duration": 15},
        {"text": "Nobody could explain what they found.", "duration": 18},
    ],
}


def test_generate_script_returns_valid_structure(mocker):
    mock_response = mocker.MagicMock()
    mock_response.text = json.dumps(SAMPLE_SCRIPT)
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("modules.script_writer.genai.Client", return_value=mock_client)

    result = generate_script("Test Topic", "fake-api-key")

    assert result["title"] == "The Test Mystery"
    assert isinstance(result["sections"], list)
    assert len(result["sections"]) == 2
    assert all("text" in s for s in result["sections"])
    assert all("duration" in s for s in result["sections"])


def test_generate_script_strips_markdown_code_block(mocker):
    mock_response = mocker.MagicMock()
    mock_response.text = f"```json\n{json.dumps(SAMPLE_SCRIPT)}\n```"
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("modules.script_writer.genai.Client", return_value=mock_client)

    result = generate_script("Test Topic", "fake-api-key")
    assert result["title"] == "The Test Mystery"


def test_generate_script_uses_gemini_flash(mocker):
    mock_response = mocker.MagicMock()
    mock_response.text = json.dumps(SAMPLE_SCRIPT)
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("modules.script_writer.genai.Client", return_value=mock_client)

    generate_script("Test Topic", "fake-api-key")

    mock_client.models.generate_content.assert_called_once()
    call_kwargs = mock_client.models.generate_content.call_args
    assert call_kwargs[1]["model"] == "gemini-2.0-flash"
