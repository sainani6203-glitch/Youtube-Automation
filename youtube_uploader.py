import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import BASE_DIR

# Scope required for uploading videos to YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

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
            creds.refresh(Request())
        else:
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

if __name__ == "__main__":
    print("Testing YouTube Uploader setup...")
    print("Place your 'client_secret.json' in C:\\Ai project to enable auto-upload.")
