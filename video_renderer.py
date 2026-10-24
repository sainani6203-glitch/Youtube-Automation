import os
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip, concatenate_videoclips, AudioClip, concatenate_audioclips, CompositeAudioClip
from config import ASSETS_DIR
from thumbnail_generator import generate_thumbnail

def render_video(audio_path: str, video_clips_paths: list, output_path: str, video_type: str = "short", title_text: str = "", category: str = "", scenes: list = None):
    """
    Renders the final video by combining audio voiceover, stock video clips, captions, intro, and outro.
    video_type: 'short' (9:16 vertical, 1080x1920) or 'long' (16:9 horizontal, 1920x1080)
    """
    audio = AudioFileClip(audio_path)
    voiceover_duration = audio.duration
    
    width, height = (1080, 1920) if video_type == "short" else (1920, 1080)
    
    # 0. Generate Thumbnail file. For YouTube Shorts, also add it as the first 2 seconds intro frame.
    thumb_path = None
    thumb_clip = None
    thumb_duration = 0.0
    if title_text:
        try:
            is_vertical = (video_type == "short")
            thumb_path = generate_thumbnail(title_text, category=category, vertical=is_vertical)
            if video_type == "short" and thumb_path and os.path.exists(thumb_path):
                thumb_clip = ImageClip(thumb_path)
                try:
                    thumb_clip = thumb_clip.resized(height=height)
                except AttributeError:
                    thumb_clip = thumb_clip.resize(height=height)
                if thumb_clip.w < width:
                    try:
                        thumb_clip = thumb_clip.resized(width=width)
                    except AttributeError:
                        thumb_clip = thumb_clip.resize(width=width)
                try:
                    thumb_clip = thumb_clip.cropped(x_center=thumb_clip.w/2, y_center=thumb_clip.h/2, width=width, height=height)
                except AttributeError:
                    thumb_clip = thumb_clip.crop(x_center=thumb_clip.w/2, y_center=thumb_clip.h/2, width=width, height=height)
                
                thumb_duration = 2.0
                try:
                    thumb_clip = thumb_clip.with_duration(thumb_duration)
                except AttributeError:
                    thumb_clip = thumb_clip.set_duration(thumb_duration)
        except Exception as e:
            print(f"[Warning] Could not generate/load thumbnail intro clip: {e}")
            thumb_clip = None
            thumb_duration = 0.0

    # 1. Check for custom intro in assets/intro.mp4
    intro_path = os.path.join(ASSETS_DIR, "intro.mp4")
    intro_clip = None
    intro_duration = 0
    if os.path.exists(intro_path):
        try:
            intro_clip = VideoFileClip(intro_path)
            intro_duration = intro_clip.duration
            try:
                intro_clip = intro_clip.resized(height=height)
            except AttributeError:
                intro_clip = intro_clip.resize(height=height)
            if intro_clip.w < width:
                try:
                    intro_clip = intro_clip.resized(width=width)
                except AttributeError:
                    intro_clip = intro_clip.resize(width=width)
            try:
                intro_clip = intro_clip.cropped(x_center=intro_clip.w/2, y_center=intro_clip.h/2, width=width, height=height)
            except AttributeError:
                intro_clip = intro_clip.crop(x_center=intro_clip.w/2, y_center=intro_clip.h/2, width=width, height=height)
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
            try:
                outro_clip = outro_clip.resized(height=height)
            except AttributeError:
                outro_clip = outro_clip.resize(height=height)
            if outro_clip.w < width:
                try:
                    outro_clip = outro_clip.resized(width=width)
                except AttributeError:
                    outro_clip = outro_clip.resize(width=width)
            try:
                outro_clip = outro_clip.cropped(x_center=outro_clip.w/2, y_center=outro_clip.h/2, width=width, height=height)
            except AttributeError:
                outro_clip = outro_clip.crop(x_center=outro_clip.w/2, y_center=outro_clip.h/2, width=width, height=height)
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
                try:
                    if c.duration < clip_duration:
                        repeats = int(clip_duration // c.duration) + 1
                        c = concatenate_videoclips([c] * repeats).subclipped(0, clip_duration)
                    else:
                        c = c.subclipped(0, clip_duration)
                except AttributeError:
                    try:
                        if c.duration < clip_duration:
                            repeats = int(clip_duration // c.duration) + 1
                            c = concatenate_videoclips([c] * repeats).subclip(0, clip_duration)
                        else:
                            c = c.subclip(0, clip_duration)
                    except Exception:
                        c = c.subclip(0, min(clip_duration, c.duration))
                
                try:
                    c = c.resized(height=height)
                except AttributeError:
                    c = c.resize(height=height)
                if c.w < width:
                    try:
                        c = c.resized(width=width)
                    except AttributeError:
                        c = c.resize(width=width)
                try:
                    c = c.cropped(x_center=c.w/2, y_center=c.h/2, width=width, height=height)
                except AttributeError:
                    c = c.crop(x_center=c.w/2, y_center=c.h/2, width=width, height=height)
                sub_clips.append(c)
            except Exception as e:
                print(f"[Warning] Error loading clip {path}: {e}")
                
    if sub_clips:
        while True:
            main_visual = concatenate_videoclips(sub_clips)
            if main_visual.duration >= voiceover_duration or len(sub_clips) > 20:
                break
            sub_clips.extend(sub_clips)
        try:
            main_visual = main_visual.subclipped(0, voiceover_duration)
        except AttributeError:
            main_visual = main_visual.subclip(0, voiceover_duration)
    else:
        main_visual = ColorClip(size=(width, height), color=(20, 24, 33))
        try:
            main_visual = main_visual.with_duration(voiceover_duration)
        except AttributeError:
            main_visual = main_visual.set_duration(voiceover_duration)

    # 4. Assemble full visual sequence (Thumbnail -> Intro -> Main -> Outro)
    sequence_visuals = []
    if thumb_clip:
        sequence_visuals.append(thumb_clip)
    if intro_clip:
        sequence_visuals.append(intro_clip)
    sequence_visuals.append(main_visual)
    if outro_clip:
        sequence_visuals.append(outro_clip)
        
    final_visual = concatenate_videoclips(sequence_visuals)

    # 4.5. Add dynamic burned-in subtitle/caption overlays for each scene so viewers never get bored
    if scenes and voiceover_duration > 0:
        subtitle_clips = []
        offset = thumb_duration + intro_duration
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
                )
                try:
                    sub_clip = sub_clip.with_position(('center', height - 400 if video_type == "short" else height - 220)).with_start(start_t).with_duration(max(0.5, end_t - start_t))
                except AttributeError:
                    sub_clip = sub_clip.set_position(('center', height - 400 if video_type == "short" else height - 220)).set_start(start_t).set_duration(max(0.5, end_t - start_t))
                subtitle_clips.append(sub_clip)
            except Exception as sub_err:
                print(f"[Note] Subtitle clip skipped for scene: {sub_err}")
        
        if subtitle_clips:
            try:
                final_visual = CompositeVideoClip([final_visual] + subtitle_clips)
            except Exception as comp_err:
                print(f"[Note] Subtitle composition skipped: {comp_err}")

    # 5. Assemble full audio sequence (Silence for thumbnail -> Silence for intro -> Voiceover -> Silence for outro)
    audio_parts = []
    if thumb_clip and thumb_duration > 0:
        audio_parts.append(AudioClip(lambda t: [0, 0], duration=thumb_duration))
    if intro_clip and intro_duration > 0:
        audio_parts.append(AudioClip(lambda t: [0, 0], duration=intro_duration))
    audio_parts.append(audio)
    if outro_clip and outro_duration > 0:
        audio_parts.append(AudioClip(lambda t: [0, 0], duration=outro_duration))
        
    final_audio_voice = concatenate_audioclips(audio_parts)
    total_duration = final_audio_voice.duration

    # 6. Add optional title watermark on main visual
    if title_text:
        try:
            txt_clip = TextClip(text=title_text, font_size=50, color='white', stroke_color='black', stroke_width=2, size=(width - 100, None))
            try:
                txt_clip = txt_clip.with_position(('center', 150)).with_duration(total_duration)
            except AttributeError:
                txt_clip = txt_clip.set_position(('center', 150)).set_duration(total_duration)
            final_visual = CompositeVideoClip([final_visual, txt_clip])
        except Exception as e:
            print(f"[Note] TextClip skipped: {e}")

    # 6b. Add visual "SUBSCRIBE" reminder overlay & notification sound effect during the final seconds of the video
    try:
        sub_reminder_clip = TextClip(text="🔔 SUBSCRIBE FOR MORE", font_size=40, color='yellow', stroke_color='black', stroke_width=2)
        sub_start = max(0, total_duration - 5.0)
        try:
            sub_reminder_clip = sub_reminder_clip.with_position(('center', height - 280)).with_start(sub_start).with_duration(5.0)
        except AttributeError:
            sub_reminder_clip = sub_reminder_clip.set_position(('center', height - 280)).set_start(sub_start).set_duration(5.0)
        final_visual = CompositeVideoClip([final_visual, sub_reminder_clip])

        import numpy as np
        def make_chime(t):
            f1, f2 = 587.33, 880.00
            val1 = 0.25 * np.sin(2 * np.pi * f1 * t) * np.exp(-3 * t)
            val2 = 0.35 * np.sin(2 * np.pi * f2 * (t - 0.15)) * np.exp(-3 * (t - 0.15)) if t >= 0.15 else 0
            return [val1 + val2, val1 + val2]
        
        chime_clip = AudioClip(make_chime, duration=0.5)
        try:
            chime_clip = chime_clip.with_start(sub_start)
        except AttributeError:
            chime_clip = chime_clip.set_start(sub_start)
            
        final_audio_voice = CompositeAudioClip([final_audio_voice, chime_clip])
    except Exception as e:
        print(f"[Note] Subscribe reminder clip/audio skipped: {e}")

    # 7. Select category-matched background music from assets/
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
    if os.path.exists(bgm_path):
        try:
            bgm_clip = AudioFileClip(bgm_path)
            if bgm_clip.duration < total_duration:
                repeats = int(total_duration // bgm_clip.duration) + 1
                bgm_clip = concatenate_audioclips([bgm_clip] * repeats)
            try:
                bgm_clip = bgm_clip.subclipped(0, total_duration)
            except AttributeError:
                bgm_clip = bgm_clip.subclip(0, total_duration)
            try:
                bgm_clip = bgm_clip.with_volume_scaled(0.55)
            except AttributeError:
                bgm_clip = bgm_clip.volumex(0.55)
            final_audio = CompositeAudioClip([final_audio_voice, bgm_clip])
        except Exception as e:
            print(f"[Warning] BGM mixing skipped: {e}")

    # 8. Combine final visual and audio
    try:
        final_composite = final_visual.with_audio(final_audio)
    except AttributeError:
        final_composite = final_visual.set_audio(final_audio)
    
    # Write output file
    final_composite.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        preset='medium',
        threads=4
    )
    
    # Close clips
    audio.close()
    if thumb_clip: thumb_clip.close()
    if intro_clip: intro_clip.close()
    if outro_clip: outro_clip.close()
    if bgm_clip: bgm_clip.close()
    final_composite.close()
    
    if thumb_path and os.path.exists(thumb_path):
        try:
            os.remove(thumb_path)
        except:
            pass
            
    print(f"[Success] Video successfully rendered at: {output_path}")
    return output_path

if __name__ == "__main__":
    print("Testing Video Renderer...")
    from tts_engine import create_voiceover_sync
    test_audio = "test_render_audio.mp3"
    create_voiceover_sync("This is a test video rendering check.", test_audio)
    render_video(test_audio, [], "test_output.mp4", "short", "Smart Tech Tip")
    if os.path.exists(test_audio): os.remove(test_audio)
    if os.path.exists("test_output.mp4"): os.remove("test_output.mp4")
