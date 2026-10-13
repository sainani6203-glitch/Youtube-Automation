import asyncio
import edge_tts
import os
import time
import re
import subprocess
import imageio_ffmpeg
from gtts import gTTS
from moviepy import AudioFileClip, concatenate_audioclips

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

def pitch_shift_to_male(input_path: str, output_path: str):
    """
    Applies FFmpeg audio filters to lower the pitch and convert gTTS female voice into a deep male voice.
    """
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, '-y', '-i', input_path,
        '-af', 'asetrate=44100*0.8,aresample=44100,atempo=1.25',
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

async def generate_voiceover(text: str, output_audio_path: str, language: str = "en"):
    """
    Generates speech audio using edge-tts male neural voices (chunked).
    If edge-tts fails (e.g. 403 WSS restriction), seamlessly falls back to gTTS
    and pitch-shifts it into a deep male voice using FFmpeg so it never fails and always sounds male.
    """
    voice = VOICE_MAP.get(language.lower(), "en-US-ChristopherNeural")
    gtts_lang = GTTS_LANG_MAP.get(language.lower(), "en")
    
    # Split text into sentence chunks (. ? ! |)
    chunks = [c.strip() for c in re.split(r'(?<=[.!?|])\s+', text) if c.strip()]
    if not chunks:
        chunks = [text]
        
    temp_files = []
    edge_tts_failed = False
    
    try:
        # Try edge-tts first
        for idx, chunk in enumerate(chunks):
            chunk_path = f"{output_audio_path}_chunk_{idx}.mp3"
            temp_files.append(chunk_path)
            
            success = False
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    communicate = edge_tts.Communicate(chunk, voice)
                    await communicate.save(chunk_path)
                    success = True
                    break
                except Exception as e:
                    print(f"[Warning] edge-tts chunk {idx+1} attempt {attempt} failed ({e}). Retrying...")
                    if attempt < max_retries:
                        await asyncio.sleep(2 * attempt)
            
            if not success:
                print(f"[Warning] edge-tts failed for chunk {idx+1}. Triggering gTTS fallback...")
                edge_tts_failed = True
                break
        
        if edge_tts_failed:
            raise RuntimeError("edge-tts encountered server block/403.")
            
        # Concatenate edge-tts chunks
        audio_clips = [AudioFileClip(fp) for fp in temp_files]
        final_clip = concatenate_audioclips(audio_clips)
        final_clip.write_audiofile(output_audio_path, logger=None)
        
        for clip in audio_clips:
            clip.close()
        final_clip.close()
        
        print(f"[Success] Generated voiceover via edge-tts male voice (chunked): {output_audio_path}")
        return output_audio_path

    except Exception as e:
        print(f"[Notice] Falling back to gTTS with male pitch transformation due to: {e}")
        # Cleanup temp files from edge-tts attempt
        for fp in temp_files:
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                except:
                    pass
        temp_files.clear()
        
        try:
            # Generate via gTTS per chunk and pitch shift to male
            gtts_temp_files = []
            for idx, chunk in enumerate(chunks):
                gtts_chunk_raw = f"{output_audio_path}_gtts_raw_{idx}.mp3"
                gtts_chunk_male = f"{output_audio_path}_gtts_male_{idx}.mp3"
                gtts_temp_files.extend([gtts_chunk_raw, gtts_chunk_male])
                
                def _gen_gtts():
                    tts = gTTS(text=chunk, lang=gtts_lang, slow=False)
                    tts.save(gtts_chunk_raw)
                    pitch_shift_to_male(gtts_chunk_raw, gtts_chunk_male)
                
                await asyncio.to_thread(_gen_gtts)
                temp_files.append(gtts_chunk_male)
            
            # Concatenate pitch-shifted male gTTS chunks
            audio_clips = [AudioFileClip(fp) for fp in temp_files if fp.endswith('_male_' + str(chunks.index(chunks[temp_files.index(fp)])) if False else fp)] # wait, simpler list
            
            # Better: collect all male chunk paths
            male_chunk_paths = [fp for fp in temp_files if '_gtts_male_' in fp]
            audio_clips = [AudioFileClip(fp) for fp in male_chunk_paths]
            final_clip = concatenate_audioclips(audio_clips)
            final_clip.write_audiofile(output_audio_path, logger=None)
            
            for clip in audio_clips:
                clip.close()
            final_clip.close()
            
            print(f"[Success] Generated voiceover via gTTS + Male Pitch Shift Fallback: {output_audio_path}")
            return output_audio_path
            
        except Exception as fallback_err:
            raise RuntimeError(f"Both edge-tts and gTTS fallback failed. Error: {fallback_err}")
            
    finally:
        # Cleanup all temp files
        for fp in temp_files:
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                except:
                    pass
        # Cleanup any raw gtts files if left over
        for f in os.listdir(os.path.dirname(output_audio_path) or '.'):
            if '_gtts_raw_' in f or '_gtts_male_' in f or '_chunk_' in f:
                try:
                    os.remove(os.path.join(os.path.dirname(output_audio_path) or '.', f))
                except:
                    pass

def create_voiceover_sync(text: str, output_audio_path: str, language: str = "en"):
    """Synchronous wrapper for generate_voiceover"""
    asyncio.run(generate_voiceover(text, output_audio_path, language))

if __name__ == "__main__":
    print("Testing TTS Engine...")
    test_text = "Welcome to your daily dose of smart knowledge. భారతదేశపు రహస్యాలు."
    test_path = "test_audio.mp3"
    create_voiceover_sync(test_text, test_path, "te")
    print(f"Audio saved to {test_path}")
    if os.path.exists(test_path):
        os.remove(test_path)
