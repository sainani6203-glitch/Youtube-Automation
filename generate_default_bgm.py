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
            
    # Generate Category-Matched Sound Effects (SFX) for transitions/hooks
    sfx_configs = {
        "sfx_dark_psychology.mp3": (50.0, 2.0),     # Deep tense sub drop
        "sfx_ancient_mysteries.mp3": (523.25, 1.5), # Mystical bell chime (C5)
        "sfx_science_space.mp3": (1046.50, 1.0)     # Futuristic sci-fi sweep (C6)
    }
    
    for filename, (freq, sfx_dur) in sfx_configs.items():
        sfx_path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(sfx_path):
            print(f"🔔 Generating category SFX: {filename}...")
            t_sfx = np.linspace(0, sfx_dur, int(fps * sfx_dur))
            if "psychology" in filename:
                signal = 0.15 * np.sin(2 * np.pi * freq * t_sfx) * np.exp(-1.5 * t_sfx) * (1 + np.sin(2 * np.pi * 5 * t_sfx))
            elif "mysteries" in filename:
                signal = 0.15 * np.sin(2 * np.pi * freq * t_sfx) * np.exp(-3.0 * t_sfx) + 0.1 * np.sin(2 * np.pi * freq * 1.5 * t_sfx) * np.exp(-4.0 * t_sfx)
            else:
                signal = 0.12 * np.sin(2 * np.pi * freq * t_sfx * (1 - 0.5 * t_sfx / sfx_dur)) * np.exp(-2.0 * t_sfx)
                
            audio_array = np.vstack((signal, signal)).T
            clip = AudioArrayClip(audio_array, fps=fps)
            clip.write_audiofile(sfx_path, fps=fps, logger=None)
            clip.close()

    # Ensure default bgm.mp3 exists as fallback
    default_bgm = os.path.join(ASSETS_DIR, "bgm.mp3")
    if not os.path.exists(default_bgm):
        import shutil
        shutil.copy(os.path.join(ASSETS_DIR, "bgm_ancient_mysteries.mp3"), default_bgm)
        
    return default_bgm

if __name__ == "__main__":
    create_default_bgm()
