import os
import numpy as np
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip, concatenate_videoclips, AudioClip, concatenate_audioclips, CompositeAudioClip
from config import ASSETS_DIR
from thumbnail_generator import generate_thumbnail

def ensure_mono_audioclip(clip):
    try:
        duration = clip.duration
        fps = 44100
        arr = clip.to_soundarray(fps=fps)
        if arr.ndim == 1:
            stereo_arr = np.column_stack([arr, arr])
        elif arr.ndim > 1 and arr.shape[1] == 1:
            stereo_arr = np.column_stack([arr[:, 0], arr[:, 0]])
        elif arr.ndim > 1 and arr.shape[1] >= 2:
            stereo_arr = arr[:, :2]
        else:
            stereo_arr = np.column_stack([arr.flatten(), arr.flatten()])

        def make_frame(t):
            t_arr = np.asarray(t).flatten()
            indices = np.clip((t_arr * fps).astype(int), 0, len(stereo_arr) - 1)
            return stereo_arr[indices]

        return AudioClip(make_frame, duration=duration, fps=fps)
    except Exception:
        return clip

def make_silent_clip(duration):
    def make_frame(t):
        t_arr = np.asarray(t).flatten()
        return np.zeros((len(t_arr), 2))
    return AudioClip(make_frame, duration=duration, fps=44100)

def set_dur(clip, d):
    for method in ['set_duration', 'with_duration']:
        if hasattr(clip, method):
            try: return getattr(clip, method)(d)
            except: pass
    return clip

def set_start(clip, t):
    for method in ['set_start', 'with_start']:
        if hasattr(clip, method):
            try: return getattr(clip, method)(t)
            except: pass
    return clip

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

def safe_composite_video(clips, duration=None):
    try:
        return CompositeVideoClip(clips, duration=duration)
    except TypeError:
        comp = CompositeVideoClip(clips)
        if duration is not None:
            comp = set_dur(comp, duration)
        return comp

