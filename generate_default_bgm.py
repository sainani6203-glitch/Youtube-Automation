import os
import numpy as np
from moviepy import AudioArrayClip
from config import ASSETS_DIR

def create_default_bgm():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    bgm_path = os.path.join(ASSETS_DIR, "bgm.mp3")
    if os.path.exists(bgm_path):
        print("Default BGM already exists.")
        return bgm_path

    print("🎵 Generating default cinematic ambient BGM...")
    duration = 30.0  # 30 seconds loop
    fps = 44100
    t = np.linspace(0, duration, int(fps * duration))
    
    # Soothing low cinematic chord (A minor ambient pad: 110Hz, 164.81Hz, 196Hz) with smooth modulation
    signal = 0.08 * (
        np.sin(2 * np.pi * 110.0 * t) + 
        np.sin(2 * np.pi * 164.81 * t) + 
        np.sin(2 * np.pi * 196.00 * t)
    ) * (0.4 + 0.6 * np.sin(2 * np.pi * 0.05 * t))
    
    # Stereo
    audio_array = np.vstack((signal, signal)).T
    clip = AudioArrayClip(audio_array, fps=fps)
    clip.write_audiofile(bgm_path, fps=fps, logger=None)
    clip.close()
    print(f"[Success] Default BGM generated at: {bgm_path}")
    return bgm_path

if __name__ == "__main__":
    create_default_bgm()
