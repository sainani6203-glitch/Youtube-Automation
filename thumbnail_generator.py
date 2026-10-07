import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from config import READY_TO_REVIEW_DIR, PEXELS_API_KEY

def generate_thumbnail(title: str, category: str = "", output_path: str = None) -> str:
    """
    Generates or downloads a high-CTR 1280x720 YouTube cinematic thumbnail.
    If title is a YouTube URL or video ID, fetches the official YouTube thumbnail directly.
    Otherwise, generates a cinematic Pexels stock photo thumbnail with high-visibility text.
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
        # Direct video ID
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
                    raw_title = match.group(1)
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
                    print(f"[Success] Official YouTube thumbnail loaded as base image for enhancement.")
                    break
            except Exception as e:
                print(f"[Note] Failed fetching {res_quality}: {e}")

    # Determine Category-based Color Palette
    # Default: Gold/Yellow
    primary_color = (255, 235, 59) 
    
    if "Dark Psychology" in category:
        primary_color = (239, 68, 68)   # Intense Red
    elif "Ancient Indian" in category:
        primary_color = (251, 191, 36)  # Ancient Gold
    elif "Incredible Science" in category:
        primary_color = (56, 189, 248)  # Electric Blue

    # Extract English keywords or generate powerful punchy hook
    search_query = title
    display_text = "SECRET REVEALED"
    
    if "|" in title:
        parts = title.split("|")
        if len(parts) > 1:
            eng_part = parts[1].strip().split("#")[0].strip()
            search_query = eng_part
            words = [w for w in eng_part.upper().split() if all(ord(c) < 128 for c in w)]
            if words:
                display_text = " ".join(words[:4])
    else:
        english_words = [w for w in title.upper().split() if all(ord(c) < 128 for c in w)]
        if len(english_words) >= 2:
            display_text = " ".join(english_words[:4])
            
    if not display_text or len(display_text) < 3:
        if "Dark Psychology" in category:
            display_text = "DARK SECRET"
        elif "Ancient Indian" in category:
            display_text = "ANCIENT MYSTERY"
        elif "Incredible Science" in category:
            display_text = "MIND BLOWING"
        else:
            display_text = "UNTOLD TRUTH"

    print(f"🔍 Thumbnail Search Query: '{search_query}'")
    print(f"🏷️ Category: '{category}' -> Using Primary Color: {primary_color} | Display Text: '{display_text}'")

    # 1. Fetch Stock Photo from Pexels
    if PEXELS_API_KEY and PEXELS_API_KEY != "your_pexels_api_key_here":
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/v1/search?query={search_query} cinematic&per_page=10&orientation=landscape"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                if photos:
                    import random
                    chosen_photo = random.choice(photos[:4])
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

    # 3. Cinematic Color Grading (Darker overlay for maximum text contrast)
    base_image = ImageEnhance.Contrast(base_image).enhance(1.3)
    base_image = ImageEnhance.Color(base_image).enhance(1.2)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 160))
    base_image = base_image.convert("RGBA")
    base_image = Image.alpha_composite(base_image, overlay).convert("RGB")

    draw = ImageDraw.Draw(base_image)
    
    # Accent Bars
    draw.rectangle([0, 0, width, 18], fill=(220, 38, 38))
    draw.rectangle([0, height-18, width, height], fill=(37, 99, 235))

    # 4. Load Fonts (Impact, Nirmala UI, or Arial Black for maximum boldness)
    font = None
    small_font = None
    font_paths = [
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'nirmala.ttf'),
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'gautami.ttf'),
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'impact.ttf'),
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arialbd.ttf'),
        "arial.ttf"
    ]
    for fpath in font_paths:
        if os.path.exists(fpath):
            try:
                font = ImageFont.truetype(fpath, 145)
                small_font = ImageFont.truetype(fpath, 65)
                break
            except Exception:
                continue
    if not font:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 5. Draw High-Visibility Text with Solid Dark Backing Cards & Outlines
    words = display_text.split()
    lines = []
    curr = ""
    for w in words:
        if len(curr + " " + w) < 15:
            curr += (" " + w) if curr else w
        else:
            lines.append(curr); curr = w
    if curr: lines.append(curr)

    y_text = 140
    for i, line in enumerate(lines[:3]):
        bbox = draw.textbbox((80, y_text), line, font=font)
        card_box = [bbox[0]-22, bbox[1]-14, bbox[2]+22, bbox[3]+14]
        
        # Solid dark backing card for 100% crystal-clear readability
        draw.rectangle(card_box, fill=(10, 15, 25))
        
        # Category Color Accent Line on the first card
        if i == 0:
            draw.rectangle([card_box[0], card_box[1], card_box[0]+18, card_box[3]], fill=primary_color)

        color = primary_color if i == 0 else (255, 255, 255)
        
        # Draw thick black outline / drop shadow for maximum punch
        for ox in [-4, 0, 4]:
            for oy in [-4, 0, 4]:
                if ox != 0 or oy != 0:
                    draw.text((80 + ox, y_text + oy), line, fill=(0, 0, 0), font=font)
                    
        # Draw main text
        draw.text((80, y_text), line, fill=color, font=font)
        y_text += 165
        
    # Bottom Badge
    badge_text = "🔥 100% UNTOLD TRUTH"
    bbox_b = draw.textbbox((80, 570), badge_text, font=small_font)
    draw.rectangle([bbox_b[0]-14, bbox_b[1]-10, bbox_b[2]+14, bbox_b[3]+10], fill=(0, 0, 0))
    for ox in [-2, 2]:
        for oy in [-2, 2]:
            draw.text((80 + ox, 570 + oy), badge_text, fill=(0, 0, 0), font=small_font)
    draw.text((80, 570), badge_text, fill=primary_color, font=small_font)

    base_image.save(output_path, "JPEG", quality=95)
    print(f"[Success] Category-Matched thumbnail generated at: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_thumbnail("కైలాస ఆలయం | Kailasa Temple Secret", "Ancient Indian Mysteries")
