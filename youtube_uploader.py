import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import BASE_DIR

# Scope required for uploading videos, captions, and managing playlists on YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube"]

def get_authenticated_service():
    """Authenticates and returns the YouTube API service client using OAuth2."""
    credentials_file = os.path.join(BASE_DIR, "client_secret.json")
    token_file = os.path.join(BASE_DIR, "token.pickle")
    
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"YouTube API credentials file '{credentials_file}' not found. "
            "Please download your OAuth client_secret.json from Google Cloud Console and place it in the project root."
        )
        
    creds = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"[Warning] Failed to refresh OAuth token: {e}")
                
        if not creds or not creds.valid:
            if os.getenv("CI") or os.environ.get("GITHUB_ACTIONS"):
                raise RuntimeError(
                    "YouTube OAuth credentials expired or invalid in CI environment. "
                    "Please regenerate token.pickle locally and update the YOUTUBE_TOKEN_B64 GitHub secret."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)
            
    return build("youtube", "v3", credentials=creds)

def upload_video_to_youtube(video_path: str, title: str, description: str, tags: list = None, category_id: str = "27", privacy_status: str = "public"):
    """
    Uploads a video file to YouTube automatically using YouTube Data API v3.
    category_id '27' = Education, '28' = Science & Technology
    privacy_status: 'public', 'private', or 'unlisted'
    """
    if not title or not title.strip():
        title = "Incredible Mystery & Science Facts #shorts"
    
    # YouTube video title maximum character limit is 100 characters
    if len(title) > 100:
        print(f"[Warning] Title length is {len(title)} chars (exceeds YouTube 100-char limit). Truncating...")
        title = title[:97] + "..."

    print(f"📤 Uploading '{title}' to YouTube...")
    youtube = get_authenticated_service()
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or ["shorts", "education", "facts", "tech"],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   -> Upload progress: {int(status.progress() * 100)}%")
            
    video_id = response.get("id")
    print(f"[Success] Video successfully uploaded to YouTube! Video ID: {video_id}")
    print(f"   -> Link: https://youtu.be/{video_id}")
    return video_id

def upload_caption(video_id: str, srt_path: str, language_code: str = "en"):
    """
    Uploads an SRT subtitle file to a YouTube video so captions are enabled automatically.
    """
    if not srt_path or not os.path.exists(srt_path):
        return
    print(f"📤 Uploading captions ({language_code}) for video {video_id}...")
    try:
        youtube = get_authenticated_service()
        media = MediaFileUpload(srt_path, mimetype='application/octet-stream')
        body = {
            "snippet": {
                "videoId": video_id,
                "language": language_code,
                "name": "Subtitles",
                "isDraft": False
            }
        }
        youtube.captions().insert(
            part="snippet",
            body=body,
            media_body=media
        ).execute()
        print(f"[Success] Captions uploaded successfully!")
    except Exception as e:
        print(f"[Warning] Could not upload captions track: {e}")

def upload_thumbnail(video_id: str, thumbnail_path: str):
    """
    Uploads a custom thumbnail image to a YouTube video with retry logic and detailed error reporting.
    """
    if not thumbnail_path or not os.path.exists(thumbnail_path):
        print(f"[Warning] Thumbnail path not found: {thumbnail_path}")
        return
    print(f"🖼️ Uploading custom thumbnail for video {video_id}...")
    
    try:
        youtube = get_authenticated_service()
        media = MediaFileUpload(thumbnail_path, mimetype='image/jpeg', resumable=True)
        
        import time
        from googleapiclient.errors import HttpError
        for attempt in range(3):
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=media
                ).execute()
                print(f"[Success] Thumbnail uploaded successfully!")
                return
            except HttpError as he:
                print(f"[Warning] Thumbnail upload HTTP error (attempt {attempt + 1}): {he.resp.status} - {he.content.decode('utf-8', errors='ignore')}")
                if attempt < 2:
                    print("⏳ Waiting 10 seconds before retrying thumbnail upload...")
                    time.sleep(10)
            except Exception as e:
                print(f"[Warning] Thumbnail upload error (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    print("⏳ Waiting 10 seconds before retrying thumbnail upload...")
                    time.sleep(10)
    except Exception as e:
        print(f"[Warning] Could not initialize thumbnail upload: {e}")

def add_video_to_playlist(video_id: str, playlist_id: str):
    """
    Adds a video to a specific YouTube playlist.
    """
    if not playlist_id:
        return
    print(f"📂 Adding video {video_id} to playlist {playlist_id}...")
    try:
        youtube = get_authenticated_service()
        body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
        youtube.playlistItems().insert(
            part="snippet",
            body=body
        ).execute()
        print(f"[Success] Video added to playlist!")
    except Exception as e:
        print(f"[Warning] Could not add video to playlist: {e}")

if __name__ == "__main__":
    print("Testing YouTube Uploader authentication flow...")
    try:
        service = get_authenticated_service()
        print("[Success] YouTube authentication successful! 'token.pickle' has been generated/refreshed.")
    except Exception as e:
        print(f"[Error] Authentication failed: {e}")
