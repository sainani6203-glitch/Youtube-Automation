import asyncio
import edge_tts
import os
from gtts import gTTS

VOICE_MAP = {
    "en": "en-US-ChristopherNeural",     # Authoritative male voice for English
    "te": "te-IN-MohanNeural",           # Authoritative male voice for Telugu
    "hi": "hi-IN-MadhurNeural",          # Authoritative male voice for Hindi
    "english": "en-US-ChristopherNeural",
    "telugu": "te-IN-MohanNeural",
    "hindi": "hi-IN-MadhurNeural"
}

GTTS_LANG_MAP = {
    "en": "en",
    "te": "te",
    "hi": "hi",
    "english": "en",
    "telugu": "te",
    "hindi": "hi"
}

async def generate_voiceover(text: str, output_audio_path: str, language: str = "en"):
    """
    Generates high-quality speech audio using edge-tts with retries, falling back to gTTS only if all edge-tts retries fail.
    """
    voice = VOICE_MAP.get(language.lower(), "en-US-ChristopherNeural")
    lang_code = GTTS_LANG_MAP.get(language.lower(), "en")
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_audio_path)
            print(f"[Success] Generated voiceover via edge-tts (attempt {attempt}): {output_audio_path}")
            return output_audio_path
        except Exception as e:
            print(f"[Warning] edge-tts attempt {attempt} failed ({e}).")
            if attempt < max_retries:
                await asyncio.sleep(2)
            else:
                print("[Warning] All edge-tts attempts failed. Falling back to gTTS...")
    
    # Fallback to gTTS if all edge-tts attempts failed
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(output_audio_path)
        print(f"[Success] Generated voiceover via gTTS fallback: {output_audio_path}")
        return output_audio_path
    except Exception as gtts_err:
        print(f"[Error] gTTS fallback also failed: {gtts_err}")
        raise gtts_err

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
