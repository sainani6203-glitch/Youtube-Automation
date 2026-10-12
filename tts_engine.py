import asyncio
import edge_tts
import os
import time

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
    Generates high-quality speech audio exclusively using edge-tts male neural voices with persistent retries.
    Never falls back to female voices.
    """
    voice = VOICE_MAP.get(language.lower(), "en-US-ChristopherNeural")
    
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_audio_path)
            print(f"[Success] Generated voiceover via edge-tts male voice (attempt {attempt}): {output_audio_path}")
            return output_audio_path
        except Exception as e:
            print(f"[Warning] edge-tts attempt {attempt} failed ({e}). Retrying...")
            if attempt < max_retries:
                await asyncio.sleep(3 * attempt) # Progressive backoff: 3s, 6s, 9s, 12s
            else:
                raise RuntimeError(f"All {max_retries} edge-tts attempts failed for voice {voice}. Error: {e}")

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
