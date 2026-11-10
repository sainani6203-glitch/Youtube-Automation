import os
import numpy as np
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip, concatenate_videoclips, AudioClip, concatenate_audioclips, CompositeAudioClip
except ImportError:
    from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip, concatenate_videoclips, AudioClip, concatenate_audioclips, CompositeAudioClip
from config import ASSETS_DIR
from thumbnail_generator import generate_thumbnail

def ensure_mono_audioclip(clip):
    try:
        duration = clip.duration
        fps = 44100
        arr = clip.to_soundarray(fps=fps)
        if arr.ndim > 1:
            arr = np.mean(arr, axis=1)
        return AudioClip(lambda t: np.interp(t, np.linspace(0, duration, len(arr)), arr), duration=duration, fps=fps)
    except Exception:
        return clip

def set_dur(clip, d):
    try: return clip.set_duration(d)
    except: return clip.with_duration(d)

def trim_clip(clip, start, end):
    try: return clip.subclip(start, end)
    except: return clip.subclipped(start, end)

def set_pos(clip, pos):
    try: return clip.set_position(pos)
    except: return clip.with_position(pos)

def set_vol(clip, vol):
    try: return clip.volumex(vol)
    except: return clip.with_volume_scaled(vol)

def set_aud(clip, aud):
    try: return clip.set_audio(aud)
    except: return clip.with_audio(aud)

def resize_clip(clip, **kwargs):
    try: return clip.resize(**kwargs)
    except: return clip.resized(**kwargs)

def crop_clip(clip, **kwargs):
    try: return clip.crop(**kwargs)
    except: return clip.cropped(**kwargs)

