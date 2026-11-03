import pickle
import os
import base64
import json
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

        # Extract Email from id_token inside token_hindi.pickle
        token_file = "/root/youtube-automation/token_hindi.pickle"
        if not os.path.exists(token_file):
            token_file = "token_hindi.pickle"
            
        if os.path.exists(token_file):
            with open(token_file, "rb") as token:
                creds = pickle.load(token)
                if hasattr(creds, 'id_token') and creds.id_token:
                    try:
                        parts = creds.id_token.split('.')
                        if len(parts) > 1:
                            payload_b64 = parts[1] + '=='
                            payload_json = base64.urlsafe_b64decode(payload_b64).decode('utf-8')
                            payload = json.loads(payload_json)
                            email = payload.get('email')
                            if email:
                                print(f"   -> Associated Gmail Address: {email}")
                            else:
                                print("   -> Email not found in id_token payload.")
                    except Exception as jwt_err:
                        print(f"   -> Could not decode id_token: {jwt_err}")
                else:
                    print("   -> id_token not present in credentials.")
    except Exception as e:
        print(f"[Error] Failed to fetch channel details: {e}")
