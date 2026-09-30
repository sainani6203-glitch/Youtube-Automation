import time
from main import run_pipeline
def run_daily_batch():
    print("==================================================")
    print("🌟 Starting OmniDaily Daily Batch Generation")
    print("==================================================")

    # 1. Generate Daily Long Video First
    print("\n--- Generating Daily Long Video ---")
    try:
        run_pipeline(video_type="long")
    except Exception as e:
        print(f"[Error] Long video failed: {e}")

    print("\nWaiting 60 seconds before next video...\n")
    time.sleep(60)

    # 2. Generate First Short
    print("\n--- Generating Morning Short ---")
    try:
        run_pipeline(video_type="short")
    except Exception as e:
        print(f"[Error] Morning short failed: {e}")

    print("\nWaiting 60 seconds before next video...\n")
    time.sleep(60)

    # 3. Generate Second Short
    print("\n--- Generating Afternoon Short ---")
    try:
        run_pipeline(video_type="short")
    except Exception as e:
        print(f"[Error] Afternoon short failed: {e}")
        
    print("==================================================")
    print("✅ OmniDaily Daily Batch Completed Successfully!")
    print("==================================================")

if __name__ == "__main__":
    run_daily_batch()
