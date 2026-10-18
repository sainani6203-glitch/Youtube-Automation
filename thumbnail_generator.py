import os
import requests
import html
import random
import time
from playwright.sync_api import sync_playwright
from config import READY_TO_REVIEW_DIR, PEXELS_API_KEY

def generate_thumbnail(title: str, category: str = "", output_path: str = None) -> str:
    """
    Generates a high-CTR cinematic YouTube thumbnail with perfect native Telugu/Hindi text shaping using Playwright and HTML/CSS.
    """
    if not output_path:
        output_path = os.path.join(READY_TO_REVIEW_DIR, "thumbnail.jpg")
        
    width, height = 1280, 720

    # Check if title is a YouTube URL or Video ID
    yt_video_id = None
    if "youtu.be/" in title:
        yt_video_id = title.split("youtu.be/")[-1].split("?")[0].strip()
    elif "youtube.com/watch" in title and "v=" in title:
        import urllib.parse
        parsed_url = urllib.parse.urlparse(title)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if "v" in query_params:
            yt_video_id = query_params["v"][0]
    elif len(title) == 11 and ("http" not in title and " " not in title):
        yt_video_id = title

    if yt_video_id:
        print(f"📥 Detected YouTube video ID/URL: '{yt_video_id}'. Fetching official YouTube video title...")
        try:
            watch_url = f"https://www.youtube.com/watch?v={yt_video_id}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            w_resp = requests.get(watch_url, headers=headers, timeout=5)
            if w_resp.status_code == 200:
                import re
                match = re.search(r'<title>(.*?)</title>', w_resp.text)
                if match:
                    raw_title = html.unescape(match.group(1))
                    if raw_title.endswith(" - YouTube"):
                        raw_title = raw_title[:-10]
                    title = raw_title.strip()
                    print(f"   -> Fetched YouTube Video Title: '{title}'")
        except Exception as e:
            print(f"[Warning] Could not fetch video title from YouTube: {e}")

    # Determine full meaningful Telugu/Hindi title for the thumbnail
    clean_title = title.replace("#shorts", "").replace("#Shorts", "").strip()
    if "|" in clean_title:
        parts = clean_title.split("|")
        thumbnail_text = parts[0].strip()
    else:
        thumbnail_text = clean_title

    if thumbnail_text.endswith("..."):
        thumbnail_text = thumbnail_text[:-3].strip()
    thumbnail_text = f"{thumbnail_text} 😱"

    # Extract English search query for Pexels background image
    search_query = clean_title
    if "|" in title:
        parts = title.split("|")
        if len(parts) > 1:
            search_query = parts[1].strip().split("#")[0].strip()

    print(f"🔍 Thumbnail Search Query: '{search_query}'")
    print(f"🏷️ Category: '{category}' -> Thumbnail Text: '{thumbnail_text}'")

    # 1. Fetch Cinematic Stock Photo from Pexels
    bg_image_url = None
    if PEXELS_API_KEY and PEXELS_API_KEY != "your_pexels_api_key_here":
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/v1/search?query={search_query} cinematic moody dark mysterious shock 4k&per_page=15&orientation=landscape"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                if photos:
                    chosen_photo = random.choice(photos[:min(5, len(photos))])
                    bg_image_url = chosen_photo.get("src", {}).get("large2x") or chosen_photo.get("src", {}).get("large")
        except Exception as e:
            print(f"[Warning] Pexels fetch failed: {e}")

    # 2. Determine Dynamic Vibrant Text Color
    vibrant_colors = [
        "#ff3b30", # Electric Red
        "#00e5ff", # Neon Cyan
        "#ffd700", # Electric Gold
        "#ff007f", # Hot Magenta
        "#39ff14", # Lime Green
        "#ff6600", # Neon Orange
        "#bf00ff", # Electric Purple
        "#ffcc00"  # Bright Yellow
    ]
    
    random.seed(int(time.time() * 1000) ^ abs(hash(title)))
    text_color = random.choice(vibrant_colors)

    background_css = f"url('{bg_image_url}') center/cover no-repeat" if bg_image_url else "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"

    # 3. Render High-Resolution Thumbnail using Playwright (Chromium OpenType Harfbuzz shaping for Telugu/Hindi)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@700;900&family=Noto+Sans+Devanagari:wght@700;900&display=swap" rel="stylesheet">
    <style>
      body {{
        margin: 0;
        width: 1280px;
        height: 720px;
        background: {background_css};
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: 'Noto Sans Telugu', 'Noto Sans Devanagari', sans-serif;
      }}
      .overlay {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.45);
      }}
      .title {{
        position: relative;
        z-index: 10;
        font-size: 56px;
        font-weight: 900;
        color: {text_color};
        text-align: center;
        padding: 50px 80px;
        text-shadow: 3px 3px 0px #000, -3px -3px 0px #000, 3px -3px 0px #000, -3px 3px 0px #000, 0px 8px 24px rgba(0,0,0,0.9);
        line-height: 1.35;
        max-width: 1100px;
      }}
    </style>
    </head>
    <body>
      <div class="overlay"></div>
      <div class="title">{thumbnail_text}</div>
    </body>
    </html>
    """

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        page.set_content(html_content)
        page.screenshot(path=output_path, type='jpeg', quality=95)
        browser.close()

    print(f"[Success] Perfect native Unicode shaped thumbnail generated at: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    title_arg = sys.argv[1] if len(sys.argv) > 1 else "भारत के Pyramids के अंदर छुपा hidden underground city रहस्य"
    out_path = os.path.join(READY_TO_REVIEW_DIR, "thumbnail.jpg")
    generate_thumbnail(title_arg, "Mysteries", out_path)
    print(f"Authentic thumbnail generated at: {out_path}")
