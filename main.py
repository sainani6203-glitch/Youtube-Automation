import os
import datetime
import json
from config import TOPIC_SCHEDULE, READY_TO_REVIEW_DIR, AUTOMATION_MODE, DEFAULT_LANGUAGE, CATEGORY_PLAYLISTS
from script_generator import generate_video_script, generate_fresh_topic
from tts_engine import create_voiceover_sync
from media_fetcher import fetch_stock_video
from video_renderer import render_video
from youtube_uploader import upload_video_to_youtube, upload_caption, upload_thumbnail, add_video_to_playlist
from thumbnail_generator import generate_thumbnail
from moviepy import AudioFileClip

def generate_srt(scenes, audio_duration, srt_path):
    total_chars = sum(len(scene.get("text", "")) for scene in scenes)
    if total_chars == 0:
        total_chars = len(scenes) * 10
        
    current_time = 0.0
    srt_lines = []
    
    for i, scene in enumerate(scenes, 1):
        text = scene.get("text", "")
        fraction = len(text) / total_chars if total_chars > 0 else 1.0 / len(scenes)
        scene_duration = max(2.0, audio_duration * fraction)
        
        start_time = current_time
        end_time = min(audio_duration, current_time + scene_duration)
        current_time = end_time
        
        def format_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
            
        srt_lines.append(f"{i}\n{format_time(start_time)} --> {format_time(end_time)}\n{text}\n")
        
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    return srt_path

