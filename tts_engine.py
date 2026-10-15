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
                    communicate = edge_tts.Communicate(chunk, voice, rate="+15%")
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

async def generate_voiceover(text: str, output_audio_path: str, language: str = "en"):
    """
    Generates speech audio with automatic fallback from edge-tts to gTTS.
    """
    try:
        await generate_voiceover_edge(text, output_audio_path, language)
        print(f"[Success] Generated voiceover via edge-tts: {output_audio_path}")
    except Exception as e:
        print(f"[Warning] edge-tts failed ({e}). Switching to gTTS fallback...")
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
