import os
import requests
import html
import random
import time
import urllib.parse
from playwright.sync_api import sync_playwright
from config import READY_TO_REVIEW_DIR, PEXELS_API_KEY

def format_title_into_lines(text: str, max_words_per_line: int = 3) -> list:
    """Splits a long thumbnail title into punchy multi-line chunks for high CTR."""
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(current_line) >= max_words_per_line:
            lines.append(" ".join(current_line))
            current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines[:3] # Max 3 lines

def get_context_aware_emoji(category: str, title: str) -> str:
    """Selects a context-aware high-CTR emoji based on category or title content."""
    cat_lower = category.lower()
    title_lower = title.lower()

    if "space" in cat_lower or "science" in cat_lower or any(w in title_lower for w in ["space", "mars", "black hole", "planet", "universe", "nasa", "earth"]):
        return random.choice(["🌌", "🚀", "🪐", "🔭", "✨"])
    elif "ancient" in cat_lower or "mystery" in cat_lower or "mysteries" in cat_lower or any(w in title_lower for w in ["temple", "alayam", "secret", "rahasyam", "ancient", "pyramid", "history"]):
        return random.choice(["🏛️", "🗿", "🗝️", "🔍", "⚡"])
    elif "psychology" in cat_lower or "mind" in cat_lower or any(w in title_lower for w in ["mind", "brain", "psychology", "behavior", "people", "secret"]):
        return random.choice(["🧠", "👁️", "🎭", "⚠️", "🤫"])
    else:
        return random.choice(["😱", "🤯", "🚨", "🔥", "💥"])

