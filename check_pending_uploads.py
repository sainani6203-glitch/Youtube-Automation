import os
import json
import datetime
from config import BASE_DIR
from youtube_uploader import get_video_status

def verify_and_cleanup_pending():
    pending_file = os.path.join(BASE_DIR, "pending_uploads.json")
    if not os.path.exists(pending_file):
        print("📭 No pending uploads to check.")
        return

    try:
        with open(pending_file, "r") as f:
            pending_data = json.load(f)
    except Exception as e:
        print(f"[Error] Could not read pending_uploads.json: {e}")
        return

    if not pending_data:
        print("📭 pending_uploads.json is empty.")
        return

    print(f"🔍 Checking status of {len(pending_data)} pending video(s)...")
    remaining_pending = []
    now = datetime.datetime.now()

    for item in pending_data:
        video_id = item.get("video_id")
        language = item.get("language", "Telugu")
        timestamp_str = item.get("timestamp")
        files = item.get("files", [])

        # Check age of the entry
        is_expired = False
        if timestamp_str:
            try:
                entry_time = datetime.datetime.fromisoformat(timestamp_str)
                if (now - entry_time).total_seconds() > 48 * 3600: # 48 hours
                    is_expired = True
            except:
                pass

        if not video_id:
            continue

        status = get_video_status(video_id, language=language)
        print(f"   -> Video {video_id} ({language}): Status = {status}")

        if status == "processed" or is_expired:
            if is_expired and status != "processed":
                print(f"⚠️ Video {video_id} expired (>48 hrs) without 'processed' status. Forcing cleanup.")
            else:
                print(f"✅ Video {video_id} successfully processed on YouTube. Cleaning up local files...")

            for p in files:
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                        print(f"      Deleted: {os.path.basename(p)}")
                    except Exception as e:
                        print(f"      [Warning] Could not delete {p}: {e}")
        else:
            # Keep for next check (still processing, uploaded, or failed)
            print(f"⏳ Video {video_id} is still '{status}'. Preserving local files.")
            remaining_pending.append(item)

    with open(pending_file, "w") as f:
        json.dump(remaining_pending, f, indent=4)
    print(f"✨ Pending uploads check complete. {len(remaining_pending)} video(s) still remaining in queue.")

if __name__ == "__main__":
    verify_and_cleanup_pending()
