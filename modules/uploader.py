from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def upload_video(video_path: str, thumbnail_path: str, script: dict, credentials: dict) -> str:
    creds = Credentials(
        token=None,
        refresh_token=credentials["refresh_token"],
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        token_uri=TOKEN_URI,
        scopes=SCOPES,
    )
    creds.refresh(Request())

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": script["title"],
            "description": script["description"],
            "tags": script["tags"],
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    insert_request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = insert_request.execute()
    video_id = response["id"]

    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path),
    ).execute()

    return video_id
