import os
import requests
import html
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
from config import READY_TO_REVIEW_DIR, PEXELS_API_KEY

def generate_thumbnail(title: str, category: str = "", output_path: str = None) -> str:
    """
    Generates a high-CTR, cinematic 1280x720 YouTube thumbnail with bold typography,
    category-matched color grading, dynamic layout variation, and zero repetition.
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

    # Determine Category-based Color Palette & Theme Accents
    # Palettes: Primary color, Accent color, Glow color
    if "Dark Psychology" in category:
        primary_color = (239, 68, 68)    # Vibrant Red
        accent_color = (255, 255, 255)   # Crisp White
        badge_list = ["🔥 DARK SECRETS", "⚠️ MIND TRICKS", "👁️ MANIPULATION", "🚨 EXPOSED"]
    elif "Ancient Indian" in category:
        primary_color = (251, 191, 36)   # Ancient Gold
        accent_color = (255, 255, 255)   # Crisp White
        badge_list = ["🔮 LOST HISTORY", "🛕 ANCIENT MYSTERY", "⚡ FORGOTTEN PAST", "🔱 UNTOLD TRUTH"]
    elif "Incredible Science" in category:
        primary_color = (56, 189, 248)   # Electric Cyan/Blue
        accent_color = (255, 255, 255)   # Crisp White
        badge_list = ["🚀 MIND BLOWING", "🌌 UNIVERSE SECRETS", "⚡ SCIENCE WONDERS", "🛰️ FUTURE TECH"]
    else:
        primary_color = (244, 63, 94)    # Rose Pink / Red
        accent_color = (250, 204, 21)    # Golden Yellow
        badge_list = ["🔥 100% UNTOLD", "⚡ SHOCKING TRUTH", "👁️ SECRET REVEALED", "🚨 MUST WATCH"]

    # Extract clean English keywords or powerful punchy hook
    search_query = title
    display_words = []
    
    stop_words = {"THE", "OF", "IN", "A", "AN", "AND", "TO", "FOR", "ON", "WITH", "IS", "IT", "BY", "AT", "THIS", "THAT", "SHORTS"}

    if "|" in title:
        parts = title.split("|")
        if len(parts) > 1:
            eng_part = parts[1].strip().split("#")[0].strip()
            search_query = eng_part
            raw_words = [w.strip('.,!?:;""\'()[]-') for w in eng_part.upper().split() if all(ord(c) < 128 for c in w)]
            display_words = [w for w in raw_words if w not in stop_words and len(w) > 1]
    
    if not display_words:
        raw_words = [w.strip('.,!?:;""\'()[]-') for w in title.upper().split() if all(ord(c) < 128 for c in w)]
        display_words = [w for w in raw_words if w not in stop_words and len(w) > 1]
        
    if not display_words:
        display_words = ["SHOCKING", "SECRET"]

    # Take up to 4 impactful words for a clean 2-line headline
    selected_words = display_words[:4]
    if len(selected_words) >= 3:
        line1 = " ".join(selected_words[:2])
        line2 = " ".join(selected_words[2:])
    elif len(selected_words) == 2:
        line1 = selected_words[0]
        line2 = selected_words[1]
    else:
        line1 = selected_words[0]
        line2 = random.choice(["SECRET", "EXPOSED", "TRUTH", "MYSTERY"])

    print(f"🔍 Thumbnail Search Query: '{search_query}'")
    print(f"🏷️ Category: '{category}' -> Line 1: '{line1}' | Line 2: '{line2}'")

    # 1. Fetch Stock Photo from Pexels if base image not already loaded
    if not base_image and PEXELS_API_KEY and PEXELS_API_KEY != "your_pexels_api_key_here":
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/v1/search?query={search_query} cinematic moody dark mysterious&per_page=15&orientation=landscape"
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

    # 3. Cinematic Color Grading (Professional contrast & dark gradient overlay for crystal-clear readability)
    base_image = ImageEnhance.Contrast(base_image).enhance(1.35)
    base_image = ImageEnhance.Color(base_image).enhance(1.25)
    
    # Create radial / vertical gradient overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 175))
    base_image = base_image.convert("RGBA")
    base_image = Image.alpha_composite(base_image, overlay).convert("RGB")

    draw = ImageDraw.Draw(base_image)
    
    # Top & Bottom Accent Cinematic Bars
    draw.rectangle([0, 0, width, 14], fill=primary_color)
    draw.rectangle([0, height-14, width, height], fill=(15, 23, 42))

    # 4. Load High-Impact Fonts (Impact / Arial Bold / DejaVu Sans Bold)
    font_large = None
    font_badge = None
    font_paths = [
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'impact.ttf'),
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arialbd.ttf'),
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'nirmala.ttf'),
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'gautami.ttf'),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "arial.ttf"
    ]
    for fpath in font_paths:
        if os.path.exists(fpath):
            try:
                font_large = ImageFont.truetype(fpath, 150)
                font_badge = ImageFont.truetype(fpath, 60)
                break
            except Exception:
                continue
    if not font_large:
        font_large = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # 5. Dynamic Layout Selection (To ensure zero repetition every day)
    layout_style = random.choice(["left_banner", "center_stacked", "diagonal_split"])

    x_start = 80
    y_start = 160

    if layout_style == "left_banner":
        # Side vertical color accent bar on the left
        draw.rectangle([x_start - 30, y_start - 20, x_start - 12, y_start + 360], fill=primary_color)
        
        # Render Line 1
        bbox1 = draw.textbbox((x_start, y_start), line1, font=font_large)
        # Drop shadow / thick outline
        for ox in [-5, -3, 0, 3, 5]:
            for oy in [-5, -3, 0, 3, 5]:
                if ox != 0 or oy != 0:
                    draw.text((x_start + ox, y_start + oy), line1, fill=(0, 0, 0), font=font_large)
        draw.text((x_start, y_start), line1, fill=primary_color, font=font_large)
        
        # Render Line 2
        y_line2 = y_start + 165
        for ox in [-5, -3, 0, 3, 5]:
            for oy in [-5, -3, 0, 3, 5]:
                if ox != 0 or oy != 0:
                    draw.text((x_start + ox, y_line2 + oy), line2, fill=(0, 0, 0), font=font_large)
        draw.text((x_start, y_line2), line2, fill=accent_color, font=font_large)

    elif layout_style == "center_stacked":
        # Center-left prominent text with semi-transparent solid background panel
        combined_text_bbox = draw.textbbox((x_start, y_start), f"{line1}\n{line2}", font=font_large)
        panel_box = [x_start - 25, y_start - 20, combined_text_bbox[2] + 45, y_start + 350]
        draw.rectangle(panel_box, fill=(10, 15, 25, 220))
        draw.rectangle([panel_box[0], panel_box[1], panel_box[0] + 16, panel_box[3]], fill=primary_color)

        # Draw Line 1
        for ox in [-4, 0, 4]:
            for oy in [-4, 0, 4]:
                if ox != 0 or oy != 0:
                    draw.text((x_start + ox, y_start + oy), line1, fill=(0, 0, 0), font=font_large)
        draw.text((x_start, y_start), line1, fill=primary_color, font=font_large)

        # Draw Line 2
        y_line2 = y_start + 165
        for ox in [-4, 0, 4]:
            for oy in [-4, 0, 4]:
                if ox != 0 or oy != 0:
                    draw.text((x_start + ox, y_line2 + oy), line2, fill=(0, 0, 0), font=font_large)
        draw.text((x_start, y_line2), line2, fill=accent_color, font=font_large)

    else: # diagonal_split / clean modern
        # Top line in primary color, bottom line with highlight box
        for ox in [-5, 0, 5]:
            for oy in [-5, 0, 5]:
                if ox != 0 or oy != 0:
                    draw.text((x_start + ox, y_start + oy), line1, fill=(0, 0, 0), font=font_large)
        draw.text((x_start, y_start), line1, fill=accent_color, font=font_large)

        y_line2 = y_start + 165
        bbox2 = draw.textbbox((x_start, y_line2), line2, font=font_large)
        draw.rectangle([bbox2[0]-16, bbox2[1]-8, bbox2[2]+16, bbox2[3]+8], fill=primary_color)
        
        for ox in [-4, 0, 4]:
            for oy in [-4, 0, 4]:
                if ox != 0 or oy != 0:
                    draw.text((x_start + ox, y_line2 + oy), line2, fill=(0, 0, 0), font=font_large)
        draw.text((x_start, y_line2), line2, fill=(255, 255, 255), font=font_large)

    # 6. High-Impact Bottom Badge (Rotated daily for freshness)
    badge_text = random.choice(badge_list)
    badge_x = 80
    badge_y = 570
    
    bbox_b = draw.textbbox((badge_x, badge_y), badge_text, font=font_badge)
    draw.rectangle([bbox_b[0]-18, bbox_b[1]-12, bbox_b[2]+18, bbox_b[3]+12], fill=(0, 0, 0))
    draw.rectangle([bbox_b[0]-18, bbox_b[1]-12, bbox_b[0]-10, bbox_b[3]+12], fill=primary_color)

    for ox in [-2, 2]:
        for oy in [-2, 2]:
            draw.text((badge_x + ox, badge_y + oy), badge_text, fill=(0, 0, 0), font=font_badge)
    draw.text((badge_x, badge_y), badge_text, fill=accent_color, font=font_badge)

    base_image.save(output_path, "JPEG", quality=95)
    print(f"[Success] High-CTR cinematic thumbnail generated at: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_thumbnail("https://youtu.be/p7qiO9b2axU", "Ancient Indian Mysteries")
