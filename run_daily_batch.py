import time
from main import run_pipeline
from generate_default_bgm import create_default_bgm

def run_daily_batch():
    print("==================================================")
    print("🌟 Starting OmniDaily Daily Batch Generation")
    print("==================================================")

    # Ensure default BGM exists
    create_default_bgm()

    # 1. Generate Daily Long Video First and capture its URL
    print("\n--- Generating Daily Long Video ---")
    long_url = None
    try:
        long_url = run_pipeline(video_type="long")
    except Exception as e:
        print(f"[Error] Long video failed: {e}")

    print("\nWaiting 60 seconds before next video...\n")
    time.sleep(60)

    # 2. Generate First Short (linked to long video)
    print("\n--- Generating Morning Short ---")
    try:
        run_pipeline(video_type="short", linked_long_video_url=long_url)
    except Exception as e:
        print(f"[Error] Morning short failed: {e}")

    print("\nWaiting 60 seconds before next video...\n")
    time.sleep(60)

    # 3. Generate Second Short (linked to long video)
    print("\n--- Generating Afternoon Short ---")
    try:
        run_pipeline(video_type="short", linked_long_video_url=long_url)
    except Exception as e:
        print(f"[Error] Afternoon short failed: {e}")
        
    print("==================================================")
    print("✅ OmniDaily Daily Batch Completed Successfully!")
    print("==================================================")

if __name__ == "__main__":
    run_daily_batch()
