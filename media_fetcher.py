import os
import requests
from config import PEXELS_API_KEY, ASSETS_DIR

def fetch_stock_video(query: str, orientation: str = "portrait", output_filename: str = "stock.mp4") -> str:
    """
    Fetches a stock video clip from Pexels API based on keyword query.
    orientation: 'portrait' (for Shorts 9:16) or 'landscape' (for Long 16:9)
    """
    output_path = os.path.join(ASSETS_DIR, output_filename)
    
    if not PEXELS_API_KEY or PEXELS_API_KEY == "your_pexels_api_key_here":
        print("[Warning] PEXELS_API_KEY not configured. Creating a fallback solid color/gradient clip.")
        return None

    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation={orientation}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            videos = data.get("videos", [])
            if videos:
                # Get video file with best HD resolution
                video_files = videos[0].get("video_files", [])
                # Filter for MP4 and sort by width
                mp4_files = [f for f in video_files if f.get("file_type") == "video/mp4"]
                if mp4_files:
                    best_file = max(mp4_files, key=lambda x: x.get("width", 0))
                    download_url = best_file.get("link")
                    
                    # Download video
                    vid_response = requests.get(download_url, stream=True)
                    if vid_response.status_code == 200:
                        with open(output_path, "wb") as f:
                            for chunk in vid_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        return output_path
    except Exception as e:
        print(f"[Error fetching stock video] {e}")
        
    return None

if __name__ == "__main__":
    print("Testing Media Fetcher...")
    path = fetch_stock_video("cyber security", "portrait", "test_clip.mp4")
    print(f"Downloaded video to: {path}")
