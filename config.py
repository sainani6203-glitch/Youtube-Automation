import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AUTOMATION_MODE = os.getenv("AUTOMATION_MODE", "semi-automated")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "Telugu")
LANGUAGES = [lang.strip() for lang in os.getenv("LANGUAGES", DEFAULT_LANGUAGE).split(",")]

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
READY_TO_REVIEW_DIR = os.path.join(BASE_DIR, "ready_to_review")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

for d in [OUTPUT_DIR, READY_TO_REVIEW_DIR, ASSETS_DIR]:
    os.makedirs(d, exist_ok=True)

# Topic Rotation Schedule (Focused on Single Deep Subjects)
TOPIC_SCHEDULE = {
    0: "Dark Psychology & Human Behavior",       # Monday
    1: "World Geography & Secret Earth Wonders", # Tuesday
    2: "Incredible Science & Space Secrets",    # Wednesday
    3: "Dark Psychology & Human Behavior",       # Thursday
    4: "World Geography & Secret Earth Wonders", # Friday
    5: "Incredible Science & Space Secrets",    # Saturday
    6: "World Geography & Secret Earth Wonders", # Sunday
}

# YouTube Playlist IDs (Language-specific)
CATEGORY_PLAYLISTS = {
    "Telugu": {
        "Dark Psychology & Human Behavior": "PLcK6it6l0tfc",
        "World Geography & Secret Earth Wonders": "PLLuMRvtViNgY",
        "Incredible Science & Space Secrets": "PLY8JQleszkVY",
    },
    "Hindi": {
        "Dark Psychology & Human Behavior": "PLfY0YU89XSQo",
        "World Geography & Secret Earth Wonders": "PLFekJAi51I5k",
        "Incredible Science & Space Secrets": "PLBrjl2htcYYA",
    }
}
