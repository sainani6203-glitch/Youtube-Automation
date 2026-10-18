import os
import requests
import random
import urllib.parse
from config import PEXELS_API_KEY, ASSETS_DIR

def fetch_stock_video(query: str, orientation: str = "portrait", output_filename: str = "stock.mp4") -> str:
    """
    Fetches a stock video clip from Pexels API based on query.
    If Pexels fails or has no video, automatically falls back to generating
    a 100% topic-matched cinematic AI image via Pollinations.ai and converting it to an MP4 video clip.
    """
    output_path = os.path.join(ASSETS_DIR, output_filename)
    
    # 1. Try Pexels API First
    if PEXELS_API_KEY and PEXELS_API_KEY != "your_pexels_api_key_here":
        headers = {"Authorization": PEXELS_API_KEY}
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=15&orientation={orientation}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                videos = data.get("videos", [])
                if videos:
                    chosen_video = random.choice(videos[:min(10, len(videos))])
                    video_files = chosen_video.get("video_files", [])
                    mp4_files = [f for f in video_files if f.get("file_type") == "video/mp4"]
                    if mp4_files:
                        best_file = max(mp4_files, key=lambda x: x.get("width", 0))
                        download_url = best_file.get("link")
                        
                        vid_response = requests.get(download_url, stream=True, timeout=15)
                        if vid_response.status_code == 200:
                            with open(output_path, "wb") as f:
                                for chunk in vid_response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            print(f"   -> [Pexels Success] Downloaded stock video for: '{query}'")
                            return output_path
        except Exception as e:
            print(f"[Warning] Pexels fetch failed for '{query}': {e}")

    # 2. Fallback: Generate 100% Topic-Matched Cinematic AI Image & Convert to MP4 Clip via Pollinations.ai
    print(f"   -> [AI Fallback] Generating cinematic AI background for: '{query}' via Pollinations.ai...")
    try:
        ai_prompt = f"{query}, masterpiece, ultra detailed, hyperrealistic 8k resolution, Unreal Engine 5 render, dramatic cinematic moody lighting, movie poster style"
        encoded_prompt = urllib.parse.quote(ai_prompt)
        ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&seed={random.randint(1000, 99999)}"
        
        img_resp = requests.get(ai_image_url, timeout=20)
        if img_resp.status_code == 200:
            temp_img_path = output_path.replace(".mp4", ".jpg")
            with open(temp_img_path, "wb") as f:
                f.write(img_resp.content)
            
            # Convert image to 4-second MP4 video clip using MoviePy
            try:
                from moviepy import ImageClip
                clip_duration = 4.0
                try:
                    img_clip = ImageClip(temp_img_path).with_duration(clip_duration)
                except AttributeError:
                    img_clip = ImageClip(temp_img_path).set_duration(clip_duration)
                
                img_clip.write_videofile(output_path, fps=24, codec="libx264", audio=False, logger=None)
                img_clip.close()
                
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
                    
                print(f"   -> [AI Fallback Success] Generated AI video clip for: '{query}'")
                return output_path
            except Exception as cvt_err:
                print(f"[Error converting AI image to video clip] {cvt_err}")
    except Exception as ai_err:
        print(f"[Error in AI Fallback] {ai_err}")

    return None

if __name__ == "__main__":
    print("Testing Media Fetcher with AI Fallback...")
    path = fetch_stock_video("Ancient Indian lost temple secret treasure", "portrait", "test_clip.mp4")
    print(f"Result clip path: {path}")
