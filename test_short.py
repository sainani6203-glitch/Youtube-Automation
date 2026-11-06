from main import run_pipeline
import os

def main():
    print("🚀 Starting Fresh Test Short with optimized FFmpeg settings...")
    try:
        run_pipeline(video_type='short', language='Telugu', custom_topic='Space Hidden Secrets')
        print("✅ Test Short completed successfully!")
    except Exception as e:
        print(f"❌ Test Short failed: {e}")

if __name__ == '__main__':
    main()
