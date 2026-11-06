import os
import json
from youtube_uploader import upload_video_to_youtube, upload_thumbnail

def main():
    ready_dir = 'ready_to_review'
    if not os.path.exists(ready_dir):
        print(f"Directory {ready_dir} does not exist.")
        return
        
    mp4s = [f for f in os.listdir(ready_dir) if f.endswith('.mp4') and 'Long' in f]
    if mp4s:
        latest_mp4 = sorted(mp4s)[-1]
        video_path = os.path.join(ready_dir, latest_mp4)
        meta_json = video_path.replace('.mp4', '.json')
        title = 'Incredible Mystery Facts'
        desc = 'Watch till the end!'
        if os.path.exists(meta_json):
            with open(meta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                title = data.get('title', title)
                desc = data.get('description', desc)
        print(f'Re-uploading {video_path}...')
        vid_id = upload_video_to_youtube(video_path, title, desc, privacy_status='public', language='Telugu')
        print(f'Uploaded successfully! Video ID: {vid_id}')
        
        # Upload thumbnail if exists
        thumb_path = os.path.join(ready_dir, 'thumbnail.jpg')
        if os.path.exists(thumb_path):
            upload_thumbnail(vid_id, thumb_path, language='Telugu')
    else:
        print('No Long video found in ready_to_review.')

if __name__ == '__main__':
    main()
