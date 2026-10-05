import os
import numpy as np
from moviepy import AudioArrayClip
from config import ASSETS_DIR

def create_default_bgm():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    bgms = {
        "bgm_dark_psychology.mp3": (75.0, 110.0, 0.04),      # Deep tense drone
        "bgm_ancient_mysteries.mp3": (110.0, 164.81, 0.05),  # Mystical ambient pad
        "bgm_science_space.mp3": (220.0, 329.63, 0.06)      # Cosmic synthesizer
    }
    
    fps = 44100
    duration = 30.0
    t = np.linspace(0, duration, int(fps * duration))
    
    for filename, (f1, f2, mod) in bgms.items():
        bgm_path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(bgm_path):
            print(f"🎵 Generating category BGM: {filename}...")
            signal = 0.07 * (
                np.sin(2 * np.pi * f1 * t) + 
                np.sin(2 * np.pi * f2 * t)
            ) * (0.3 + 0.7 * np.sin(2 * np.pi * mod * t))
            audio_array = np.vstack((signal, signal)).T
            clip = AudioArrayClip(audio_array, fps=fps)
            clip.write_audiofile(bgm_path, fps=fps, logger=None)
            clip.close()
            
    # Ensure default bgm.mp3 exists as fallback
    default_bgm = os.path.join(ASSETS_DIR, "bgm.mp3")
    if not os.path.exists(default_bgm):
        import shutil
        shutil.copy(os.path.join(ASSETS_DIR, "bgm_ancient_mysteries.mp3"), default_bgm)
        
    return default_bgm

if __name__ == "__main__":
    create_default_bgm()
