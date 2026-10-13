import asyncio
import edge_tts
import os
import time
import re
from moviepy import AudioFileClip, concatenate_audioclips

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
    Generates high-quality speech audio strictly using edge-tts male neural voices.
    Uses rate='+15%' for natural, fluent human-like pacing and splits into chunks with polite delays.
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
                    # rate="+15%" speeds up speech slightly to sound fluent and natural like human narration
                    communicate = edge_tts.Communicate(chunk, voice, rate="+15%")
                    await communicate.save(chunk_path)
                    success = True
                    break
                except Exception as e:
                    print(f"[Warning] edge-tts chunk {idx+1} attempt {attempt} failed ({e}). Retrying...")
                    if attempt < max_retries:
                        await asyncio.sleep(3 * attempt)
            
            if not success:
                raise RuntimeError(f"All {max_retries} attempts failed for chunk {idx+1}: {chunk[:30]}...")
            
            # Short polite delay between chunks
            if idx < len(chunks) - 1:
                await asyncio.sleep(1.0)
        
        # Concatenate chunks using moviepy
        audio_clips = [AudioFileClip(fp) for fp in temp_files]
        final_clip = concatenate_audioclips(audio_clips)
        final_clip.write_audiofile(output_audio_path, logger=None)
        
        for clip in audio_clips:
            clip.close()
        final_clip.close()
        
        print(f"[Success] Generated fluent voiceover via edge-tts pure male voice: {output_audio_path}")
        return output_audio_path
        
    finally:
        for fp in temp_files:
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                except:
                    pass

def create_voiceover_sync(text: str, output_audio_path: str, language: str = "en"):
    """Synchronous wrapper for generate_voiceover"""
    asyncio.run(generate_voiceover(text, output_audio_path, language))

if __name__ == "__main__":
    print("Testing TTS Engine with fluent rate...")
    test_text = "Welcome to your daily dose of smart knowledge. ఇది అసలైన తెలుగు మేల్ వాయిస్ టెస్ట్. మనుషులు మాట్లాడినట్టు చాలా ఫ్లూయెంట్ గా ఉంటుంది."
    test_path = "sample_voice.mp3"
    create_voiceover_sync(test_text, test_path, "te")
    print(f"Audio saved to {test_path}")
