import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
AUTOMATION_MODE = os.getenv("AUTOMATION_MODE", "semi-automated")

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
READY_TO_REVIEW_DIR = os.path.join(BASE_DIR, "ready_to_review")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

for d in [OUTPUT_DIR, READY_TO_REVIEW_DIR, ASSETS_DIR]:
    os.makedirs(d, exist_ok=True)

# Topic Rotation Schedule
TOPIC_SCHEDULE = {
    0: "Smart Money & Savings Tips",          # Monday
    1: "Life Hacks & Productivity",           # Tuesday
    2: "Incredible Science & Space Facts",    # Wednesday
    3: "Digital Security & Tech Tips",        # Thursday
    4: "Psychology & Human Behavior",         # Friday
    5: "Amazing History & Mystery Facts",     # Saturday
    6: "Health, Fitness & Wellness Tips",     # Sunday
}
