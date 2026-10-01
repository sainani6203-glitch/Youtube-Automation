import os
from moviepy import ColorClip, TextClip, CompositeVideoClip
from config import ASSETS_DIR

def create_default_outro():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    outro_path = os.path.join(ASSETS_DIR, "outro.mp4")
    if os.path.exists(outro_path):
        print("Default Outro video already exists.")
        return outro_path

    print("🎬 Generating default Subscribe Outro video...")
    width, height = 1080, 1920  # Vertical default, works for short/long
    duration = 3.0
    
    bg = ColorClip(size=(width, height), color=(15, 23, 42)).with_duration(duration)
    
    try:
        txt = TextClip("SUBSCRIBE & LIKE\nFor More Mysteries!", fontsize=60, color='white', font='Arial-Bold', bg_color='rgba(220,38,38,0.8)', size=(width-100, None))
        txt = txt.set_position(('center', 'center')).set_duration(duration)
        clip = CompositeVideoClip([bg, txt])
    except Exception:
        clip = bg

    clip.write_videofile(
        outro_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        preset='medium',
        logger=None
    )
    clip.close()
    print(f"[Success] Default Outro video generated at: {outro_path}")
    return outro_path

if __name__ == "__main__":
    create_default_outro()
