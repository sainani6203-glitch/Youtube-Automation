import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from config import READY_TO_REVIEW_DIR, PEXELS_API_KEY

def generate_thumbnail(title: str, category: str = "", output_path: str = None) -> str:
    """
    Generates a high-CTR 1280x720 YouTube cinematic thumbnail featuring:
    1. Topic-relevant stock photo from Pexels.
    2. Category-matched dynamic colors for primary hook text.
    3. Solid dark backing cards for 100% crystal-clear readability.
    """
    if not output_path:
        output_path = os.path.join(READY_TO_REVIEW_DIR, "thumbnail.jpg")
        
    width, height = 1280, 720
    base_image = None

    # Determine Category-based Color Palette
    # Default: Gold/Yellow
    primary_color = (255, 235, 59) 
    
    if "Dark Psychology" in category:
        primary_color = (239, 68, 68)   # Intense Red
    elif "Ancient Indian" in category:
        primary_color = (251, 191, 36)  # Ancient Gold
    elif "Incredible Science" in category:
        primary_color = (56, 189, 248)  # Electric Blue

    # Extract English keywords from bilingual title
    search_query = title
    display_text = "TOP SECRET"
    if "|" in title:
        parts = title.split("|")
        if len(parts) > 1:
            eng_part = parts[1].strip().split("#")[0].strip()
            search_query = eng_part
            words = eng_part.upper().split()
            display_text = " ".join(words[:4])

    print(f"🔍 Thumbnail Search Query: '{search_query}'")
    print(f"🏷️ Category: '{category}' -> Using Primary Color: {primary_color}")

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

    # 3. Cinematic Color Grading
    base_image = ImageEnhance.Contrast(base_image).enhance(1.25)
    base_image = ImageEnhance.Color(base_image).enhance(1.2)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 130))
    base_image = base_image.convert("RGBA")
    base_image = Image.alpha_composite(base_image, overlay).convert("RGB")

    draw = ImageDraw.Draw(base_image)
    
    # Accent Bars
    draw.rectangle([0, 0, width, 18], fill=(220, 38, 38))
    draw.rectangle([0, height-18, width, height], fill=(37, 99, 235))

    # 4. Load Fonts
    font = None
    small_font = None
    font_paths = [
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'impact.ttf'),
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arialbd.ttf'),
        "arial.ttf"
    ]
    for fpath in font_paths:
        if os.path.exists(fpath):
            try:
                font = ImageFont.truetype(fpath, 75)
                small_font = ImageFont.truetype(fpath, 42)
                break
            except Exception:
                continue
    if not font:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 5. Draw Text with Solid Backing Cards
    words = display_text.split()
    lines = []
    curr = ""
    for w in words:
        if len(curr + " " + w) < 18:
            curr += (" " + w) if curr else w
        else:
            lines.append(curr); curr = w
    if curr: lines.append(curr)

    y_text = 200
    for i, line in enumerate(lines[:3]):
        bbox = draw.textbbox((80, y_text), line, font=font)
        card_box = [bbox[0]-16, bbox[1]-10, bbox[2]+16, bbox[3]+10]
        draw.rectangle(card_box, fill=(15, 23, 42))
        
        # Category Color Accent Line on the first card
        if i == 0:
            draw.rectangle([card_box[0], card_box[1], card_box[0]+12, card_box[3]], fill=primary_color)

        color = primary_color if i == 0 else (255, 255, 255)
        draw.text((80, y_text), line, fill=color, font=font)
        y_text += 105
        
    # Bottom Badge
    badge_text = "🔥 100% UNTOLD TRUTH"
    bbox_b = draw.textbbox((80, 560), badge_text, font=small_font)
    draw.rectangle([bbox_b[0]-12, bbox_b[1]-8, bbox_b[2]+12, bbox_b[3]+8], fill=(0, 0, 0))
    draw.text((80, 560), badge_text, fill=primary_color, font=small_font)

    base_image.save(output_path, "JPEG", quality=95)
    print(f"[Success] Category-Matched thumbnail generated at: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_thumbnail("కైలాస ఆలయం | Kailasa Temple Secret", "Ancient Indian Mysteries")
