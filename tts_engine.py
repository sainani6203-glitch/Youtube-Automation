import asyncio
import edge_tts
import os

VOICE_MAP = {
    "en": "en-US-AriaNeural",
    "te": "te-IN-ShrutiNeural",
    "hi": "hi-IN-SwaraNeural",
    "english": "en-US-AriaNeural",
    "telugu": "te-IN-ShrutiNeural",
    "hindi": "hi-IN-SwaraNeural"
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
