import requests
from youtube_uploader import get_authenticated_service

if __name__ == "__main__":
    print("Checking authenticated Hindi YouTube channel and Gmail details...")
    try:
        service = get_authenticated_service("Hindi")
        
        # Get channel details
        channels = service.channels().list(part="snippet,statistics", mine=True).execute()
        for item in channels.get("items", []):
            print(f"\n[SUCCESS] Connected to YouTube Channel:")
            print(f"   -> Channel Title: {item['snippet']['title']}")
            print(f"   -> Channel ID: {item['id']}")

        # Get Google Account Email using token
        import pickle
        import os
        token_file = "/root/youtube-automation/token_hindi.pickle"
        if not os.path.exists(token_file):
            token_file = "token_hindi.pickle"
            
        if os.path.exists(token_file):
            with open(token_file, "rb") as token:
                creds = pickle.load(token)
                if creds and creds.token:
                    headers = {"Authorization": f"Bearer {creds.token}"}
                    resp = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
                    if resp.status_code == 200:
                        email = resp.json().get("email")
                        print(f"   -> Associated Gmail Address: {email}")
                    else:
                        print("   -> Could not fetch associated Gmail address from token.")
    except Exception as e:
        print(f"[Error] Failed to fetch channel details: {e}")
