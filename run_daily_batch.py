import time
import datetime
from main import run_pipeline
from generate_default_bgm import create_default_bgm
from script_generator import generate_fresh_topic
from config import TOPIC_SCHEDULE, DEFAULT_LANGUAGE

def run_daily_batch():
    print("==================================================")
    print("🌟 Starting OmniDaily 5-Shorts & Long Daily Batch")
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

    # 1. Generate Daily Long Video First (Published at 3:30 PM IST) and capture its URL
    print(f"\n--- Generating Daily Long Video: {today_topic} ---")
    long_url = None
    try:
        long_url = run_pipeline(video_type="long", custom_topic=today_topic)
        if not long_url:
            raise Exception("Long video pipeline returned no URL (upload or render failed).")
        print(f"[Success] Long video published successfully: {long_url}")
    except Exception as e:
        print(f"[Error] Long video failed: {e}")
        import sys
        sys.exit(1)

    # Spacing interval between shorts (10 minutes = 600 seconds)
    SHORT_SPACING_SECONDS = 600

    # 5 Short Angles for maximum variety and retention
    short_angles = [
        "shocking_fact",
        "hidden_truth",
        "unsolved_mystery",
        "bizarre_experiment",
        "deep_paradox"
    ]

    # 2. Generate and upload 5 Shorts linked to the Long Video, spaced across the afternoon/evening
    for i, angle in enumerate(short_angles, 1):
        print(f"\nWaiting {SHORT_SPACING_SECONDS // 60} minutes before uploading Short {i}/5 ({angle})...\n")
        time.sleep(SHORT_SPACING_SECONDS)

        print(f"--- Generating Short {i}/5 [{angle}]: {today_topic} ---")
        try:
            short_res = run_pipeline(
                video_type="short",
                custom_topic=today_topic,
                linked_long_video_url=long_url,
                short_angle=angle
            )
            if not short_res:
                print(f"[Warning] Short {i} pipeline returned no result, but continuing batch...")
            else:
                print(f"[Success] Short {i}/5 published successfully.")
        except Exception as e:
            print(f"[Error] Short {i}/5 failed: {e}")
            # Continue with remaining shorts even if one fails
            continue

    print("==================================================")
    print("✅ OmniDaily Daily Batch (1 Long + 5 Shorts) Completed!")
    print("==================================================")

if __name__ == "__main__":
    run_daily_batch()
