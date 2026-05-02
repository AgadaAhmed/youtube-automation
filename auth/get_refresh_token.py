"""
Run this once locally to get your YouTube refresh token.
Usage:
  export YOUTUBE_CLIENT_ID="your-client-id"
  export YOUTUBE_CLIENT_SECRET="your-client-secret"
  python auth/get_refresh_token.py
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ["YOUTUBE_CLIENT_ID"],
        "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }
}

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=0)
    print("\n=== YOUR REFRESH TOKEN ===")
    print(creds.refresh_token)
    print("=========================")
    print("Copy this into GitHub Secrets as YOUTUBE_REFRESH_TOKEN")


if __name__ == "__main__":
    main()
