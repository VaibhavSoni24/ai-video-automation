"""
Step 8 — Upload to YouTube using the YouTube Data API v3.
Handles OAuth2 authentication and resumable uploads.
"""

import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "token.json"

VIDEO_PATH = os.path.join("assets", "video", "final_subtitled.mp4")
THUMBNAIL_PATH = os.path.join("assets", "video", "thumbnail.jpg")


def _ensure_client_secrets():
    """Create client_secrets.json from .env variables if it doesn't exist."""
    if os.path.exists(CLIENT_SECRETS_FILE):
        return

    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError(
            "YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET must be set in .env "
            "or provide a client_secrets.json file."
        )

    secrets = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    with open(CLIENT_SECRETS_FILE, "w") as f:
        json.dump(secrets, f, indent=2)
    print(f"[Upload] Created {CLIENT_SECRETS_FILE} from .env credentials.")


def _get_authenticated_service():
    """Authenticate with YouTube API, caching credentials in token.json."""
    _ensure_client_secrets()

    credentials = None

    # Load cached token
    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh or get new credentials
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            credentials = flow.run_local_server(port=8080)

        # Save for next run
        with open(TOKEN_FILE, "w") as f:
            f.write(credentials.to_json())
        print("[Upload] Credentials saved.")

    return build("youtube", "v3", credentials=credentials)


def upload_video(
    video_path: str = VIDEO_PATH,
    title: str = "AI Generated Video",
    description: str = "",
    tags: list[str] = None,
    category_id: str = "22",  # People & Blogs
    privacy: str = "private",
    thumbnail_path: str = THUMBNAIL_PATH,
) -> str:
    """
    Upload video to YouTube with metadata.
    Returns the video ID on success.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    youtube = _get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path,
        chunksize=256 * 1024,  # 256 KB chunks
        resumable=True,
        mimetype="video/mp4",
    )

    print(f"[Upload] Uploading '{title}' to YouTube ({privacy})...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[Upload] Progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"[Upload] ✓ Video uploaded: https://youtube.com/watch?v={video_id}")

    # Set thumbnail if available
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
            ).execute()
            print(f"[Upload] ✓ Thumbnail set.")
        except Exception as e:
            print(f"[Upload] Thumbnail upload failed (may need verified account): {e}")

    return video_id


if __name__ == "__main__":
    vid = upload_video()
    print(f"Done! Video ID: {vid}")