def run_pipeline(video_type: str = "short", custom_topic: str = None, language: str = DEFAULT_LANGUAGE, linked_long_video_url: str = None, short_angle: str = "shocking_fact"):
    """
    Runs the automated video generation pipeline for a given video type ('short' or 'long') and language.
    """
    print("==================================================")
    print(f"🚀 Starting YouTube Automation Pipeline ({video_type.upper()} | {language})")
    print("==================================================")
    
    weekday = datetime.datetime.now().weekday()
    category_theme = TOPIC_SCHEDULE.get(weekday, "Incredible Mysteries and Science Facts")

    # 1. Determine Topic based on Day of Week or Custom Topic
    if custom_topic:
        topic = custom_topic
    else:
        print(f"📂 Today's Category: {category_theme}")
        try:
            topic = generate_fresh_topic(category_theme, language)
        except Exception as e:
            print(f"[Warning] Fresh topic generation failed: {e}")
            topic = category_theme
        
    print(f"🎯 Selected Topic for today: '{topic}'")
    
    # 2. Generate Script & Metadata via Gemini
    print(f"🤖 Step 1/4: Generating AI Script & Metadata ({language})...")
    try:
        script_data = generate_video_script(topic, video_type, language, linked_long_video_url, short_angle)
        print(f"   -> Title: {script_data.get('title')}")
        print(f"   -> Scenes count: {len(script_data.get('scenes', []))}")
    except Exception as e:
        print(f"[Error] Failed to generate script: {e}")
        return None

    # 3. Generate Voiceover Audio via TTS
    print(f"🎙️ Step 2/4: Synthesizing Voiceover Audio ({language})...")
    full_text = " ".join([scene["text"] for scene in script_data.get("scenes", [])])
    audio_filename = f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    audio_path = os.path.join(READY_TO_REVIEW_DIR, audio_filename)
    try:
        create_voiceover_sync(full_text, audio_path, language)
        print(f"   -> Audio saved: {audio_path}")
    except Exception as e:
        print(f"[Error] Failed to generate voiceover: {e}")
        return

    # Generate SRT Subtitles file
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    srt_filename = f"captions_{timestamp}.srt"
    srt_path = os.path.join(READY_TO_REVIEW_DIR, srt_filename)
    try:
        audio_clip_obj = AudioFileClip(audio_path)
        audio_duration = audio_clip_obj.duration
        audio_clip_obj.close()
        generate_srt(script_data.get("scenes", []), audio_duration, srt_path)
        print(f"   -> Subtitles SRT saved: {srt_path}")
    except Exception as e:
        print(f"[Warning] Failed to generate SRT: {e}")

    # 4. Fetch Stock Video Clips for each scene
    print("🎬 Step 3/4: Fetching Stock Footage from Pexels...")
    video_clips_paths = []
    orientation = "portrait" if video_type == "short" else "landscape"
    
    for i, scene in enumerate(script_data.get("scenes", [])):
        keyword = scene.get("visual_keyword", topic)
        clip_filename = f"clip_{i}_{timestamp}.mp4"
        print(f"   -> Fetching clip for keyword: '{keyword}'")
        clip_path = fetch_stock_video(keyword, orientation, clip_filename)
        if clip_path:
            video_clips_paths.append(clip_path)

    # 5. Render Final Video
    print("⚙️ Step 4/4: Rendering Final Video...")
    video_filename = f"YouTube_{video_type.capitalize()}_{timestamp}.mp4"
    final_video_path = os.path.join(READY_TO_REVIEW_DIR, video_filename)
    
    # Save metadata JSON alongside the video
    meta_filename = f"YouTube_{video_type.capitalize()}_{timestamp}.json"
    meta_path = os.path.join(READY_TO_REVIEW_DIR, meta_filename)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2)

    try:
        render_video(
            audio_path=audio_path,
            video_clips_paths=video_clips_paths,
            output_path=final_video_path,
            video_type=video_type,
            title_text=script_data.get("title"),
            category=category_theme
        )
        print("==================================================")
        print(f"✅ Video rendered successfully!")
        print(f"   📁 File: {video_filename}")
        
        # Check automation mode
        if "fully" in AUTOMATION_MODE.lower():
            print("🚀 Fully-automated mode detected. Uploading directly to YouTube...")
            desc = script_data.get("description", "")
            if linked_long_video_url:
                desc += f"\n\n🔗 Watch the full detailed video here: {linked_long_video_url}"
                
            video_id = upload_video_to_youtube(
                video_path=final_video_path,
                title=script_data.get("title"),
                description=desc,
                privacy_status="public"
            )
            
            # Add video to category playlist automatically (Long videos only)
            if video_id and video_type == "long":
                category_theme = TOPIC_SCHEDULE.get(datetime.datetime.now().weekday(), "")
                playlist_id = CATEGORY_PLAYLISTS.get(category_theme, "")
                if playlist_id and "REPLACE_WITH" not in playlist_id:
                    add_video_to_playlist(video_id, playlist_id)
                else:
                    print(f"[Note] Playlist ID for category '{category_theme}' not configured in config.py.")

            # Upload Subtitles / Captions (.srt) to YouTube
            if video_id and os.path.exists(srt_path):
                lang_code = {"english": "en", "telugu": "te", "hindi": "hi"}.get(language.lower(), "en")
                upload_caption(video_id, srt_path, lang_code)

            # Generate and upload Custom Thumbnail for Long Videos
            thumb_path = None
            if video_id and video_type == "long":
                import time
                print("⏳ Waiting 15 seconds for video processing before uploading thumbnail...")
                time.sleep(15)
                thumb_path = generate_thumbnail(script_data.get("title"))
                upload_thumbnail(video_id, thumb_path)

            # Auto-delete local files to save storage
            if video_id:
                print("🧹 Cleaning up local storage (deleting local video, audio, metadata, and subtitle files)...")
                files_to_clean = [final_video_path, meta_path, audio_path, srt_path]
                if thumb_path:
                    files_to_clean.append(thumb_path)
                for p in files_to_clean:
                    if p and os.path.exists(p):
                        try:
                            os.remove(p)
                            print(f"   -> Deleted local file: {os.path.basename(p)}")
                        except Exception as e:
                            print(f"[Warning] Could not delete {p}: {e}")
                            
                return f"https://youtu.be/{video_id}"
        else:
            print(f"🛡️ Mode: SEMI-AUTOMATED. Video saved in: {READY_TO_REVIEW_DIR}")
            print("   (To enable 100% auto-upload, set AUTOMATION_MODE=fully-automated in .env)")
        print("==================================================")
    except Exception as e:
        print(f"[Error] Failed to render or upload video: {e}")
    return None

if __name__ == "__main__":
    import sys
    v_type = "short"
    custom_t = None
    lang_arg = DEFAULT_LANGUAGE
    if len(sys.argv) > 1:
        v_type = sys.argv[1] # 'short' or 'long'
    if len(sys.argv) > 2:
        custom_t = sys.argv[2]
    if len(sys.argv) > 3:
        lang_arg = sys.argv[3]
        
    run_pipeline(video_type=v_type, custom_topic=custom_t, language=lang_arg)
