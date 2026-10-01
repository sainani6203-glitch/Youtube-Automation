import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
AUTOMATION_MODE = os.getenv("AUTOMATION_MODE", "semi-automated")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "Telugu")

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
READY_TO_REVIEW_DIR = os.path.join(BASE_DIR, "ready_to_review")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

for d in [OUTPUT_DIR, READY_TO_REVIEW_DIR, ASSETS_DIR]:
    os.makedirs(d, exist_ok=True)

# Topic Rotation Schedule (Focused on Single Deep Subjects)
TOPIC_SCHEDULE = {
    0: "The Dark Psychology of Manipulation and Mind Control",         # Monday
    1: "Kailasa Temple Ellora: The Impossible Monolithic Architecture", # Tuesday
    2: "The Secrets of Quantum Physics and Parallel Universes",        # Wednesday
    3: "Padmanabhaswamy Temple Vault B Secret Mystery",                 # Thursday
    4: "Human Subconscious Mind and Dark Psychology Triggers",          # Friday
    5: "The Mystery of Pyramids and Ancient Advanced Technology",       # Saturday
    6: "The Lost Sarasvati River and Ancient Indian Civilization",      # Sunday
}
