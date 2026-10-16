import os
import requests
import html
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
from config import READY_TO_REVIEW_DIR, PEXELS_API_KEY

def render_single_text(text: str, font_size: int = 56, color: tuple = (255, 255, 255)) -> Image.Image:
    """Renders a single unified mixed Telugu + English text with heavy outline and zero background box."""
    # Replace common emojis with text/symbols and filter out unsupported non-rendering unicode symbols
    text = text.replace("🔥", "!!").replace("🚨", "!!").replace("😱", "!!").replace("🚀", "!!")
    text = ''.join(c for c in text if ord(c) < 128 or ('\u0C00' <= c <= '\u0C7F') or ('\u0900' <= c <= '\u097F') or c in ' !?,.-_!#')
    text = text.strip()

    font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'Nirmala.ttc')
    if not os.path.exists(font_path):
        font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'nirmala.ttc')

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy_img)

    # Word wrap text nicely
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > 1050:
            current_line.pop()
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    line_heights = []
    max_w = 0
    for line in lines:
        bbox = dummy_draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_w = max(max_w, w)
        line_heights.append(h)

    total_h = sum(line_heights) + (len(lines) - 1) * 15 + 40
    txt_img = Image.new("RGBA", (max_w + 60, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_img)

    def draw_outlined_text(xy, text_str, font, fill_color):
        x, y = xy
        # Clean 8-point offset for crisp outline without heavy black box
        offsets = [
            (-3, -3), (-3, 0), (-3, 3),
            (0, -3),           (0, 3),
            (3, -3),  (3, 0),  (3, 3)
        ]
        for dx, dy in offsets:
            draw.text((x + dx, y + dy), text_str, font=font, fill=(0, 0, 0, 255))
        draw.text((x, y), text_str, font=font, fill=(fill_color[0], fill_color[1], fill_color[2], 255))

    current_y = 20
    for idx, line in enumerate(lines):
        draw_outlined_text((20, current_y), line, font, color)
        current_y += line_heights[idx] + 15

    return txt_img

def generate_thumbnail(title: str, category: str = "", output_path: str = None) -> str:
    """
    Generates a high-CTR cinematic YouTube thumbnail with floating bold Telugu text and zero background boxes.
    """
    if not output_path:
        output_path = os.path.join(READY_TO_REVIEW_DIR, "thumbnail.jpg")
        
    width, height = 1280, 720
    base_image = None

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
        print(f"📥 Detected YouTube video ID/URL: '{yt_video_id}'. Fetching official YouTube thumbnail and video title...")
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

        for res_quality in ["maxresdefault.jpg", "sddefault.jpg", "hqdefault.jpg"]:
            yt_thumb_url = f"https://img.youtube.com/vi/{yt_video_id}/{res_quality}"
            try:
                resp = requests.get(yt_thumb_url)
                if resp.status_code == 200 and len(resp.content) > 5000:
                    base_image = Image.open(BytesIO(resp.content)).convert("RGB")
                    print(f"[Success] Official YouTube thumbnail loaded as base image.")
                    break
            except Exception as e:
                print(f"[Note] Failed fetching {res_quality}: {e}")

    # Determine mixed-words sentence for thumbnail
    clean_title = title.replace("#shorts", "").replace("#Shorts", "").strip()
    if "|" in clean_title:
        parts = clean_title.split("|")
        thumbnail_text = f"{parts[0].strip()} {parts[1].strip()} 🔥"
    else:
        thumbnail_text = clean_title

    # Determine Dynamic Vibrant Text Color (Rotates daily / per video for fresh variety)
    vibrant_colors = [
        (255, 59, 48),    # Electric Red
        (0, 229, 255),    # Neon Cyan
        (255, 215, 0),    # Electric Gold
        (255, 0, 127),    # Hot Magenta
        (57, 255, 20),    # Lime Green
        (255, 102, 0),    # Neon Orange
        (191, 0, 255),    # Electric Purple
        (255, 204, 0)     # Bright Yellow
    ]
    
    import random
    import time
    random.seed(int(time.time() * 1000) ^ abs(hash(title)))
    text_color = random.choice(vibrant_colors)

    # Extract clean English keywords for stock photo search query
    search_query = clean_title
    if "|" in title:
        parts = title.split("|")
        if len(parts) > 1:
            search_query = parts[1].strip().split("#")[0].strip()

    print(f"🔍 Thumbnail Search Query: '{search_query}'")
    print(f"🏷️ Category: '{category}' -> Mixed Thumbnail Text: '{thumbnail_text}'")

    # 1. Fetch Stock Photo from Pexels if base image not already loaded
    if not base_image and PEXELS_API_KEY and PEXELS_API_KEY != "your_pexels_api_key_here":
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/v1/search?query={search_query} cinematic moody dark mysterious shock 4k&per_page=15&orientation=landscape"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                if photos:
                    chosen_photo = random.choice(photos[:min(5, len(photos))])
                    img_url = chosen_photo.get("src", {}).get("large2x") or chosen_photo.get("src", {}).get("large")
                    if img_url:
                        img_resp = requests.get(img_url, stream=True)
                        if img_resp.status_code == 200:
                            base_image = Image.open(BytesIO(img_resp.content)).convert("RGB")
        except Exception as e:
            print(f"[Warning] Pexels fetch failed: {e}")

    if not base_image:
        base_image = Image.new("RGB", (width, height), color=(15, 23, 42))
        
    # 2. Cover-Fit Resize & Crop
    img_ratio = base_image.width / base_image.height
    target_ratio = width / height
    if img_ratio > target_ratio:
        new_h = height
        new_w = int(height * img_ratio)
        base_image = base_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        base_image = base_image.crop((left, 0, left + width, height))
    else:
        new_w = width
        new_h = int(width / img_ratio)
        base_image = base_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        top = (new_h - height) // 2
        base_image = base_image.crop((0, top, width, top + height))

    # 3. Cinematic Color Grading (Rich contrast without dark overlay)
    base_image = ImageEnhance.Contrast(base_image).enhance(1.40)
    base_image = ImageEnhance.Color(base_image).enhance(1.25)
    base_image = base_image.convert("RGBA")

    # 4. Render Floating Mixed-Text directly onto the image (Zero background box)
    x_start = 80
    y_start = 220

    txt_img = render_single_text(thumbnail_text, font_size=56, color=text_color)
    max_w = 1120
    if txt_img.width > max_w:
        ratio = max_w / txt_img.width
        txt_img = txt_img.resize((max_w, int(txt_img.height * ratio)), Image.Resampling.LANCZOS)

    base_image.paste(txt_img, (x_start, y_start), txt_img)

    base_image.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"[Success] Bilingual floating-text cinematic thumbnail generated at: {output_path}")
    return output_path

if __name__ == "__main__":
    url = "https://youtu.be/NtJC6Np1_aY"
    out_path = os.path.join(READY_TO_REVIEW_DIR, "thumbnail.jpg")
    generate_thumbnail("भारत के Pyramids के अंदर छुपा hidden underground city रहस्य", "Ancient Mysteries", out_path)
    print(f"Authentic Devanagari Hindi thumbnail generated at: {out_path}")
