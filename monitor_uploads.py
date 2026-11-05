import os
import json
import time
import datetime
from youtube_uploader import get_video_status, upload_video_to_youtube
from config import BASE_DIR

PENDING_FILE = os.path.join(BASE_DIR, "pending_uploads.json")

def monitor_and_cleanup():
    if not os.path.exists(PENDING_FILE):
        print("📭 No pending uploads to monitor.")
        return

    try:
        with open(PENDING_FILE, "r") as f:
            pending_data = json.load(f)
    except Exception as e:
        print(f"[Error] Could not read {PENDING_FILE}: {e}")
        return

    if not pending_data:
        print("📭 Pending list is empty.")
        return

    still_pending = []
    cleaned_count = 0

    print(f"🕵️ Monitoring {len(pending_data)} pending uploads...")

    for entry in pending_data:
        video_id = entry.get("video_id")
        language = entry.get("language", "Telugu")
        files = entry.get("files", [])
        retry_count = entry.get("retry_count", 0)
        upload_params = entry.get("upload_params")

        status = get_video_status(video_id, language=language)

        if status == "processed":
            print(f"✅ Video {video_id} is PROCESSED. Cleaning up local files...")
            for file_path in files:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"   -> Deleted: {os.path.basename(file_path)}")
                    except Exception as e:
                        print(f"   [Warning] Could not delete {file_path}: {e}")
            cleaned_count += 1
        elif status == "failed":
            print(f"❌ Video {video_id} FAILED processing.")
            if upload_params and retry_count < 2:
                print(f"🔄 Attempting automatic re-upload (Retry {retry_count + 1}/2)...")
                video_path = upload_params.get("video_path")
                if video_path and os.path.exists(video_path):
                    try:
                        new_video_id = upload_video_to_youtube(
                            video_path=video_path,
                            title=upload_params.get("title"),
                            description=upload_params.get("description"),
                            privacy_status=upload_params.get("privacy_status", "public"),
                            language=upload_params.get("language", "Telugu"),
                            publish_at=upload_params.get("publish_at")
                        )
                        if new_video_id:
                            print(f"[Success] Re-upload successful! New Video ID: {new_video_id}")
                            entry["video_id"] = new_video_id
                            entry["retry_count"] = retry_count + 1
                            entry["timestamp"] = datetime.datetime.now().isoformat()
                            still_pending.append(entry)
                            continue
                    except Exception as re_err:
                        print(f"[Error] Re-upload attempt failed: {re_err}")
                else:
                    print(f"   [Warning] Video file not found at {video_path}, cannot re-upload.")
            
            print(f"⚠️ Max retries reached or re-upload failed. Preserving files for manual check.")
            still_pending.append(entry)
        elif status == "rejected":
            print(f"🚫 Video {video_id} was REJECTED by YouTube (Policy/Copyright). Preserving files for manual check.")
            still_pending.append(entry)
        elif status == "not_found":
            print(f"⚠️ Video {video_id} not found on YouTube. It might have been deleted manually.")
            still_pending.append(entry)
        else:
            print(f"⏳ Video {video_id} is still in status: {status}. Waiting for next check.")
            still_pending.append(entry)

    # Save the updated pending list
    with open(PENDING_FILE, "w") as f:
        json.dump(still_pending, f, indent=4)

    print(f"📊 Summary: {cleaned_count} videos cleaned, {len(still_pending)} still pending.")

if __name__ == "__main__":
    monitor_and_cleanup()
