import google.generativeai as genai
import json
import os
from config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_video_script(topic: str, video_type: str = "short", language: str = "English") -> dict:
    """
    Generates an engaging script, title, description, and keywords for stock search using Gemini.
    video_type: 'short' or 'long'
    language: target language (e.g. 'English', 'Telugu', 'Hindi')
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing in environment variables.")

    if video_type == "short":
        prompt = f"""
        Create a viral, highly engaging YouTube Short script about the topic: "{topic}".
        The title, description, and script text MUST be written entirely in {language}.
        Requirements:
        1. Must have a powerful hook in the first 3 seconds.
        2. Keep the total length around 100-140 words (approx 40-50 seconds when spoken).
        3. Break the script into 3-4 visual scenes/sentences.
        4. For each scene, provide a short visual keyword search term IN ENGLISH (e.g., "person typing fast", " glowing brain") to find stock footage on Pexels.
        
        Return ONLY valid JSON in this exact format:
        {{
            "title": "Catchy YouTube Short Title #shorts",
            "description": "Optimized description with tags",
            "scenes": [
                {{"text": "Sentence 1...", "visual_keyword": "keyword1"}},
                {{"text": "Sentence 2...", "visual_keyword": "keyword2"}}
            ]
        }}
        """
    else:
        prompt = f"""
        Create a comprehensive, highly engaging 9-10 minute long-form YouTube video script about the topic: "{topic}".
        The title, description, and script text MUST be written entirely in {language}.
        Requirements:
        1. Engaging hook and comprehensive introduction.
        2. Detailed exploration with 5-6 deep main points/sections.
        3. Strong conclusion and call-to-action to subscribe.
        4. Total length around 1300-1500 words (approx 9-10 minutes when spoken).
        5. Break into 15-20 scenes, each with a specific visual keyword search term IN ENGLISH for stock footage.
        
        Return ONLY valid JSON in this exact format:
        {{
            "title": "Engaging Long Video Title",
            "description": "Detailed SEO description with timestamps",
            "scenes": [
                {{"text": "Scene sentence 1...", "visual_keyword": "keyword1"}},
                {{"text": "Scene sentence 2...", "visual_keyword": "keyword2"}}
            ]
        }}
        """

    model_names = [
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-3.1-pro-preview",
        "gemini-3.5-flash-lite"
    ]
    response = None
    
    for m_name in model_names:
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content(prompt)
            if response and response.text:
                print(f"[Success] Used Gemini model: {m_name}")
                break
        except Exception as e:
            print(f"[Note] Model '{m_name}' skipped ({e})")
            
    if not response or not response.text:
        raise RuntimeError("All Gemini models reached daily quota limit or failed. Please try again later or use another API key.")

    text_result = response.text.strip()
    
    # Clean up markdown code blocks if present
    if text_result.startswith("```json"):
        text_result = text_result[7:]
    if text_result.endswith("```"):
        text_result = text_result[:-3]
        
    return json.loads(text_result.strip())

if __name__ == "__main__":
    print("Testing Script Generator...")
    try:
        script_data = generate_video_script("3 Amazing Psychology Tricks", "short")
        print(json.dumps(script_data, indent=2))
    except Exception as e:
        print(f"Error: {e}")
