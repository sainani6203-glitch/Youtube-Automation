import asyncio
import edge_tts
import os
import time
import re
from moviepy import AudioFileClip, concatenate_audioclips
from gtts import gTTS

VOICE_MAP = {
    "en": "en-US-ChristopherNeural",     # Authoritative male voice for English
    "te": "te-IN-MohanNeural",           # Authoritative male voice for Telugu
    "hi": "hi-IN-MadhurNeural",          # Authoritative male voice for Hindi
    "english": "en-US-ChristopherNeural",
    "telugu": "te-IN-MohanNeural",
    "hindi": "hi-IN-MadhurNeural"
}

async def generate_voiceover_edge(text: str, output_audio_path: str, language: str = "en"):
    """
    Generates speech audio using edge-tts neural voices.
    """
    voice = VOICE_MAP.get(language.lower(), "en-US-ChristopherNeural")
    
    # Split text into sentence chunks (. ? ! |)
    chunks = [c.strip() for c in re.split(r'(?<=[.!?|])\s+', text) if c.strip()]
    if not chunks:
        chunks = [text]
        
    temp_files = []
    try:
        for idx, chunk in enumerate(chunks):
            chunk_path = f"{output_audio_path}_chunk_{idx}.mp3"
            temp_files.append(chunk_path)
            
            success = False
            max_retries = 5
            for attempt in range(1, max_retries + 1):
                try:
                    communicate = edge_tts.Communicate(chunk, voice, rate="+3%")
                    await communicate.save(chunk_path)
                    success = True
                    break
                except Exception as e:
                    print(f"[Warning] edge-tts chunk {idx+1} attempt {attempt} failed ({e}). Retrying...")
                    if attempt < max_retries:
                        await asyncio.sleep(3 * attempt)
            
            if not success:
                raise RuntimeError(f"All {max_retries} edge-tts attempts failed for chunk {idx+1}")
            
            if idx < len(chunks) - 1:
                await asyncio.sleep(1.5)
        
        audio_clips = [AudioFileClip(fp) for fp in temp_files]
        final_clip = concatenate_audioclips(audio_clips)
        final_clip.write_audiofile(output_audio_path, logger=None)
        
        for clip in audio_clips:
            clip.close()
        final_clip.close()
        return output_audio_path
        
    finally:
        for fp in temp_files:
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                except:
                    pass

def generate_voiceover_gtts_fallback(text: str, output_audio_path: str, language: str = "en"):
    """
    Fallback TTS using gTTS when edge-tts encounters network or 403 errors.
    Supports chunking for long scripts.
    """
    lang_code = language[:2].lower()
    if lang_code not in ["en", "te", "hi"]:
        lang_code = "en"
    print(f"[Info] Falling back to gTTS for language '{lang_code}'...")
    
    chunks = [c.strip() for c in re.split(r'(?<=[.!?|])\s+', text) if c.strip()]
    if not chunks:
        chunks = [text]
        
    temp_files = []
    try:
        for idx, chunk in enumerate(chunks):
            chunk_path = f"{output_audio_path}_gtts_chunk_{idx}.mp3"
            temp_files.append(chunk_path)
            
            success = False
            for attempt in range(1, 4):
                try:
                    tts = gTTS(text=chunk, lang=lang_code, slow=False)
                    tts.save(chunk_path)
                    success = True
                    break
                except Exception as e:
                    print(f"[Warning] gTTS chunk {idx+1} attempt {attempt} failed ({e}). Retrying...")
                    time.sleep(1)
            
            if not success:
                raise RuntimeError(f"All gTTS attempts failed for chunk {idx+1}")
                
        audio_clips = [AudioFileClip(fp) for fp in temp_files]
        final_clip = concatenate_audioclips(audio_clips)
        final_clip.write_audiofile(output_audio_path, logger=None)
        
        for clip in audio_clips:
            clip.close()
        final_clip.close()
        return output_audio_path
    finally:
        for fp in temp_files:
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                except:
                    pass