def generate_thumbnail(title: str, category: str = "", output_path: str = None) -> str:
    """
    Generates an ultra-attractive, high-CTR cinematic YouTube thumbnail with 100% topic-matched
    AI background (Pollinations.ai), Google Fonts 'Baloo 2' bold typography, Split-Color Keyword Pop,
    Randomized Multi-Position / Multi-Angle Layouts, Context-Aware Emojis, and Watermark Blocker.
    """
    if not output_path:
        output_path = os.path.join(READY_TO_REVIEW_DIR, "thumbnail.jpg")
    
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
    width, height = 1280, 720

    # Check if title is a YouTube URL or Video ID
    yt_video_id = None
    if "youtu.be/" in title:
        yt_video_id = title.split("youtu.be/")[-1].split("?")[0].strip()
    elif "youtube.com/watch" in title and "v=" in title:
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

    # Determine full meaningful title for the thumbnail
    clean_title = title.replace("#shorts", "").replace("#Shorts", "").strip()
    if "|" in clean_title:
        parts = clean_title.split("|")
        thumbnail_text = parts[0].strip()
    else:
        thumbnail_text = clean_title

    if thumbnail_text.endswith("..."):
        thumbnail_text = thumbnail_text[:-3].strip()
    
    # Add context-aware high-CTR curiosity emoji if not already present
    all_emojis = ["😱", "🤯", "🚨", "🔥", "💥", "🌌", "🚀", "🪐", "🔭", "✨", "🏛️", "🗿", "🗝️", "🔍", "⚡", "🧠", "👁️", "🎭", "⚠️", "🤫"]
    if not any(e in thumbnail_text for e in all_emojis):
        context_emoji = get_context_aware_emoji(category, clean_title)
        thumbnail_text = f"{thumbnail_text} {context_emoji}"

    # Format into punchy multi-lines
    title_lines = format_title_into_lines(thumbnail_text, max_words_per_line=3)

    # Extract English search query for background generation
    search_query = clean_title
    if "|" in title:
        parts = title.split("|")
        if len(parts) > 1:
            search_query = parts[1].strip().split("#")[0].strip()

    print(f"🔍 Thumbnail Topic/Query: '{search_query}'")
    print(f"🏷️ Category: '{category}' -> Title Lines: {title_lines}")

    # 1. Generate Ultra-Attractive 100% Topic-Matched Cinematic AI Background (Pollinations.ai)
    ai_prompt = f"{search_query}, masterpiece, ultra detailed, hyperrealistic 8k resolution, Unreal Engine 5 render, dramatic cinematic moody lighting, vibrant neon and gold accents, award-winning photography, cinematic depth of field, movie poster style"
    encoded_prompt = urllib.parse.quote(ai_prompt)
    bg_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&seed={random.randint(1000, 99999)}"

    # 2. Seed deterministic pseudo-randomness based on title hash so each video gets a unique layout style
    title_seed = abs(hash(title))
    rng = random.Random(title_seed)

    vibrant_colors = [
        "#ffd700", # Electric Gold / Yellow
        "#00e5ff", # Neon Cyan
        "#ff3b30", # Electric Red
        "#39ff14", # Lime Green
        "#ff007f", # Hot Magenta
        "#ff6600"  # Neon Orange
    ]
    accent_color = rng.choice(vibrant_colors)

    # Randomly pick layout position: 'left', 'right', or 'center'
    layout_position = rng.choice(['left', 'right', 'center'])
    print(f"🎲 Randomized Layout Position: '{layout_position}' | Accent Color: {accent_color}")

    background_css = f"url('{bg_image_url}') center/cover no-repeat"

    # Build HTML lines markup with randomized angles and offsets
    lines_html = ""
    for i, line in enumerate(title_lines):
        words = line.split()
        if len(words) > 1:
            base_words = " ".join(words[:-1])
            highlight_word = words[-1]
            formatted_line = f'{html.escape(base_words)} <span style="color: {accent_color}; text-shadow: 0 0 25px {accent_color}, 4px 4px 0px #000;">{html.escape(highlight_word)}</span>'
        else:
            formatted_line = f'<span style="color: {accent_color}; text-shadow: 0 0 25px {accent_color}, 4px 4px 0px #000;">{html.escape(line)}</span>'

        angle = rng.randint(-5, 5)
        offset = rng.randint(-20, 25)

        lines_html += f'<div class="line" style="transform: rotate({angle}deg); margin-left: {offset}px;">{formatted_line}</div>\n'

    # Configure CSS alignment based on layout position
    if layout_position == 'right':
        flex_align = "justify-content: flex-end; padding-right: 80px;"
        text_align = "text-align: right;"
        overlay_bg = "linear-gradient(270deg, rgba(5, 5, 12, 0.88) 0%, rgba(5, 5, 12, 0.50) 52%, rgba(0, 0, 0, 0.05) 100%);"
    elif layout_position == 'center':
        flex_align = "justify-content: center; padding-left: 0px;"
        text_align = "text-align: center;"
        overlay_bg = "radial-gradient(circle, rgba(5, 5, 12, 0.75) 0%, rgba(5, 5, 12, 0.90) 100%);"
    else: # 'left'
        flex_align = "justify-content: flex-start; padding-left: 80px;"
        text_align = "text-align: left;"
        overlay_bg = "linear-gradient(90deg, rgba(5, 5, 12, 0.88) 0%, rgba(5, 5, 12, 0.50) 52%, rgba(0, 0, 0, 0.05) 100%);"

    # 3. Render High-Resolution Thumbnail using Playwright with Watermark Blocker
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@700;800&family=Noto+Sans+Telugu:wght@700;900&family=Noto+Sans+Devanagari:wght@700;900&display=swap" rel="stylesheet">
    <style>
      body {{
        margin: 0;
        width: 1280px;
        height: 720px;
        background: #0f172a {background_css};
        position: relative;
        display: flex;
        {flex_align}
        align-items: center;
        font-family: 'Baloo 2', 'Noto Sans Telugu', 'Noto Sans Devanagari', sans-serif;
      }}
      .overlay {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: {overlay_bg}
      }}
      .title-container {{
        position: relative;
        z-index: 10;
        max-width: 750px;
        {text_align}
        filter: drop-shadow(0 15px 35px rgba(0,0,0,0.9));
      }}
      .line {{
        font-size: 58px;
        font-weight: 800;
        line-height: 1.15;
        margin: 14px 0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #ffffff;
        text-shadow: 4px 4px 0px #000, -4px -4px 0px #000, 4px -4px 0px #000, -4px 4px 0px #000, 0px 8px 25px rgba(0,0,0,0.95);
        display: inline-block;
      }}
      /* Expanded Bulletproof Watermark Blocker at bottom-right corner */
      .watermark-blocker {{
        position: absolute;
        bottom: 0;
        right: 0;
        width: 380px;
        height: 90px;
        background: #05050c;
        z-index: 9999;
        border-top-left-radius: 20px;
      }}
    </style>
    </head>
    <body>
      <div class="overlay"></div>
      <div class="watermark-blocker"></div>
      <div class="title-container">
        {lines_html}
      </div>
    </body>
    </html>
    """

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        page.set_content(html_content)
        print("⏳ Waiting for AI image generation and rendering...")
        time.sleep(6)
        page.screenshot(path=output_path, type='jpeg', quality=95)
        browser.close()

    print(f"[Success] Context-Aware Emoji Thumbnail generated at: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    title_arg = sys.argv[1] if len(sys.argv) > 1 else "పద్మనాభస్వామి ఆలయం రహస్యం"
    out_path = os.path.join(READY_TO_REVIEW_DIR, "thumbnail.jpg")
    generate_thumbnail(title_arg, "Ancient Mysteries", out_path)
    print(f"Thumbnail generated at: {out_path}")
