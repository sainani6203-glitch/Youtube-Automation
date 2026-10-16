import time
import datetime
from main import run_pipeline
from generate_default_bgm import create_default_bgm
from script_generator import generate_fresh_topic
from config import TOPIC_SCHEDULE, LANGUAGES

def run_daily_batch():
    print("==================================================")
    print(f"🌟 Starting OmniDaily 1-Long & 5-Shorts Daily Batch Across Languages: {LANGUAGES}")
    print("==================================================")

    # Ensure default BGM exists
    create_default_bgm()

    # Determine today's fresh topic based on category
    weekday = datetime.datetime.now().weekday()
    category_theme = TOPIC_SCHEDULE.get(weekday, "Incredible Mysteries and Science Facts")
    print(f"📂 Today's Category: {category_theme}")

    for idx, language in enumerate(LANGUAGES):
        if idx > 0:
            print("\n⏳ Pausing 30 seconds before switching to next language batch to prevent TTS rate limits...")
            time.sleep(30)

        print(f"\n==================================================")
        print(f"🌍 Processing Language Batch: {language}")
        print(f"==================================================")
        
        try:
            today_topic = generate_fresh_topic(category_theme, language)
            print(f"🎯 Generated Fresh Topic ({language}): {today_topic}")
        except Exception as e:
            print(f"[Warning] Fresh topic generation failed for {language}, using category theme: {e}")
            today_topic = category_theme

        # 1. Generate Daily Long Video First (Published at 3:30 PM IST) and capture its URL
        print(f"\n--- Generating Daily Long Video ({language}): {today_topic} ---")
        long_url = None
        try:
            long_url = run_pipeline(video_type="long", custom_topic=today_topic, language=language)
            if not long_url:
                print(f"[Warning] Long video pipeline for {language} returned no URL. Continuing with shorts...")
            else:
                print(f"[Success] Long video published successfully ({language}): {long_url}")
        except Exception as e:
            print(f"[Error] Long video failed for {language}: {e}")

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

        # 2. Generate and upload 5 Shorts linked to the Long Video
        for i, angle in enumerate(short_angles, 1):
            print(f"\nWaiting {SHORT_SPACING_SECONDS // 60} minutes before uploading Short {i}/5 ({language} - {angle})...\n")
            time.sleep(SHORT_SPACING_SECONDS)

            print(f"--- Generating Short {i}/5 [{angle}] ({language}): {today_topic} ---")
            try:
                short_res = run_pipeline(
                    video_type="short",
                    custom_topic=today_topic,
                    language=language,
                    linked_long_video_url=long_url,
                    short_angle=angle
                )
                if not short_res:
                    print(f"[Warning] Short {i} pipeline for {language} returned no result, but continuing batch...")
                else:
                    print(f"[Success] Short {i}/5 published successfully ({language}).")
            except Exception as e:
                print(f"[Error] Short {i}/5 failed for {language}: {e}")
                continue

    print("==================================================")
    print("✅ OmniDaily Multi-Language Daily Batch Completed!")
    print("==================================================")

if __name__ == "__main__":
    run_daily_batch()