def generate_voiceover_pyttsx3(text: str, output_audio_path: str, language: str = "en"):
    """
    100% free offline TTS using pyttsx3 (Windows SAPI5 / system voices).
    Explicitly prioritizes male voices.
    """
    print(f"[Info] Falling back to offline pyttsx3 TTS...")
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    lang_code = language[:2].lower()
    
    chosen_voice = None
    # 1. Try to find a voice matching language AND explicitly male
    for voice in voices:
        v_info = (voice.name + " " + voice.id).lower()
        if lang_code in v_info or lang_code in [l.lower() for l in voice.languages]:
            if any(m in v_info for m in ["male", "david", "hemant", "ravi", "george", "microsoft david", "kumar"]):
                chosen_voice = voice.id
                break
                
    # 2. If no explicit male voice found, take any voice matching language
    if not chosen_voice:
        for voice in voices:
            v_info = (voice.name + " " + voice.id).lower()
            if lang_code in v_info or lang_code in [l.lower() for l in voice.languages]:
                chosen_voice = voice.id
                break
                
    if chosen_voice:
        engine.setProperty('voice', chosen_voice)
        
    engine.save_to_file(text, output_audio_path)
    engine.runAndWait()
    return output_audio_path

def generate_voiceover_openai(text: str, output_audio_path: str):
    """
    Fallback TTS using OpenAI Audio Speech API (`tts-1` with `onyx` deep male/neutral voice).
    """
    from config import OPENAI_API_KEY
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured.")
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("[Info] Falling back to OpenAI TTS (onyx deep male voice)...")
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text
    )
    response.stream_to_file(output_audio_path)
    return output_audio_path

async def generate_voiceover(text: str, output_audio_path: str, language: str = "en"):
    """
    Generates speech audio using edge-tts neural voices.
    Fallback chain: edge-tts retry -> pyttsx3 (Free Offline) -> OpenAI TTS -> gTTS.
    """
    lang_lower = language.lower()
    try:
        await generate_voiceover_edge(text, output_audio_path, language)
        print(f"[Success] Generated voiceover via edge-tts: {output_audio_path}")
        return output_audio_path
    except Exception as e:
        print(f"[Warning] edge-tts failed ({e}). Attempting retry...")
        try:
            await asyncio.sleep(5)
            await generate_voiceover_edge(text, output_audio_path, language)
            print(f"[Success] Generated voiceover via edge-tts on retry: {output_audio_path}")
            return output_audio_path
        except Exception as e2:
            print(f"[Warning] edge-tts retry also failed ({e2}). Trying 100% free offline pyttsx3 fallback...")
            try:
                generate_voiceover_pyttsx3(text, output_audio_path, language)
                print(f"[Success] Generated voiceover via offline pyttsx3: {output_audio_path}")
                return output_audio_path
            except Exception as e3:
                print(f"[Warning] pyttsx3 fallback failed ({e3}). Trying OpenAI TTS fallback...")
                try:
                    generate_voiceover_openai(text, output_audio_path)
                    print(f"[Success] Generated voiceover via OpenAI TTS: {output_audio_path}")
                    return output_audio_path
                except Exception as e4:
                    print(f"[Warning] OpenAI TTS fallback failed ({e4}). Falling back to gTTS...")
                    generate_voiceover_gtts_fallback(text, output_audio_path, language)
                    print(f"[Success] Generated voiceover via gTTS fallback: {output_audio_path}")
                    return output_audio_path

def create_voiceover_sync(text: str, output_audio_path: str, language: str = "en"):
    """Synchronous wrapper for generate_voiceover"""
    asyncio.run(generate_voiceover(text, output_audio_path, language))

if __name__ == "__main__":
    print("Testing TTS Engine with fallback...")
    test_text = "Welcome to your daily dose of smart knowledge. ఇది అసలైన తెలుగు వాయిస్ టెస్ట్."
    test_path = "sample_voice.mp3"
    create_voiceover_sync(test_text, test_path, "te")
    print(f"Audio saved to {test_path}")