def render_video(audio_path: str, video_clips_paths: list, output_path: str, video_type: str = "short", title_text: str = "", category: str = "", scenes: list = None, language: str = "Telugu"):
    """
    Renders the final video by combining audio voiceover, stock video clips, captions, intro, and outro.
    video_type: 'short' (9:16 vertical, 1080x1920) or 'long' (16:9 horizontal, 1920x1080)
    """
    raw_audio = AudioFileClip(audio_path)
    audio = ensure_mono_audioclip(raw_audio)
    voiceover_duration = audio.duration
    
    width, height = (1080, 1920) if video_type == "short" else (1920, 1080)
    
    # 0. Generate Thumbnail file for YouTube upload. (Thumbnail intro frame removed so video starts directly with hook).
    thumb_path = None
    if title_text:
        try:
            is_vertical = (video_type == "short")
            thumb_path = generate_thumbnail(title_text, category=category, vertical=is_vertical, language=language)
        except Exception as e:
            print(f"[Warning] Could not generate thumbnail: {e}")
            thumb_path = None

    # 1. Check for custom intro in assets/intro.mp4
    intro_path = os.path.join(ASSETS_DIR, "intro.mp4")
    intro_clip = None
    intro_duration = 0
    if os.path.exists(intro_path):
        try:
            intro_clip = VideoFileClip(intro_path)
            intro_duration = intro_clip.duration
            intro_clip = resize_clip(intro_clip, height=height)
            if intro_clip.w < width:
                intro_clip = resize_clip(intro_clip, width=width)
            intro_clip = crop_clip(intro_clip, x_center=intro_clip.w/2, y_center=intro_clip.h/2, width=width, height=height)
        except Exception as e:
            print(f"[Warning] Could not load intro.mp4: {e}")
            intro_clip = None
            intro_duration = 0

    # 2. Check for custom outro in assets/outro.mp4
    outro_path = os.path.join(ASSETS_DIR, "outro.mp4")
    outro_clip = None
    outro_duration = 0
    if os.path.exists(outro_path):
        try:
            outro_clip = VideoFileClip(outro_path)
            outro_duration = outro_clip.duration
            outro_clip = resize_clip(outro_clip, height=height)
            if outro_clip.w < width:
                outro_clip = resize_clip(outro_clip, width=width)
            outro_clip = crop_clip(outro_clip, x_center=outro_clip.w/2, y_center=outro_clip.h/2, width=width, height=height)
        except Exception as e:
            print(f"[Warning] Could not load outro.mp4: {e}")
            outro_clip = None
            outro_duration = 0

    # 3. Build main visual content clips matching voiceover duration
    valid_clips = [p for p in video_clips_paths if p and os.path.exists(p)]
    sub_clips = []
    
    if valid_clips:
        clip_duration = voiceover_duration / len(valid_clips)
        for path in valid_clips:
            try:
                c = VideoFileClip(path)
                if c.duration < clip_duration:
                    repeats = int(clip_duration // c.duration) + 1
                    c = trim_clip(concatenate_videoclips([c] * repeats), 0, clip_duration)
                else:
                    c = trim_clip(c, 0, clip_duration)
                
                c = resize_clip(c, height=height)
                if c.w < width:
                    c = resize_clip(c, width=width)
                c = crop_clip(c, x_center=c.w/2, y_center=c.h/2, width=width, height=height)
                sub_clips.append(c)
            except Exception as e:
                print(f"[Warning] Error loading clip {path}: {e}")
                
    if sub_clips:
        while True:
            main_visual = concatenate_videoclips(sub_clips)
            if main_visual.duration >= voiceover_duration or len(sub_clips) > 20:
                break
            sub_clips.extend(sub_clips)
        main_visual = trim_clip(main_visual, 0, voiceover_duration)
    else:
        main_visual = set_dur(ColorClip(size=(width, height), color=(15, 23, 42)), voiceover_duration)

    # 4. Assemble full visual sequence
    sequence_visuals = []
    if video_type != "short":
        if intro_clip:
            sequence_visuals.append(intro_clip)
            
    sequence_visuals.append(main_visual)
    
    if video_type != "short":
        if outro_clip:
            sequence_visuals.append(outro_clip)
        
    final_visual = concatenate_videoclips(sequence_visuals)

    # 4.5. Burned-in subtitles disabled as requested
    if False and scenes and voiceover_duration > 0 and video_type == "short":
        subtitle_clips = []
        offset = 0
        for scene in scenes:
            txt = scene.get("text", "")
            if not txt:
                continue
            scene_start = scene.get("start_time", 0.0)
            scene_end = scene.get("end_time", scene_start + 2.0)
            
            start_t = offset + scene_start
            end_t = offset + scene_end
            
            try:
                sub_clip = TextClip(
                    text=txt,
                    font_size=38 if video_type == "short" else 44,
                    color='white',
                    stroke_color='black',
                    stroke_width=2,
                    size=(width - 150, None)
                ).with_position(('center', height - 400 if video_type == "short" else height - 220)).with_start(start_t).with_duration(max(0.5, end_t - start_t))
                subtitle_clips.append(sub_clip)
            except Exception as sub_err:
                print(f"[Note] Subtitle clip skipped for scene: {sub_err}")
        
        if subtitle_clips:
            try:
                final_visual = CompositeVideoClip([final_visual] + subtitle_clips, duration=final_visual.duration)
            except Exception as comp_err:
                print(f"[Note] Subtitle composition skipped: {comp_err}")

    # 5. Assemble full audio sequence
    audio_parts = []
    if video_type != "short":
        if intro_clip and intro_duration > 0:
            audio_parts.append(AudioClip(lambda t: np.zeros_like(t) if isinstance(t, np.ndarray) else 0.0, duration=intro_duration))
            
    audio_parts.append(audio)
    
    if video_type != "short":
        if outro_clip and outro_duration > 0:
            audio_parts.append(AudioClip(lambda t: np.zeros_like(t) if isinstance(t, np.ndarray) else 0.0, duration=outro_duration))
        
    final_audio_voice = concatenate_audioclips(audio_parts)
    total_duration = final_audio_voice.duration

    if video_type == "short":
        max_short_duration = 48.0
        if total_duration > max_short_duration:
            print(f"[Info] Short total duration ({total_duration:.2f}s) exceeds {max_short_duration}s. Trimming to {max_short_duration}s.")
            total_duration = max_short_duration
        else:
            total_duration = min(total_duration, max_short_duration)
    else:
        max_short_duration = total_duration

    # Strictly trim final_visual and final_audio_voice to total_duration
    final_visual = set_dur(trim_clip(final_visual, 0, total_duration), total_duration)
    final_audio_voice = set_dur(trim_clip(final_audio_voice, 0, total_duration), total_duration)

    # (Title watermark overlay removed to keep video clean and professional)

    # 6b. Add visual "SUBSCRIBE" reminder overlay & notification sound effect during the final seconds
    try:
        sub_reminder_clip = TextClip(text="🔔 SUBSCRIBE FOR MORE", font_size=40, color='yellow', stroke_color='black', stroke_width=2)
        sub_start = max(0, total_duration - 5.0)
        sub_reminder_clip = set_dur(sub_reminder_clip.set_position(('center', height - 280)).set_start(sub_start), 5.0)
        final_visual = set_dur(CompositeVideoClip([final_visual, sub_reminder_clip], duration=total_duration), total_duration)

        def make_chime(t):
            f1, f2 = 587.33, 880.00
            val1 = 0.25 * np.sin(2 * np.pi * f1 * t) * np.exp(-3 * t)
            val2 = np.where(t >= 0.15, 0.35 * np.sin(2 * np.pi * f2 * (t - 0.15)) * np.exp(-3 * (t - 0.15)), 0.0)
            return val1 + val2
        
        chime_clip = set_dur(AudioClip(make_chime, duration=0.5).set_start(sub_start), 0.5)
        chime_clip = ensure_mono_audioclip(chime_clip)
        final_audio_voice = set_dur(CompositeAudioClip([final_audio_voice, chime_clip], duration=total_duration), total_duration)
    except Exception as e:
        print(f"[Note] Subscribe reminder clip/audio skipped: {e}")

    # 6c. Add category-matched Sound Effect (SFX) at the beginning hook
    sfx_filename = "sfx_ancient_mysteries.mp3"
    if "Dark Psychology" in category:
        sfx_filename = "sfx_dark_psychology.mp3"
    elif "Ancient" in category:
        sfx_filename = "sfx_ancient_mysteries.mp3"
    elif "Incredible Science" in category:
        sfx_filename = "sfx_science_space.mp3"
        
    sfx_path = os.path.join(ASSETS_DIR, sfx_filename)
    if os.path.exists(sfx_path):
        try:
            raw_sfx = AudioFileClip(sfx_path)
            sfx_clip = ensure_mono_audioclip(raw_sfx)
            sfx_start = intro_duration
            sfx_clip = sfx_clip.set_start(sfx_start)
            final_audio_voice = set_dur(CompositeAudioClip([final_audio_voice, sfx_clip], duration=total_duration), total_duration)
        except Exception as e:
            print(f"[Note] SFX mixing skipped: {e}")

    # 7. Select category-matched background music (Long videos only, skip for shorts)
    bgm_path = None
    if video_type != "short":
        bgm_filename = "bgm.mp3"
        if "Dark Psychology" in category:
            bgm_filename = "bgm_dark_psychology.mp3"
        elif "Ancient" in category:
            bgm_filename = "bgm_ancient_mysteries.mp3"
        elif "Incredible Science" in category:
            bgm_filename = "bgm_science_space.mp3"
            
        bgm_path = os.path.join(ASSETS_DIR, bgm_filename)
        if not os.path.exists(bgm_path):
            bgm_path = os.path.join(ASSETS_DIR, "bgm.mp3")

    final_audio = final_audio_voice
    bgm_clip = None
    if bgm_path and os.path.exists(bgm_path):
        try:
            raw_bgm = AudioFileClip(bgm_path)
            bgm_clip = ensure_mono_audioclip(raw_bgm)
            bgm_dur = getattr(bgm_clip, 'duration', None)
            if bgm_dur and bgm_dur > 0 and bgm_dur < 86400:
                if bgm_dur < total_duration:
                    repeats = int(total_duration // bgm_dur) + 1
                    bgm_clip = concatenate_audioclips([bgm_clip] * repeats)
            bgm_clip = trim_clip(bgm_clip, 0, total_duration)
            bgm_volume = 0.35 if video_type == "short" else 0.45
            bgm_clip = set_dur(set_vol(bgm_clip, bgm_volume), total_duration)
            final_audio = set_dur(CompositeAudioClip([final_audio_voice, bgm_clip], duration=total_duration), total_duration)
        except Exception as e:
            print(f"[Warning] BGM mixing skipped: {e}")

    # Final strict enforcement of total_duration on visual and audio
    final_visual = set_dur(trim_clip(final_visual, 0, total_duration), total_duration)
    final_audio = set_dur(trim_clip(final_audio, 0, total_duration), total_duration)

    final_composite = set_dur(trim_clip(set_aud(final_visual, final_audio), 0, total_duration), total_duration)
    
    target_bitrate = "8000k" if video_type != "short" else "4000k"
    
    final_composite.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        bitrate=target_bitrate,
        audio_codec='aac',
        audio_bitrate='128k',
        preset='veryfast',
        threads=2,
        ffmpeg_params=[
            '-movflags', '+faststart',
            '-fps_mode', 'cfr',
            '-pix_fmt', 'yuv420p',
            '-ar', '44100',
            '-g', '48',
            '-keyint_min', '24',
            '-profile:v', 'main',
            '-level', '4.0'
        ]
    )
    
    # Close clips
    audio.close()
    if intro_clip: intro_clip.close()
    if outro_clip: outro_clip.close()
    if bgm_clip: bgm_clip.close()
    final_composite.close()
    
    if thumb_path and os.path.exists(thumb_path):
        try:
            os.remove(thumb_path)
        except:
            pass
            
    print(f"[Success] Video successfully rendered at: {output_path} (Duration: {total_duration:.2f}s)")
    return output_path
