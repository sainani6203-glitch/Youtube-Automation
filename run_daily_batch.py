import time
import datetime
from main import run_pipeline
from generate_default_bgm import create_default_bgm
from script_generator import generate_fresh_topic
from config import TOPIC_SCHEDULE, DEFAULT_LANGUAGE

def run_daily_batch():
    print("==================================================")
    print("🌟 Starting OmniDaily Daily Batch Generation")
    print("==================================================")

    # Ensure default BGM exists
    create_default_bgm()

    # Determine today's fresh topic based on category
    weekday = datetime.datetime.now().weekday()
    category_theme = TOPIC_SCHEDULE.get(weekday, "Incredible Mysteries and Science Facts")
    print(f"📂 Today's Category: {category_theme}")
    
    try:
        today_topic = generate_fresh_topic(category_theme, DEFAULT_LANGUAGE)
        print(f"🎯 Generated Fresh Topic: {today_topic}")
    except Exception as e:
        print(f"[Warning] Fresh topic generation failed, using category theme: {e}")
        today_topic = category_theme

    # 1. Generate Daily Long Video First and capture its URL
    print(f"\n--- Generating Daily Long Video: {today_topic} ---")
    long_url = None
    try:
        long_url = run_pipeline(video_type="long", custom_topic=today_topic)
        if not long_url:
            raise Exception("Long video pipeline returned no URL (upload or render failed).")
    except Exception as e:
        print(f"[Error] Long video failed: {e}")
        import sys
        sys.exit(1)

    print("\nWaiting 60 seconds before next video...\n")
    time.sleep(60)

    # 2. Generate First Short (linked to long video)
    print(f"\n--- Generating Morning Short: {today_topic} ---")
    try:
        short1_res = run_pipeline(video_type="short", custom_topic=today_topic, linked_long_video_url=long_url)
        if not short1_res:
            raise Exception("Morning short pipeline failed.")
    except Exception as e:
        print(f"[Error] Morning short failed: {e}")
        import sys
        sys.exit(1)

    print("\nWaiting 60 seconds before next video...\n")
    time.sleep(60)

    # 3. Generate Second Short (linked to long video)
    print(f"\n--- Generating Afternoon Short: {today_topic} ---")
    try:
        short2_res = run_pipeline(video_type="short", custom_topic=today_topic, linked_long_video_url=long_url)
        if not short2_res:
            raise Exception("Afternoon short pipeline failed.")
    except Exception as e:
        print(f"[Error] Afternoon short failed: {e}")
        import sys
        sys.exit(1)
        
    print("==================================================")
    print("✅ OmniDaily Daily Batch Completed Successfully!")
    print("==================================================")

if __name__ == "__main__":
    run_daily_batch()
