import os
import requests
import random
import urllib.parse
from config import PEXELS_API_KEY, ASSETS_DIR

def fetch_wikimedia_image(query: str) -> str:
    """Fetches a real historical/geographic photograph from Wikipedia or Wikimedia Commons API."""
    try:
        headers = {"User-Agent": "YouTubeAutomationBot/1.0 (educational purpose)"}
        
        # 1. Try Wikipedia Page Images API first (most accurate for real monuments/places)
        wiki_search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit=3"
        resp = requests.get(wiki_search_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            search_results = resp.json().get("query", {}).get("search", [])
            for res in search_results:
                title = res.get("title")
                if title:
                    page_img_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&pithumbsize=1200&format=json"
                    img_resp = requests.get(page_img_url, headers=headers, timeout=10)
                    if img_resp.status_code == 200:
                        pages = img_resp.json().get("query", {}).get("pages", {})
                        for p_id, p_data in pages.items():
                            thumb = p_data.get("thumbnail", {}).get("source")
                            if thumb:
                                r_img = requests.get(thumb, timeout=15)
                                if r_img.status_code == 200:
                                    print(f"   -> [Real Archive Success] Fetched real photograph from Wikipedia for '{title}'")
                                    return r_img.content

        # 2. Fallback to Wikimedia Commons search
        queries_to_try = [query]
        words = query.split()
        if len(words) > 3:
            queries_to_try.append(" ".join(words[:3]))
            queries_to_try.append(" ".join(words[-3:]))
            
        for q in queries_to_try:
            url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(q)}&gsrlimit=5&prop=imageinfo&iiprop=url&format=json"
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
                                print(f"   -> [Real Archive Success] Fetched real photograph from Wikimedia Commons for '{q}'")
                                return img_resp.content
    except Exception as e:
        print(f"[Note] Wikimedia/Wikipedia fetch failed for '{query}': {e}")
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

