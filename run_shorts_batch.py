import time
import datetime
import os
from main import run_pipeline
from generate_default_bgm import create_default_bgm
from script_generator import generate_fresh_topic
from config import TOPIC_SCHEDULE, LANGUAGES
from monitor_uploads import monitor_and_cleanup

def run_shorts_only_batch():
    print("==================================================")
    print(f"🌟 Starting Shorts-Only Daily Batch Across Languages: {LANGUAGES}")
    print("==================================================")

    monitor_and_cleanup()
    create_default_bgm()

    weekday = datetime.datetime.now().weekday()
    category_theme = TOPIC_SCHEDULE.get(weekday, "Incredible Mysteries and Science Facts")
    print(f"📂 Today's Category: {category_theme}")

    for idx, language in enumerate(LANGUAGES):
        if idx > 0:
            print("\n⏳ Pausing 5 minutes before switching to next language batch...")
            time.sleep(300)

        print(f"\n==================================================")
        print(f"🌍 Processing Language Batch (Shorts Only): {language}")
        print(f"==================================================")
        
        try:
            today_topic = generate_fresh_topic(category_theme, language)
            print(f"🎯 Generated Fresh Topic ({language}): {today_topic}")
        except Exception as e:
            print(f"[Warning] Fresh topic generation failed for {language}: {e}")
            today_topic = category_theme

        short_angles = [
            "shocking_fact",
            "hidden_truth"
        ]

        for i, angle in enumerate(short_angles, 1):
            print(f"\n--- Generating Short {i}/2 [{angle}] ({language}): {today_topic} ---\n")
            try:
                short_res = run_pipeline(
                    video_type="short",
                    custom_topic=today_topic,
                    language=language,
                    short_angle=angle
                )
                if not short_res:
                    print(f"[Warning] Short {i} pipeline for {language} returned no result.")
                else:
                    print(f"[Success] Short {i}/2 published successfully ({language}).")
            except Exception as e:
                print(f"[Error] Short {i}/2 failed for {language}: {e}")
                continue
            time.sleep(30)

    print("==================================================")
    print("✅ Shorts-Only Multi-Language Daily Batch Completed!")
    print("==================================================")

if __name__ == "__main__":
    run_shorts_only_batch()