def safe_text_clip(text_content, font_size=40, color='white', stroke_color='black', stroke_width=2, size=None, **kwargs):
    """Generates a text clip using Playwright (for Telugu/Hindi with Google Fonts) or PIL (for English)."""
    has_indic = any('\u0C00' <= c <= '\u0C7F' or '\u0900' <= c <= '\u097F' for c in text_content)
    
    if has_indic:
        try:
            from playwright.sync_api import sync_playwright
            import tempfile
            import html
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@700;900&family=Noto+Sans+Devanagari:wght@700;900&display=swap" rel="stylesheet">
            <style>
              body {{
                margin: 0;
                background: transparent;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 10px;
                font-family: 'Noto Sans Telugu', 'Noto Sans Devanagari', sans-serif;
              }}
              .subtitle-pill {{
                background: rgba(0, 0, 0, 0.88);
                border: 2px solid rgba(255, 255, 255, 0.35);
                border-radius: 20px;
                padding: 14px 28px;
                max-width: 950px;
                text-align: center;
                color: #ffffff;
                font-size: {max(font_size * 1.35, 38)}px;
                font-weight: 900;
                line-height: 1.3;
                text-shadow: 2px 2px 4px #000, -2px -2px 4px #000, 2px -2px 4px #000, -2px 2px 4px #000, 0px 4px 15px rgba(0,0,0,0.9);
                box-shadow: 0 10px 30px rgba(0,0,0,0.85);
              }}
            </style>
            </head>
            <body>
              <div class="subtitle-pill">{html.escape(text_content)}</div>
            </body>
            </html>
            """
            
            temp_fd, temp_path = tempfile.mkstemp(suffix=".png")
            os.close(temp_fd)
            
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1000, 'height': 300})
                page.set_content(html_content, wait_until="domcontentloaded")
                page.wait_for_timeout(600)
                element = page.locator(".subtitle-pill")
                element.screenshot(path=temp_path, type='png', omit_background=True)
                browser.close()
                
            from moviepy.editor import ImageClip
            return ImageClip(temp_path)
        except Exception as e:
            print(f"[Warning] Playwright Indic subtitle rendering failed: {e}, falling back to PIL")

    try:
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        
        max_w = size[0] if size and size[0] else 1000
        
        candidates = [
            "DejaVuSans-Bold.ttf",
            "arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
        
        font = None
        for cp in candidates:
            try:
                if os.path.exists(cp) or not cp.startswith("/"):
                    font = ImageFont.truetype(cp, font_size)
                    break
            except:
                continue
        if not font:
            font = ImageFont.load_default()

        words = text_content.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) * (font_size * 0.45) > max_w and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        if not lines:
            lines = [text_content]

        line_spacing = int(font_size * 0.3)
        dummy_img = Image.new("RGBA", (10, 10))
        draw_dummy = ImageDraw.Draw(dummy_img)
        
        line_heights = []
        max_line_w = 0
        for line in lines:
            bbox = draw_dummy.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            max_line_w = max(max_line_w, lw)
            line_heights.append(lh)

        total_h = sum(line_heights) + line_spacing * (len(lines) - 1) + 40
        img_w = max(max_line_w + 60, 100)
        img_h = max(total_h + 20, 50)

        if img_w % 2 != 0:
            img_w += 1
        if img_h % 2 != 0:
            img_h += 1

        txt_img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_img)

        draw.rounded_rectangle(
            [10, 5, img_w - 10, img_h - 5],
            radius=18,
            fill=(0, 0, 0, 190),
            outline=(255, 255, 255, 60),
            width=2
        )

        y_text = 20
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            x_text = int(((img_w - lw) / 2) // 2 * 2)
            y_text = int(y_text // 2 * 2)
            
            if stroke_width > 0 and stroke_color:
                for adj_x in range(-stroke_width, stroke_width + 1):
                    for adj_y in range(-stroke_width, stroke_width + 1):
                        if adj_x != 0 or adj_y != 0:
                            draw.text((x_text + adj_x, y_text + adj_y), line, font=font, fill=stroke_color)
            
            draw.text((x_text, y_text), line, font=font, fill=color)
            y_text += line_heights[i] + line_spacing

        temp_fd, temp_path = tempfile.mkstemp(suffix=".png")
        os.close(temp_fd)
        txt_img.save(temp_path, "PNG")

        from moviepy.editor import ImageClip
        
        return ImageClip(temp_path)
    except Exception as e:
        print(f"[Warning] PIL safe_text_clip failed: {e}, falling back to TextClip")
        try:
            return TextClip(text=text_content, font_size=font_size, **kwargs)
        except:
            return TextClip(txt=text_content, fontsize=font_size, **kwargs)

def safe_composite_audio(clips, duration=None):
    try:
        return CompositeAudioClip(clips, duration=duration)
    except TypeError:
        comp = CompositeAudioClip(clips)
        if duration is not None:
            comp = set_dur(comp, duration)
        return comp

def resize_clip(clip, **kwargs):
    try: 
        c = clip.resize(**kwargs)
    except: 
        c = clip.resized(**kwargs)
    if hasattr(c, 'w') and hasattr(c, 'h') and c.w and c.h:
        w, h = int(c.w), int(c.h)
        ew, eh = (w // 2) * 2, (h // 2) * 2
        if w != ew or h != eh:
            try: c = c.resize(width=ew, height=eh)
            except:
                try: c = c.resized(width=ew, height=eh)
                except: pass
    return c

def crop_clip(clip, **kwargs):
    try: 
        c = clip.crop(**kwargs)
    except: 
        c = clip.cropped(**kwargs)
    if hasattr(c, 'w') and hasattr(c, 'h') and c.w and c.h:
        w, h = int(c.w), int(c.h)
        ew, eh = (w // 2) * 2, (h // 2) * 2
        if w != ew or h != eh:
            try: c = c.resize(width=ew, height=eh)
            except:
                try: c = c.resized(width=ew, height=eh)
                except: pass
    return c

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
            # Robust Resize & Crop to fill 100% of the target resolution
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
            # Robust Resize & Crop to fill 100% of the target resolution
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
                
                # Strictly resize to fill target dimensions (fill the smaller dimension first)
                c = resize_clip(c, height=height)
                if c.w < width:
                    c = resize_clip(c, width=width)
                
                # Perform a centered crop to match exact target dimensions
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
        try:
            import requests, urllib.parse
            ai_prompt = f"epic cinematic mystery background {category} 8k resolution, photorealistic"
            encoded_prompt = urllib.parse.quote(ai_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&seed={random.randint(1000, 99999)}"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                temp_img = os.path.join(ASSETS_DIR, f"fallback_{random.randint(1000,9999)}.jpg")
                with open(temp_img, "wb") as f:
                    f.write(r.content)
                from moviepy.editor import ImageClip
                img_c = ImageClip(temp_img)
                img_c = img_c.resize(height=height)
                main_visual = set_dur(img_c, voiceover_duration)
                if os.path.exists(temp_img):
                    os.remove(temp_img)
            else:
                main_visual = set_dur(ColorClip(size=(width, height), color=(15, 23, 42)), voiceover_duration)
        except Exception:
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

    # 4.5. Burned-in subtitles (Top for shorts, Bottom for long videos)
    if scenes and voiceover_duration > 0:
        subtitle_clips = []
        offset = intro_duration if video_type != "short" else 0
        for idx, scene in enumerate(scenes):
            txt = scene.get("text", "")
            if not txt:
                continue
            scene_start = scene.get("start_time", 0.0)
            scene_end = scene.get("end_time", scene_start + 3.0)
            
            start_t = offset + scene_start
            if idx == 0:
                start_t = max(0.3, start_t)
            end_t = offset + scene_end
            
            try:
                sub_clip = safe_text_clip(
                    text_content=txt[:120] + ("..." if len(txt) > 120 else ""),
                    font_size=38 if video_type == "short" else 42,
                    color='white',
                    stroke_color='black',
                    stroke_width=3,
                    size=(width - 120, None)
                )
                y_pos = 220 if video_type == "short" else height - 200
                sub_clip = set_pos(sub_clip, ('center', y_pos))
                sub_clip = set_dur(sub_clip, max(0.8, end_t - start_t))
                sub_clip = set_start(sub_clip, start_t)
                subtitle_clips.append(sub_clip)
            except Exception as sub_err:
                print(f"[Note] Subtitle clip skipped for scene: {sub_err}")
        
        if subtitle_clips:
            try:
                final_visual = safe_composite_video([final_visual] + subtitle_clips, duration=final_visual.duration)
            except Exception as comp_err:
                print(f"[Note] Subtitle composition skipped: {comp_err}")

    # 5. Assemble full audio sequence
    audio_parts = []
    if video_type != "short":
        if intro_clip and intro_duration > 0:
            audio_parts.append(make_silent_clip(intro_duration))
            
    audio_parts.append(audio)
    
    if video_type == "short":
        # Add 3.5s trailing buffer for Subscribe CTA so voiceover never cuts off
        audio_parts.append(make_silent_clip(3.5))
    
    if video_type != "short":
        if outro_clip and outro_duration > 0:
            audio_parts.append(make_silent_clip(outro_duration))
        
    final_audio_voice = concatenate_audioclips(audio_parts)
    total_duration = final_audio_voice.duration

    if video_type == "short":
        max_short_duration = 58.0
        if total_duration > max_short_duration:
            print(f"[Info] Short total duration ({total_duration:.2f}s) exceeds {max_short_duration}s. Trimming to {max_short_duration}s.")
            total_duration = max_short_duration
    else:
        max_short_duration = total_duration

    # Ensure final_visual matches total_duration (extend last frame if needed)
    if final_visual.duration < total_duration:
        diff = total_duration - final_visual.duration
        try:
            last_frame = trim_clip(final_visual, final_visual.duration - 0.1, final_visual.duration)
            last_frame = set_dur(last_frame, diff)
            final_visual = concatenate_videoclips([final_visual, last_frame])
        except:
            pass

    # Strictly trim final_visual and final_audio_voice to total_duration
    final_visual = set_dur(trim_clip(final_visual, 0, total_duration), total_duration)
    final_audio_voice = set_dur(trim_clip(final_audio_voice, 0, total_duration), total_duration)

    # (Title watermark overlay removed to keep video clean and professional)

    # 6b. Add visual "SUBSCRIBE" reminder overlay during the final seconds (No chime audio)
    try:
        if total_duration > 6.0:
            sub_start = max(3.0, total_duration - 5.0)
            sub_reminder_clip = safe_text_clip(text_content="🔔 SUBSCRIBE FOR MORE", font_size=40, color='yellow', stroke_color='black', stroke_width=2)
            sub_reminder_clip = set_dur(sub_reminder_clip, min(5.0, total_duration - sub_start))
            sub_reminder_clip = set_start(sub_reminder_clip.set_position(('center', height - 280)), sub_start)
            final_visual = set_dur(safe_composite_video([final_visual, sub_reminder_clip], duration=total_duration), total_duration)
    except Exception as e:
        print(f"[Note] Subscribe reminder clip skipped: {e}")

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
            final_audio = set_dur(safe_composite_audio([final_audio_voice, bgm_clip], duration=total_duration), total_duration)
        except Exception as e:
            print(f"[Warning] BGM mixing skipped: {e}")

    # Final strict enforcement of total_duration on visual and audio
    final_visual = set_dur(trim_clip(final_visual, 0, total_duration), total_duration)
    final_audio = set_dur(trim_clip(final_audio, 0, total_duration), total_duration)

    final_composite = set_dur(trim_clip(set_aud(final_visual, final_audio), 0, total_duration), total_duration)
    
    target_bitrate = "8000k" if video_type != "short" else "4000k"
    
    scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p"

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
            '-vf', scale_filter,
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
