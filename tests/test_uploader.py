import pytest
from modules.uploader import upload_video

FAKE_CREDS = {
    "client_id": "fake-client-id",
    "client_secret": "fake-secret",
    "refresh_token": "fake-refresh-token",
}

SAMPLE_SCRIPT = {
    "title": "The Dark Secret of the Lighthouse",
    "description": "A gripping tale of three missing men.",
    "tags": ["mystery", "history"],
    "sections": [],
}


def test_upload_video_returns_video_id(mocker, tmp_path):
    video_file = tmp_path / "video.mp4"
    video_file.write_bytes(b"fake video content")
    thumb_file = tmp_path / "thumb.jpg"
    thumb_file.write_bytes(b"fake thumb content")

    mock_creds = mocker.MagicMock()
    mocker.patch("modules.uploader.Credentials", return_value=mock_creds)
    mocker.patch("modules.uploader.Request")

    mock_youtube = mocker.MagicMock()
    mock_insert = mocker.MagicMock()
    mock_insert.execute.return_value = {"id": "abc123XYZ"}
    mock_youtube.videos.return_value.insert.return_value = mock_insert
    mock_youtube.thumbnails.return_value.set.return_value.execute.return_value = {}
    mocker.patch("modules.uploader.build", return_value=mock_youtube)

    video_id = upload_video(str(video_file), str(thumb_file), SAMPLE_SCRIPT, FAKE_CREDS)
    assert video_id == "abc123XYZ"


def test_upload_video_sets_category_education(mocker, tmp_path):
    video_file = tmp_path / "video.mp4"
    video_file.write_bytes(b"fake")
    thumb_file = tmp_path / "thumb.jpg"
    thumb_file.write_bytes(b"fake")

    mock_creds = mocker.MagicMock()
    mocker.patch("modules.uploader.Credentials", return_value=mock_creds)
    mocker.patch("modules.uploader.Request")

    mock_youtube = mocker.MagicMock()
    mock_insert = mocker.MagicMock()
    mock_insert.execute.return_value = {"id": "xyz"}
    mock_youtube.videos.return_value.insert.return_value = mock_insert
    mock_youtube.thumbnails.return_value.set.return_value.execute.return_value = {}
    mocker.patch("modules.uploader.build", return_value=mock_youtube)

    upload_video(str(video_file), str(thumb_file), SAMPLE_SCRIPT, FAKE_CREDS)

    call_kwargs = mock_youtube.videos.return_value.insert.call_args[1]
    assert call_kwargs["body"]["snippet"]["categoryId"] == "27"
