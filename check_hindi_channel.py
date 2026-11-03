from youtube_uploader import get_authenticated_service

if __name__ == "__main__":
    print("Checking authenticated Hindi YouTube channel details...")
    try:
        service = get_authenticated_service("Hindi")
        channels = service.channels().list(part="snippet,statistics", mine=True).execute()
        for item in channels.get("items", []):
            print(f"\n[SUCCESS] Connected to YouTube Channel:")
            print(f"   -> Channel Title: {item['snippet']['title']}")
            print(f"   -> Channel ID: {item['id']}")
            print(f"   -> Description: {item['snippet'].get('description', 'N/A')}")
    except Exception as e:
        print(f"[Error] Failed to fetch channel details: {e}")
