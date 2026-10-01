import asyncio
import edge_tts
import os

VOICE_MAP = {
    "en": "en-US-ChristopherNeural",     # Authoritative male voice for English
    "te": "te-IN-MohanNeural",           # Authoritative male voice for Telugu
    "hi": "hi-IN-MadhurNeural",          # Authoritative male voice for Hindi
    "english": "en-US-ChristopherNeural",
    "telugu": "te-IN-MohanNeural",
    "hindi": "hi-IN-MadhurNeural"
}

async def generate_voiceover(text: str, output_audio_path: str, language: str = "en"):
    """
    Generates high-quality speech audio from text using edge-tts supporting multiple languages.
    """
    voice = VOICE_MAP.get(language.lower(), "en-US-AriaNeural")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_audio_path)
    return output_audio_path

def create_voiceover_sync(text: str, output_audio_path: str, language: str = "en"):
    """Synchronous wrapper for generate_voiceover"""
    asyncio.run(generate_voiceover(text, output_audio_path, language))

if __name__ == "__main__":
    print("Testing TTS Engine...")
    test_text = "Welcome to your daily dose of smart knowledge."
    test_path = "test_audio.mp3"
    create_voiceover_sync(test_text, test_path, "en")
    print(f"Audio saved to {test_path}")
    if os.path.exists(test_path):
        os.remove(test_path)
