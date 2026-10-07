import google.generativeai as genai
import json
import os
from config import GEMINI_API_KEY

try:
    from groq import Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except ImportError:
    GROQ_API_KEY = None
    groq_client = None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_video_script(topic: str, video_type: str = "short", language: str = "English", linked_long_video_url: str = None, short_angle: str = "shocking_fact") -> dict:
    """
    Generates an engaging script, title, description, and keywords for stock search using Groq or Gemini.
    video_type: 'short' or 'long'
    language: target language (e.g. 'English', 'Telugu', 'Hindi')
    linked_long_video_url: optional long video URL to cross-promote in shorts
    short_angle: angle/focus for shorts ('shocking_fact' or 'hidden_truth') to ensure variety between daily shorts
    """
    if video_type == "short":
        cta_instruction = f"5. CRITICAL: The final scene MUST end with a strong Call-to-Action telling viewers to SUBSCRIBE to the channel and turn on the notification bell to discover more such facts, and also watch the full detailed video on the channel (e.g., in Telugu: 'ఇలాంటి అంతుచిక్కని రహస్యాలు మరిన్ని తెలుసుకోవడానికి మన ఛానెల్‌ని సబ్‌స్క్రైబ్ చేసుకొని బెల్ ఐకాన్ ఆన్ చేసుకోండి, మరియు పూర్తి వివరాల కోసం ఫుల్ వీడియో చూడండి!')." if linked_long_video_url else "5. Conclude with a strong CTA to subscribe, like, and turn on the notification bell."
        
        angle_instruction = ""
        if short_angle == "shocking_fact":
            angle_instruction = "Focus specifically on ONE unique, surprising, shocking, or mind-boggling sub-fact of this topic (Do NOT give a general summary; dive into one specific startling detail)."
        elif short_angle == "hidden_truth":
            angle_instruction = "Focus specifically on ONE unique mysterious background, hidden truth, or lesser-known origin story related to this topic."
        elif short_angle == "unsolved_mystery":
            angle_instruction = "Focus specifically on ONE unique unresolved mystery, missing evidence, or baffling unanswered question within this topic."
        elif short_angle == "bizarre_experiment":
            angle_instruction = "Focus specifically on ONE unique bizarre experiment, historical anomaly, or strange event related to this topic."
        else:
            angle_instruction = "Focus on ONE unique, fascinating scientific paradox, strange phenomenon, or mind-bending perspective of this topic."

        prompt = f"""
        Create a viral, high-retention YouTube Short script about the topic: "{topic}".
        {angle_instruction}
        CRITICAL REQUIREMENT FOR TITLE: The title MUST be BILINGUAL in this exact format: "Telugu Title | English Title #shorts". MAXIMUM length 90 characters total.
        The description and script narration text MUST be written entirely in {language}.
        Requirements:
        1. FIRST 3 SECONDS HOOK: Start directly with a mind-blowing question, shocking fact, or captivating mystery about the topic itself. CRITICAL: DO NOT use annoying command words like "agu", "apu", "stop scrolling", or telling viewers to stop/wait. Jump straight into the fascinating fact or secret in {language}.
        2. FAST PACING & LENGTH: Keep total length around 120-150 words (approx 40-50 seconds when spoken).
        3. 8-12 VISUAL SCENES: Break the script into 8 to 12 short, punchy sentences/scenes so that each visual clip stays on screen for only 3-4 seconds before cutting to the next.
        4. STOCK FOOTAGE KEYWORDS: For each scene, provide a distinct, dynamic visual keyword search term IN ENGLISH (e.g., "glowing ancient artifact closeup", "mysterious dark forest drone shot", "futuristic laboratory digital display") to fetch high-impact stock footage on Pexels.
        {cta_instruction}
        
        Return ONLY valid JSON in this exact format:
        {{
            "title": "Telugu Title | English Title #shorts",
            "description": "Optimized description with tags",
            "scenes": [
                {{"text": "Hook sentence 1...", "visual_keyword": "keyword1"}},
                {{"text": "Sentence 2...", "visual_keyword": "keyword2"}},
                {{"text": "Sentence 3...", "visual_keyword": "keyword3"}},
                {{"text": "Sentence 4...", "visual_keyword": "keyword4"}},
                {{"text": "Sentence 5...", "visual_keyword": "keyword5"}},
                {{"text": "Sentence 6...", "visual_keyword": "keyword6"}},
                {{"text": "Sentence 7...", "visual_keyword": "keyword7"}},
                {{"text": "Sentence 8...", "visual_keyword": "keyword8"}}
            ]
        }}
        """
    else:
        prompt = f"""
        Create a comprehensive, highly engaging and deeply detailed 10-12 minute long-form YouTube video script focusing on ONE SINGLE specific topic/mystery: "{topic}" (Do NOT list 5-6 different separate topics; instead, explore this ONE single subject deeply from every angle: its origin, history, deep mysteries, scientific analysis, architectural wonders, and final conclusion).
        CRITICAL REQUIREMENT FOR TITLE: The title MUST be BILINGUAL in this exact format: "Telugu Title | English Title". MAXIMUM length 90 characters total.
        The description and script narration text MUST be written entirely in {language}.
        Requirements:
        1. Powerful hook and comprehensive introduction to this single subject.
        2. Narrative depth exploring various chapters/aspects of this ONE topic in detail.
        3. Strong conclusion and a powerful Call-to-Action telling viewers to LIKE, SHARE, and SUBSCRIBE to the channel (e.g., in Telugu: 'ఈ వీడియో మీకు నచ్చితే తప్పకుండా లైక్ చేయండి, షేర్ చేయండి, మరియు ఇలాంటి మరిన్ని రహస్యాలు తెలుసుకోవడానికి మన ఛానెల్‌ని సబ్‌స్క్రైబ్ చేసుకోండి!').
        4. CRITICAL: Each scene in the "scenes" array MUST contain a detailed, rich paragraph of at least 80-100 words of narration, so that when combined across 18-22 scenes, the total word count is between 1500-1800 words (approx 10-12 minutes when spoken).
        5. For each scene, provide a specific visual keyword search term IN ENGLISH for stock footage.
        
        Return ONLY valid JSON in this exact format:
        {{
            "title": "Telugu Title | English Title",
            "description": "Detailed SEO description with timestamps",
            "scenes": [
                {{"text": "Detailed paragraph 1 with 80-100 words...", "visual_keyword": "keyword1"}},
                {{"text": "Detailed paragraph 2 with 80-100 words...", "visual_keyword": "keyword2"}}
            ]
        }}
        """

    text_result = None

    # Try Groq first if available (bypasses Gemini rate/quota limits)
    if groq_client:
        try:
            print("[Info] Generating script using Groq (openai/gpt-oss-120b)...")
            completion = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are a professional YouTube scriptwriter and JSON generator. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=8192
            )
            text_result = completion.choices[0].message.content.strip()
            print("[Success] Generated script via Groq.")

            # Test parsing JSON to ensure it wasn't truncated
            try:
                cleaned = text_result
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                parsed = json.loads(cleaned.strip())
                return parsed
            except json.JSONDecodeError as jde:
                print(f"[Warning] Groq JSON output was truncated/invalid ({jde}), falling back to Gemini...")
                text_result = None
        except Exception as e:
            print(f"[Note] Groq generation failed ({e}), falling back to Gemini...")
            text_result = None
    # Fallback to Gemini if Groq not available or failed
    if not text_result:
        if not GEMINI_API_KEY:
            raise ValueError("Neither GROQ_API_KEY nor GEMINI_API_KEY is available or working.")
            
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
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(max_output_tokens=8192)
                )
                if response and response.text:
                    print(f"[Success] Used Gemini model: {m_name}")
                    break
            except Exception as e:
                print(f"[Note] Model '{m_name}' skipped ({e})")
                
        if not response or not response.text:
            raise RuntimeError("All Gemini and Groq models reached quota limits or failed.")
        text_result = response.text.strip()

    # Clean up markdown code blocks if present
    if text_result.startswith("```json"):
        text_result = text_result[7:]
    if text_result.endswith("```"):
        text_result = text_result[:-3]
        
    return json.loads(text_result.strip())

def generate_fresh_topic(category_prompt: str, language: str = "English") -> str:
    """
    Generates a unique, fresh, and engaging topic under the given category using Groq or Gemini.
    """
    prompt = f"""
    Generate one unique, highly catchy, and viral YouTube video topic under this broad category: "{category_prompt}".
    The topic must be fresh, intriguing, and written entirely in {language}.
    Return ONLY the topic title as a plain string, with no extra formatting, quotes, or markdown.
    """

    topic_text = None

    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=100
            )
            topic_text = completion.choices[0].message.content.strip()
        except Exception:
            pass

    if not topic_text and GEMINI_API_KEY:
        model_names = [
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-3.1-pro-preview",
            "gemini-3.5-flash-lite"
        ]
        for m_name in model_names:
            try:
                model = genai.GenerativeModel(m_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    topic_text = response.text.strip()
                    break
            except Exception:
                continue

    if not topic_text:
        return category_prompt  # fallback to category name
        
    return topic_text.replace('"', '')

if __name__ == "__main__":
    print("Testing Script Generator...")
    try:
        script_data = generate_video_script("3 Amazing Psychology Tricks", "short")
        print(json.dumps(script_data, indent=2))
    except Exception as e:
        print(f"Error: {e}")
