import os
import requests
import random
import urllib.parse
from config import PEXELS_API_KEY, ASSETS_DIR

def fetch_wikimedia_image(query: str) -> str:
    """Fetches a real historical/geographic image from Wikimedia Commons API."""
    try:
        url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit=5&prop=imageinfo&iiprop=url&format=json"
        headers = {"User-Agent": "YouTubeAutomationBot/1.0 (educational purpose)"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                imageinfo = page_data.get("imageinfo", [])
                if imageinfo:
                    img_url = imageinfo[0].get("url")
                    if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        img_resp = requests.get(img_url, timeout=15)
                        if img_resp.status_code == 200:
                            return img_resp.content
    except Exception as e:
        print(f"[Note] Wikimedia fetch failed for '{query}': {e}")
    return None

def fetch_nasa_image(query: str) -> str:
    """Fetches real space/astronomy image from NASA Image and Video Library API."""
    try:
        url = f"https://images-api.nasa.gov/search?q={urllib.parse.quote(query)}&media_type=image"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("collection", {}).get("items", [])
            if items:
                item = random.choice(items[:min(5, len(items))])
                links = item.get("links", [])
                if links:
                    img_url = links[0].get("href")
                    if img_url:
                        img_resp = requests.get(img_url, timeout=15)
                        if img_resp.status_code == 200:
                            return img_resp.content
    except Exception as e:
        print(f"[Note] NASA fetch failed for '{query}': {e}")
    return None

def image_to_video_clip(img_bytes: bytes, output_path: str) -> str:
    """Converts image bytes into a 4-second dynamic video clip with Ken Burns zoom effect using MoviePy."""
    temp_img_path = output_path.replace(".mp4", "_temp.jpg")
    try:
        with open(temp_img_path, "wb") as f:
            f.write(img_bytes)
            
        from moviepy import ImageClip
        clip_duration = 4.0
        try:
            img_clip = ImageClip(temp_img_path).with_duration(clip_duration)
        except AttributeError:
            img_clip = ImageClip(temp_img_path).set_duration(clip_duration)
            
        # Apply smooth cinematic zoom-in (Ken Burns effect)
        try:
            img_clip = img_clip.resized(lambda t: 1.0 + 0.05 * t)
        except Exception:
            try:
                img_clip = img_clip.resize(lambda t: 1.0 + 0.05 * t)
            except Exception:
                pass
                
        img_clip.write_videofile(output_path, fps=24, codec="libx264", audio=False, logger=None)
        img_clip.close()
        return output_path
    except Exception as e:
        print(f"[Error] Failed to convert image to video clip: {e}")
        return None
    finally:
        if os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except:
                pass

def fetch_stock_video(query: str, orientation: str = "portrait", output_filename: str = "stock.mp4") -> str:
    """
    3-Tier Hybrid Media Pipeline:
    Tier 1: Smart AI Cinematic B-Roll (Pollinations.ai) with Ken Burns zoom-in effect.
    Tier 2: Real Historical/Space Archives (Wikimedia Commons & NASA APIs) for authentic topics.
    Tier 3: Ambient Cinematic Motion Backgrounds (Pexels) as fallback.
    """
    output_path = os.path.join(ASSETS_DIR, output_filename)
    
    q_lower = query.lower()
    is_space = any(k in q_lower for k in ["space", "planet", "galaxy", "nasa", "star", "telescope", "mars", "black hole", "universe"])
    is_history = any(k in q_lower for k in ["ancient", "temple", "egypt", "pyramid", "history", "rome", "artifact", "ruins", "civilization"])

    # 1. Tier 2: Real Archives (NASA for space, Wikimedia for history/geography)
    img_bytes = None
    if is_space:
        print(f"   -> [NASA Archive] Fetching authentic space visual for: '{query}'...")
        img_bytes = fetch_nasa_image(query)
    elif is_history or len(query) > 10:
        print(f"   -> [Wikimedia Archive] Fetching authentic historical visual for: '{query}'...")
        img_bytes = fetch_wikimedia_image(query)
        if not img_bytes and is_space:
            img_bytes = fetch_nasa_image(query)

    if img_bytes:
        res_path = image_to_video_clip(img_bytes, output_path)
        if res_path:
            print(f"   -> [Archive Success] Converted authentic archive image to cinematic video clip.")
            return res_path

    # 2. Tier 1: Smart AI Cinematic B-Roll (Pollinations.ai)
    print(f"   -> [AI Cinematic B-Roll] Generating 8K cinematic visual for: '{query}' via Pollinations.ai...")
    try:
        ai_prompt = f"{query}, masterpiece, ultra detailed, hyperrealistic 8k resolution, Unreal Engine 5 render, dramatic cinematic moody lighting, documentary film still"
        encoded_prompt = urllib.parse.quote(ai_prompt)
        ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&seed={random.randint(1000, 99999)}"
        
        img_resp = requests.get(ai_image_url, timeout=20)
        if img_resp.status_code == 200:
            res_path = image_to_video_clip(img_resp.content, output_path)
            if res_path:
                print(f"   -> [AI Cinematic Success] Generated 100% topic-matched video clip.")
                return res_path
    except Exception as ai_err:
        print(f"[Warning] AI Cinematic B-Roll failed: {ai_err}")

    # 3. Tier 3: Ambient Motion Backgrounds (Pexels API fallback)
    if PEXELS_API_KEY and PEXELS_API_KEY != "your_pexels_api_key_here":
        print(f"   -> [Pexels Fallback] Searching ambient stock video for: '{query}'...")
        headers = {"Authorization": PEXELS_API_KEY}
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote('cinematic ambient background ' + query)}&per_page=10&orientation={orientation}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                videos = data.get("videos", [])
                if videos:
                    chosen_video = random.choice(videos[:min(5, len(videos))])
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
                            print(f"   -> [Pexels Success] Downloaded ambient stock video.")
                            return output_path
        except Exception as e:
            print(f"[Warning] Pexels fallback failed: {e}")

    return None

if __name__ == "__main__":
    print("Testing 3-Tier Media Fetcher Pipeline...")
    path = fetch_stock_video("Ancient Egyptian secret temple hieroglyphs", "portrait", "test_clip.mp4")
    print(f"Result clip path: {path}")
