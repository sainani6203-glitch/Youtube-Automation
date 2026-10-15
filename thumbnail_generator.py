import os
import requests
import html
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
from config import READY_TO_REVIEW_DIR, PEXELS_API_KEY

def render_telugu_text(text: str, font_size: int = 72, color: tuple = (255, 255, 255)) -> Image.Image:
    """Legacy wrapper for single text rendering."""
    return render_bilingual_text(text, "", font_size, color)

def render_bilingual_text(telugu_text: str, english_text: str, font_size: int = 60, color: tuple = (255, 255, 255)) -> Image.Image:
    """Renders high-CTR 2-line bilingual (Telugu + English) text with heavy outline and zero background box."""
    font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'Nirmala.ttc')
    if not os.path.exists(font_path):
        font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'nirmala.ttc')
        
    try:
        font_te = ImageFont.truetype(font_path, font_size)
        font_en = ImageFont.truetype(font_path, int(font_size * 0.80))
    except Exception:
        font_te = ImageFont.load_default()
        font_en = ImageFont.load_default()

    dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy_img)
    
    bbox_te = dummy_draw.textbbox((0, 0), telugu_text, font=font_te)
    w_te = bbox_te[2] - bbox_te[0]
    h_te = bbox_te[3] - bbox_te[1]
    
    if english_text:
        bbox_en = dummy_draw.textbbox((0, 0), english_text, font=font_en)
        w_en = bbox_en[2] - bbox_en[0]
        h_en = bbox_en[3] - bbox_en[1]
    else:
        w_en, h_en = 0, 0

    max_w = max(w_te, w_en) + 60
    total_h = h_te + (h_en + 15 if english_text else 0) + 40

    txt_img = Image.new("RGBA", (max_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_img)

    def draw_outlined_text(xy, text, font, fill_color):
        outline_width = 5
        x, y = xy
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))
        draw.text((x, y), text, font=font, fill=(fill_color[0], fill_color[1], fill_color[2], 255))

    draw_outlined_text((20, 20), telugu_text, font_te, color)
    if english_text:
        draw_outlined_text((20, 20 + h_te + 15), english_text, font_en, (255, 255, 255))

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

    # Determine High-CTR Category Color & Topic-Specific Bilingual Hook
    telugu_text = ""
    english_text = "SECRET REVEALED! 🚨"
    if "|" in title:
        parts = title.split("|")
        left_part = parts[0].strip()
        if any('\u0C00' <= c <= '\u0C7F' for c in left_part):
            telugu_text = left_part
        if len(parts) > 1:
            right_part = parts[1].strip().split("#")[0].strip()
            if len(right_part) <= 30:
                english_text = right_part.upper()

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
    
    # Pick dynamic color based on title hash or day of month
    import datetime
    color_seed = abs(hash(title)) if title else datetime.datetime.now().day
    text_color = vibrant_colors[color_seed % len(vibrant_colors)]

    # Extract clean English keywords for stock photo search query
    search_query = title
    if "|" in title:
        parts = title.split("|")
        if len(parts) > 1:
            search_query = parts[1].strip().split("#")[0].strip()

    print(f"🔍 Thumbnail Search Query: '{search_query}'")
    print(f"🏷️ Category: '{category}' -> Bilingual Hook: '{telugu_text}' | '{english_text}'")

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

    # 4. Render Floating Bilingual Hook directly onto the image (Zero background box)
    x_start = 80
    y_start = 220
    
    txt_img = render_bilingual_text(telugu_text, english_text, font_size=64, color=text_color)
    max_w = 1120
    if txt_img.width > max_w:
        ratio = max_w / txt_img.width
        txt_img = txt_img.resize((max_w, int(txt_img.height * ratio)), Image.Resampling.LANCZOS)

    base_image.paste(txt_img, (x_start, y_start), txt_img)

    base_image.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"[Success] Clean floating-text cinematic thumbnail generated at: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_thumbnail("Mysterious Ancient Secrets of India", "Ancient Indian Mysteries")
