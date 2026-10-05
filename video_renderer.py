import os
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips, AudioClip, concatenate_audioclips, CompositeAudioClip
from config import ASSETS_DIR

def render_video(audio_path: str, video_clips_paths: list, output_path: str, video_type: str = "short", title_text: str = "", category: str = ""):
    """
    Renders the final video by combining audio voiceover, stock video clips, captions, intro, and outro.
    video_type: 'short' (9:16 vertical, 1080x1920) or 'long' (16:9 horizontal, 1920x1080)
    """
    audio = AudioFileClip(audio_path)
    voiceover_duration = audio.duration
    
    width, height = (1080, 1920) if video_type == "short" else (1920, 1080)
    
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

    # 4. Assemble full visual sequence (Intro -> Main -> Outro)
    sequence_visuals = []
    if intro_clip:
        sequence_visuals.append(intro_clip)
    sequence_visuals.append(main_visual)
    if outro_clip:
        sequence_visuals.append(outro_clip)
        
    final_visual = concatenate_videoclips(sequence_visuals)

    # 5. Assemble full audio sequence (Silence for intro -> Voiceover -> Silence for outro)
    audio_parts = []
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
            txt_clip = TextClip(title_text, fontsize=50, color='white', font='Arial-Bold', bg_color='rgba(0,0,0,0.6)', size=(width - 100, None))
            txt_clip = txt_clip.set_position(('center', 150)).set_duration(total_duration)
            final_visual = CompositeVideoClip([final_visual, txt_clip])
        except Exception as e:
            print(f"[Note] TextClip skipped: {e}")

    # 7. Select category-matched background music from assets/
    bgm_filename = "bgm.mp3"
    if "Dark Psychology" in category:
        bgm_filename = "bgm_dark_psychology.mp3"
    elif "Ancient Indian" in category:
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
                bgm_clip = bgm_clip.with_volume_scaled(0.22)
            except AttributeError:
                bgm_clip = bgm_clip.volumex(0.22)
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
    if intro_clip: intro_clip.close()
    if outro_clip: outro_clip.close()
    if bgm_clip: bgm_clip.close()
    final_composite.close()
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