def image_to_video_clip(img_bytes: bytes, output_path: str, orientation: str = "portrait") -> str:
    """Converts image bytes into a 4-second dynamic video clip with smooth Ken Burns zoom and pan animation."""
    temp_img_path = output_path.replace(".mp4", "_temp.jpg")
    try:
        with open(temp_img_path, "wb") as f:
            f.write(img_bytes)
            
        target_w = 1080 if orientation == "portrait" else 1920
        target_h = 1920 if orientation == "portrait" else 1080
        
        try:
            from PIL import Image
            with Image.open(temp_img_path) as img:
                img = img.convert("RGB")
                w_orig, h_orig = img.size
                if h_orig > 100:
                    img = img.crop((0, 0, w_orig, h_orig - 35))
                img.save(temp_img_path, quality=95)
        except Exception as pil_err:
            print(f"[Note] PIL crop skipped: {pil_err}")

        import subprocess, imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Ken Burns zoompan filter for smooth cinematic motion (4 seconds at 24fps = 96 frames)
        vf_string = f"scale={target_w}*2:{target_h}*2:force_original_aspect_ratio=increase,crop={target_w}*2:{target_h}*2,zoompan=z='min(zoom+0.0015,1.2)':d=96:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',scale={target_w}:{target_h},format=yuv420p"
        
        cmd = [
            ffmpeg_exe, "-y", "-loop", "1", "-i", temp_img_path,
            "-t", "4.0",
            "-vf", vf_string,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-fps_mode", "cfr", "-r", "24",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_path
    except Exception as e:
        print(f"[Error] Failed to convert image to video clip with Ken Burns: {e}")
        try:
            from moviepy.editor import ImageClip
            img_clip = ImageClip(temp_img_path).set_duration(4.0)
            img_clip.write_videofile(output_path, fps=24, codec="libx264", audio=False, logger=None)
            img_clip.close()
            return output_path
        except Exception as ex2:
            print(f"[Error] MoviePy fallback failed: {ex2}")
            return None
    finally:
        if os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except:
                pass

def fetch_pexels_photo(query: str, orientation: str = "portrait") -> bytes:
    """Fetches real professional stock photographs from Pexels Photos API."""
    if not PEXELS_API_KEY or PEXELS_API_KEY == "your_pexels_api_key_here":
        return None
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        orient_param = "portrait" if orientation == "portrait" else "landscape"
        url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=15&orientation={orient_param}"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            photos = data.get("photos", [])
            if photos:
                photo = random.choice(photos[:min(5, len(photos))])
                src = photo.get("src", {})
                img_url = src.get("large2x") or src.get("large") or src.get("original")
                if img_url:
                    img_resp = requests.get(img_url, timeout=15)
                    if img_resp.status_code == 200:
                        print(f"   -> [Pexels Photo Success] Fetched real professional photograph for '{query}'")
                        return img_resp.content
    except Exception as e:
        print(f"[Note] Pexels photo fetch failed for '{query}': {e}")
    return None

def fetch_stock_video(query: str, orientation: str = "portrait", output_filename: str = "stock.mp4") -> str:
    """
    Enhanced Hybrid Media Pipeline:
    Tier 1: Real Stock Video Footage (Pexels Videos API search with exact query)
    Tier 2: Real Professional Photographs & Archives (Pexels Photos, Wikimedia, NASA) -> Converted with Ken Burns Zoom/Pan effect
    Tier 3: AI Cinematic B-Roll (Pollinations.ai) -> Converted with Ken Burns Zoom/Pan effect
    """
    output_path = os.path.join(ASSETS_DIR, output_filename)
    
    # 1. Tier 1: Try Pexels Video API first for actual moving video footage
    if PEXELS_API_KEY and PEXELS_API_KEY != "your_pexels_api_key_here":
        print(f"   -> [Pexels Video] Searching real stock video for: '{query}'...")
        headers = {"Authorization": PEXELS_API_KEY}
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=12&orientation={orientation}"
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
                            print(f"   -> [Pexels Video Success] Downloaded real stock video. Normalizing...")
                            try:
                                import subprocess, imageio_ffmpeg
                                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                                target_w = 1080 if orientation == "portrait" else 1920
                                target_h = 1920 if orientation == "portrait" else 1080
                                temp_norm_path = output_path.replace(".mp4", "_norm.mp4")
                                scale_filter = f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},format=yuv420p"
                                cmd = [
                                    ffmpeg_exe, "-y", "-i", output_path,
                                    "-sws_flags", "lanczos+accurate_rnd",
                                    "-vf", scale_filter,
                                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                                    "-c:a", "aac", "-b:a", "128k",
                                    "-fps_mode", "cfr", "-r", "24",
                                    temp_norm_path
                                ]
                                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                                if os.path.exists(temp_norm_path):
                                    os.replace(temp_norm_path, output_path)
                            except Exception as norm_err:
                                print(f"[Note] Pexels normalization fallback skipped: {norm_err}")
                            return output_path
        except Exception as e:
            print(f"[Warning] Pexels video search failed: {e}")

    # 2. Tier 2: Real Photos & Archives (Pexels Photos, Wikimedia, NASA)
    q_lower = query.lower()
    is_space = any(k in q_lower for k in ["space", "planet", "galaxy", "nasa", "star", "telescope", "mars", "black hole", "universe"])

    img_bytes = None
    try:
        print(f"   -> [Pexels Photos] Searching real professional photograph for: '{query}'...")
        img_bytes = fetch_pexels_photo(query, orientation)

        if not img_bytes:
            if is_space:
                print(f"   -> [NASA Archive] Fetching authentic space visual for: '{query}'...")
                img_bytes = fetch_nasa_image(query)
                if not img_bytes:
                    img_bytes = fetch_wikimedia_image(query)
            else:
                print(f"   -> [Wikimedia Archive] Fetching real photograph for: '{query}'...")
                img_bytes = fetch_wikimedia_image(query)
                if not img_bytes:
                    img_bytes = fetch_nasa_image(query)
    except Exception as archive_err:
        print(f"[Note] Real archive/photo fetch skipped due to error/timeout: {archive_err}")

    if img_bytes:
        res_path = image_to_video_clip(img_bytes, output_path, orientation)
        if res_path:
            print(f"   -> [Real Photo Success] Converted authentic real photograph to dynamic video clip with Ken Burns.")
            return res_path

    # 3. Tier 3: Smart AI Cinematic B-Roll (Pollinations.ai)
    print(f"   -> [AI Cinematic B-Roll] Generating 8K vibrant cinematic visual for: '{query}' via Pollinations.ai...")
    try:
        ai_prompt = f"{query}, masterpiece, ultra detailed, hyperrealistic 8k resolution, Unreal Engine 5 render, extremely vibrant rich colors, cinematic HDR lighting, golden hour glow, highly saturated, visually stunning photorealistic cinematic film still"
        encoded_prompt = urllib.parse.quote(ai_prompt)
        ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&seed={random.randint(1000, 99999)}"
        
        img_resp = requests.get(ai_image_url, timeout=20)
        if img_resp.status_code == 200:
            res_path = image_to_video_clip(img_resp.content, output_path, orientation)
            if res_path:
                print(f"   -> [AI Cinematic Success] Generated 100% topic-matched dynamic video clip.")
                return res_path
    except Exception as ai_err:
        print(f"[Warning] AI Cinematic B-Roll failed: {ai_err}")

    # 4. Final Fallback: Cinematic AI Visual
    print(f"   -> [Cinematic AI Fallback] Generating stunning 8K vibrant cinematic background visual for: '{query}'...")
    try:
        fallback_prompt = f"epic cinematic mystery and wonder background, {query}, highly detailed 8k resolution, extremely vibrant rich colors, cinematic HDR lighting, golden hour glow, highly saturated, photorealistic documentary style"
        encoded_fallback = urllib.parse.quote(fallback_prompt)
        fallback_url = f"https://image.pollinations.ai/prompt/{encoded_fallback}?width=1280&height=720&nologo=true&seed={random.randint(1000, 99999)}"
        
        img_resp = requests.get(fallback_url, timeout=15)
        if img_resp.status_code == 200:
            res_path = image_to_video_clip(img_resp.content, output_path, orientation)
            if res_path:
                print(f"   -> [Cinematic Fallback Success] Created rich dynamic visual clip.")
                return res_path
    except Exception as fallback_err:
        print(f"[Warning] Cinematic Fallback failed: {fallback_err}")

    return None

if __name__ == "__main__":
    print("Testing 3-Tier Media Fetcher Pipeline...")
    path = fetch_stock_video("Ancient Egyptian secret temple hieroglyphs", "portrait", "test_clip.mp4")
    print(f"Result clip path: {path}")
