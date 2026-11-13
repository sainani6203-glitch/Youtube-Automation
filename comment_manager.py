import os
import json
import google.generativeai as genai
from youtube_uploader import get_authenticated_service
from config import GEMINI_API_KEY, BASE_DIR

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

REPLIED_FILE = os.path.join(BASE_DIR, "replied_comments.json")

def load_replied():
    if os.path.exists(REPLIED_FILE):
        try:
            with open(REPLIED_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_replied(replied_set):
    with open(REPLIED_FILE, "w") as f:
        json.dump(list(replied_set), f, indent=4)

def generate_ai_reply(comment_text: str, video_title: str, channel_language: str = "Telugu") -> str:
    """Uses Gemini API to generate an intelligent, informative, friendly reply in the viewer's language."""
    if not GEMINI_API_KEY:
        return "Thank you for watching! Subscribe for more amazing mysteries and facts! 🌋✨"

    prompt = f"""
    You are the creator of a popular YouTube channel focused on fascinating mysteries, ancient history, and geography facts ("Prapancha Rahasyaluu").
    A viewer left this comment on the video titled "{video_title}" ({channel_language} channel):
    "{comment_text}"

    Task: Write a short, engaging, polite, and informative reply to this comment in the EXACT SAME LANGUAGE that the viewer used in their comment.
    Requirements:
    1. Acknowledge their comment or question directly and warmly.
    2. Provide a quick fascinating insight or friendly remark related to the video topic.
    3. Encourage them to subscribe for more hidden facts and mysteries.
    4. Keep it concise (under 30 words). Return ONLY the reply text, with no extra quotes or explanation.
    """

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-pro-latest"
    ]

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip().strip('"')
        except Exception as e:
            print(f"[Warning] Failed to generate reply with {model_name}: {e}")

    return "Thank you for watching! Subscribe for more amazing mysteries and facts! 🌋✨"

def check_and_reply_channel(language: str = "Telugu"):
    print(f"\n🤖 Checking comments for {language} channel...")
    try:
        youtube = get_authenticated_service(language=language)
        
        # Get channel info to find our own channel ID (so we don't reply to ourselves)
        channels_response = youtube.channels().list(part="snippet", mine=True).execute()
        my_channel_id = ""
        if channels_response.get("items"):
            my_channel_id = channels_response["items"][0]["id"]

        # Get recent uploaded videos
        search_args = {
            "part": "snippet",
            "type": "video",
            "order": "date",
            "maxResults": 10
        }
        if my_channel_id:
            search_args["channelId"] = my_channel_id

        search_response = youtube.search().list(**search_args).execute()

        videos = search_response.get("items", [])
        if not videos:
            print(f"No recent videos found on {language} channel.")
            return

        replied_set = load_replied()
        replied_count = 0

        for video in videos:
            video_id = video["id"]["videoId"]
            video_title = video["snippet"]["title"]

            # Fetch comment threads for this video
            try:
                threads_response = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=20
                ).execute()
            except Exception as e:
                print(f"[Warning] Could not fetch comments for video {video_id}: {e}")
                continue

            for thread in threads_response.get("items", []):
                top_comment = thread["snippet"]["topLevelComment"]
                comment_id = top_comment["id"]
                comment_snippet = top_comment["snippet"]
                author_channel_id = comment_snippet.get("authorChannelId", {}).get("value", "")
                
                # Skip if we already replied or if the comment is by us
                if comment_id in replied_set or author_channel_id == my_channel_id:
                    continue

                # Check if we (the channel) already replied in the replies list
                already_replied_by_us = False
                if "replies" in thread:
                    for reply in thread["replies"].get("comments", []):
                        reply_author_id = reply["snippet"].get("authorChannelId", {}).get("value", "")
                        if reply_author_id == my_channel_id:
                            already_replied_by_us = True
                            break

                if already_replied_by_us:
                    replied_set.add(comment_id)
                    continue

                comment_text = comment_snippet["textDisplay"]
                author_name = comment_snippet["authorDisplayName"]

                print(f"\n💬 New comment on '{video_title}' by {author_name}: {comment_text}")

                # Generate AI reply
                ai_reply = generate_ai_reply(comment_text, video_title, channel_language=language)
                print(f"🤖 Generated AI reply: {ai_reply}")

                # Post reply
                try:
                    youtube.comments().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "parentId": comment_id,
                                "textOriginal": ai_reply
                            }
                        }
                    ).execute()
                    print(f"✅ Successfully posted reply to comment {comment_id}!")
                    replied_set.add(comment_id)
                    replied_count += 1
                except Exception as e:
                    print(f"[Error] Failed to post reply: {e}")

        save_replied(replied_set)
        print(f"✨ Completed comment check for {language} channel. Posted {replied_count} new replies.")

    except Exception as e:
        print(f"[Error] Failed checking comments for {language} channel: {e}")

if __name__ == "__main__":
    for lang in ["Telugu", "Hindi"]:
        try:
            check_and_reply_channel(language=lang)
        except Exception as e:
            print(f"[Warning] Skipped {lang} channel due to auth/error: {e}")
