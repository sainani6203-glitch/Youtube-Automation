import os
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
from config import ASSETS_DIR

def render_video(audio_path: str, video_clips_paths: list, output_path: str, video_type: str = "short", title_text: str = ""):
    """
    Renders the final video by combining audio voiceover, stock video clips, and captions.
    video_type: 'short' (9:16 vertical, 1080x1920) or 'long' (16:9 horizontal, 1920x1080)
    """
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    width, height = (1080, 1920) if video_type == "short" else (1920, 1080)
    
    clips = []
    # If valid video clips exist, use them; otherwise use a professional dark background clip
    valid_clips = [p for p in video_clips_paths if p and os.path.exists(p)]
    
    if valid_clips:
        # Load and loop/resize clips to match duration
        sub_clips = []
        clip_duration = duration / len(valid_clips)
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
                # Resize and crop to target resolution
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
            # Ensure final_visual matches required audio duration
            while True:
                final_visual = concatenate_videoclips(sub_clips)
                if final_visual.duration >= duration or len(sub_clips) > 20:
                    break
                sub_clips.extend(sub_clips)
            
            try:
                final_visual = final_visual.subclipped(0, duration)
            except AttributeError:
                final_visual = final_visual.subclip(0, duration)
            clips.append(final_visual)
            
    if not clips:
        # Fallback background clip
        bg_clip = ColorClip(size=(width, height), color=(20, 24, 33))
        try:
            bg_clip = bg_clip.with_duration(duration)
        except AttributeError:
            bg_clip = bg_clip.set_duration(duration)
        clips.append(bg_clip)
        
    # Add optional title watermark / caption banner
    if title_text:
        try:
            txt_clip = TextClip(title_text, fontsize=50, color='white', font='Arial-Bold', bg_color='rgba(0,0,0,0.6)', size=(width - 100, None))
            txt_clip = txt_clip.set_position(('center', 150)).set_duration(duration)
            clips.append(txt_clip)
        except Exception as e:
            print(f"[Note] TextClip skipped (ImageMagick might not be installed): {e}")
            
    # Check for background music in assets/bgm.mp3
    bgm_path = os.path.join(ASSETS_DIR, "bgm.mp3")
    final_audio = audio
    bgm_clip = None
    if os.path.exists(bgm_path):
        try:
            from moviepy import CompositeAudioClip, concatenate_audioclips
            bgm_clip = AudioFileClip(bgm_path)
            if bgm_clip.duration < duration:
                repeats = int(duration // bgm_clip.duration) + 1
                bgm_clip = concatenate_audioclips([bgm_clip] * repeats)
            try:
                bgm_clip = bgm_clip.subclipped(0, duration)
            except AttributeError:
                bgm_clip = bgm_clip.subclip(0, duration)
            try:
                bgm_clip = bgm_clip.with_volume_scaled(0.12)
            except AttributeError:
                bgm_clip = bgm_clip.volumex(0.12)
            final_audio = CompositeAudioClip([audio, bgm_clip])
        except Exception as e:
            print(f"[Warning] BGM mixing skipped: {e}")

    # Combine visual with final audio (voiceover + optional bgm)
    try:
        final_composite = CompositeVideoClip(clips).with_audio(final_audio)
    except AttributeError:
        final_composite = CompositeVideoClip(clips).set_audio(final_audio)
    
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
    if bgm_clip:
        bgm_clip.close()
    final_composite.close()
    print(f"[Success] Video successfully rendered at: {output_path}")
    return output_path

if __name__ == "__main__":
    print("Testing Video Renderer...")
    # Quick test with audio only fallback
    from tts_engine import create_voiceover_sync
    test_audio = "test_render_audio.mp3"
    create_voiceover_sync("This is a test video rendering check.", test_audio)
    render_video(test_audio, [], "test_output.mp4", "short", "Smart Tech Tip")
    if os.path.exists(test_audio): os.remove(test_audio)
    if os.path.exists("test_output.mp4"): os.remove("test_output.mp4")
