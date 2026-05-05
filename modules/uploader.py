from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _build_youtube(credentials: dict):
    creds = Credentials(
        token=None,
        refresh_token=credentials["refresh_token"],
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        token_uri=TOKEN_URI,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, thumbnail_path: str, script: dict, credentials: dict) -> str:
    youtube = _build_youtube(credentials)

    top_tags = script["tags"][:5]
    hashtags = " ".join(f"#{t.replace(' ', '')}" for t in top_tags)
    description = f"{script['description']}\n\n{hashtags}"

    body = {
        "snippet": {
            "title": script["title"],
            "description": description,
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

    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path),
        ).execute()
    except Exception as e:
        print(f"      Warning: thumbnail upload skipped ({e})")

    return video_id


def upload_short(short_path: str, script: dict, credentials: dict) -> str:
    youtube = _build_youtube(credentials)

    short_title = f"{script['title']} #Shorts"[:100]
    top_tags = script["tags"][:5]
    hashtags = " ".join(f"#{t.replace(' ', '')}" for t in top_tags)
    description = f"{script['description']}\n\n{hashtags}\n\n#Shorts\n\nFollow for more dark history."

    body = {
        "snippet": {
            "title": short_title,
            "description": description,
            "tags": script["tags"] + ["shorts", "youtubeshorts"],
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(short_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    insert_request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = insert_request.execute()
    return response["id"]
