import sys
from youtube_uploader import get_authenticated_service

if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "Telugu"
    print(f"🔑 Starting authentication for language channel: {lang}")
    try:
        service = get_authenticated_service(language=lang)
        print(f"✅ Success! Authentication token for '{lang}' generated successfully.")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
