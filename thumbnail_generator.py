import os
from PIL import Image, ImageDraw, ImageFont
from config import READY_TO_REVIEW_DIR

def generate_thumbnail(title: str, output_path: str = None) -> str:
    """
    Generates a high-CTR 1280x720 YouTube thumbnail using Pillow with vibrant background and bold text.
    """
    if not output_path:
        output_path = os.path.join(READY_TO_REVIEW_DIR, "thumbnail.jpg")
        
    width, height = 1280, 720
    # Create dark mysterious background with gradient feel
    image = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(image)
    
    # Draw decorative gradient / accent shapes
    draw.rectangle([0, 0, width, 20], fill=(220, 38, 38)) # Red accent bar top
    draw.rectangle([0, height-20, width, height], fill=(37, 99, 235)) # Blue accent bar bottom
    
    # Draw central glowing / spotlight effect using circles or simple styling
    draw.ellipse([width//2 - 400, height//2 - 300, width//2 + 400, height//2 + 300], fill=(30, 41, 59))

    # Add text
    try:
        # Try to load a standard system font or default
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
        
    # Wrap title into lines
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) < 25:
            current_line += (" " + word) if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
        
    # Draw title text centered
    y_text = 200
    for line in lines[:3]: # max 3 lines
        draw.text((80, y_text), line, fill=(255, 255, 255), font=font_large)
        y_text += 80
        
    draw.text((80, 560), "100% UNTOSHABLE MYSTERY", fill=(239, 68, 68), font=font_small)
    
    image.save(output_path, "JPEG", quality=95)
    print(f"[Success] Thumbnail generated at: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_thumbnail("కైలాస ఆలయం: 3D రాతి శిల్పకళా అద్భుతం")
