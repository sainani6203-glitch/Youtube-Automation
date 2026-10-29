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

def has_telugu_chars(text: str) -> bool:
    return any('\u0C00' <= c <= '\u0C7F' for c in text)

def generate_video_script(topic: str, video_type: str = "short", language: str = "English", linked_long_video_url: str = None, short_angle: str = "shocking_fact") -> dict:
    """
    Generates an engaging script, title, description, and keywords for stock search using Groq or Gemini.
    video_type: 'short' or 'long'
    language: target language (e.g. 'English', 'Telugu', 'Hindi')
    linked_long_video_url: optional long video URL to cross-promote in shorts
    short_angle: angle/focus for shorts ('shocking_fact' or 'hidden_truth') to ensure variety between daily shorts
    """
    script_lang_name = language.capitalize()
    if script_lang_name.lower() == "hindi":
        script_script_name = "Devanagari script (हिंदी लिपि) mixed with English words"
        example_title = "Egypt Pyramids में छुपा हुआ hidden mystery रहस्य"
    elif script_lang_name.lower() == "telugu":
        script_script_name = "Telugu script (తెలుగు లిపి) mixed with English words"
        example_title = "Egypt Pyramids లో ఉన్న hidden secret రహస్యం"
    else:
        script_script_name = "English script"
        example_title = "Amazing Cosmic Mystery Revealed"

    if video_type == "short":
        cta_instruction = f"5. CRITICAL: The final scene MUST end with a strong Call-to-Action telling viewers to SUBSCRIBE to the channel and turn on the notification bell to discover more such facts, and also watch the full detailed video on the channel." if linked_long_video_url else "5. Conclude with a strong CTA to subscribe, like, and turn on the notification bell."
        mid_cta_instruction = "6. MID-VIDEO VALUE & CTA: In the middle of the video (around scene 5), smoothly include a brief curiosity hook and call to subscribe (e.g. telling viewers that the next incredible hidden truth is even more shocking and to make sure they subscribe so they don't miss future mysteries)."
        
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

        language_instruction = f"The script narration text MUST be written in natural conversational mixed-language style ({script_script_name}), combining regional script and English words smoothly just like modern viral YouTube shorts." if script_lang_name.lower() in ["telugu", "hindi"] else f"The script narration text MUST be written entirely in {language}."

        prompt = f"""
        Create a viral, high-retention YouTube Short script about the topic: "{topic}".
        {angle_instruction}
        CRITICAL MANDATE FOR TITLE: DO NOT copy any example title. The title MUST be strictly DUAL-LANGUAGE in this exact format: "[Regional {language} Title] | [English Title]". First write the title in authentic {language} script, followed by a pipe (|), and then the English title. Include "#shorts" at the end. Maximum 90 characters total.
        {language_instruction}
        Requirements:
        1. FIRST 3 SECONDS HOOK: Start directly with a mind-blowing question, shocking fact, or captivating mystery about the topic itself. CRITICAL: DO NOT use annoying command words like "agu", "apu", "stop scrolling", or telling viewers to stop/wait. Jump straight into the fascinating fact or secret.
        2. FAST PACING & LENGTH: Keep total length around 120-150 words (approx 40-50 seconds when spoken).
        3. 8-12 VISUAL SCENES: Break the script into 8 to 12 short, punchy sentences/scenes so that each visual clip stays on screen for only 3-4 seconds before cutting to the next.
        4. STOCK FOOTAGE KEYWORDS: For each scene, provide a distinct, dynamic visual keyword search term IN ENGLISH (e.g., "glowing ancient artifact closeup", "mysterious dark forest drone shot", "futuristic laboratory digital display") to fetch high-impact stock footage on Pexels.
        {mid_cta_instruction}
        {cta_instruction}
        
        Return ONLY valid JSON in this exact format:
        {{
            "title": "Dual language title #shorts",
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
        Create a comprehensive, highly engaging, and deeply researched 10-12 minute investigative documentary-style long-form YouTube video script focusing on ONE SINGLE specific topic/mystery: "{topic}" (Do NOT list 5-6 different separate topics; instead, explore this ONE single subject deeply from every angle).
        CRITICAL MANDATE FOR TITLE: DO NOT copy any example title. The title MUST be strictly DUAL-LANGUAGE in this exact format: "[Regional {language} Title] | [English Title]". First write the title in authentic {language} script, followed by a pipe (|), and then the English title. Maximum 90 characters total.
        The description and script narration text MUST be written entirely in {language}.
        
        Requirements & Investigative Documentary Standards:
        1. POWERFUL HOOK & MYSTERY SETUP: Start with an arresting question and a deep-dive introduction into the core enigma of this single subject.
        2. EMPIRICAL PROOFS & HARD EVIDENCE: Every major claim or chapter MUST include concrete proofs—such as archaeological excavation findings, carbon-14 dating results, geological anomalies, ancient architectural blueprints, or historical manuscripts from recognized archives.
        3. EXPERT THEORIES & DEBATES: Discuss recognized historians, scientists, or researchers, their published theories, and the ongoing scientific debate between conventional explanations and alternative anomalies.
        4. INVESTIGATIVE NARRATIVE ARC: Structure the script like a high-end Netflix or National Geographic documentary, guiding viewers step-by-step through the evidence (e.g., "ippudu ee proof chudandi...", logical deduction, and revealing hidden layers).
        5. CURIOSITY & VALUE LOOP: Establish a deep investigative narrative arc, reminding viewers throughout about our complete historical archives and masterclass deep-dives.
        6. STRONG CONCLUSION & CTA: Conclude with profound insight and a powerful Call-to-Action telling viewers to LIKE, SHARE, and SUBSCRIBE to the channel.
        7. LENGTH & WORD COUNT: Each scene in the "scenes" array MUST contain a detailed, rich paragraph of at least 80-100 words of narration, so that when combined across 18-22 scenes, the total word count is between 1500-1800 words (approx 10-12 minutes when spoken).
        8. VISUAL KEYWORDS: For each scene, provide a specific, highly visual search term IN ENGLISH for stock footage representing the exact historical artifact, excavation site, or scientific proof being discussed.
        
        Return ONLY valid JSON in this exact format:
        {{
            "title": "Dual language title",
            "description": "Detailed SEO description with timestamps and reference proofs",
            "scenes": [
                {{"text": "Detailed paragraph 1 with 80-100 words incorporating historical/scientific proofs...", "visual_keyword": "keyword1"}},
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
                model = genai.GenerativeModel(m_name, tools=['google_search'])
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(max_output_tokens=8192)
                )
                if response and response.text:
                    print(f"[Success] Used Gemini model with Google Search grounding: {m_name}")
                    break
            except Exception as e:
                print(f"[Note] Model '{m_name}' with search tools skipped ({e}), trying without tools...")
                try:
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(max_output_tokens=8192)
                    )
                    if response and response.text:
                        print(f"[Success] Used Gemini model (fallback without search): {m_name}")
                        break
                except Exception as e2:
                    print(f"[Note] Model '{m_name}' completely failed ({e2})")
                
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
    Generates a unique, fresh, and engaging topic under the given category using Groq or Gemini,
    avoiding previously used topics stored in topic_history.json.
    """
    history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "topic_history.json")
    used_topics = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                used_topics = json.load(f)
        except Exception:
            used_topics = []

    exclusion_list_str = ""
    if used_topics:
        recent_used = used_topics[-30:] # keep last 30 to avoid prompt bloating
        exclusion_list_str = f"CRITICAL: Do NOT repeat any of these recently used topics:\n" + "\n".join([f"- {t}" for t in recent_used])

    prompt = f"""
    Generate one unique, highly catchy, and viral YouTube video topic under this broad category: "{category_prompt}".
    The topic must be fresh, intriguing, and written entirely in {language}.
    {exclusion_list_str}
    Return ONLY the topic title as a plain string, with no extra formatting, quotes, or markdown.
    """

    topic_text = None

    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
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
        topic_text = category_prompt  # fallback to category name
    else:
        topic_text = topic_text.replace('"', '').strip()

    # Save to history
    if topic_text and topic_text not in used_topics:
        used_topics.append(topic_text)
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(used_topics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Warning] Could not save topic history: {e}")
        
    return topic_text

if __name__ == "__main__":
    print("Testing Script Generator...")
    try:
        script_data = generate_video_script("3 Amazing Psychology Tricks", "short")
        print(json.dumps(script_data, indent=2))
    except Exception as e:
        print(f"Error: {e}")
