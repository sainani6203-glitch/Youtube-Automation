import google.generativeai as genai
import json
import os
from config import GEMINI_API_KEY, OPENAI_API_KEY

try:
    from groq import Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except ImportError:
    GROQ_API_KEY = None
    groq_client = None

try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except ImportError:
    openai_client = None

# Initialize local Ollama client (OpenAI compatible endpoint)
try:
    ollama_client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"  # Ollama doesn't require a real API key
    )
except Exception:
    ollama_client = None

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
        script_script_name = "pure Devanagari script (हिंदी लिपि) ONLY, with NO mixed English words"
        example_title = "इजिप्त के पिरामिडों का रहस्य"
    elif script_lang_name.lower() == "telugu":
        script_script_name = "pure Telugu script (తెలుగు లిపి) ONLY, with NO mixed English words"
        example_title = "ఈజిప్ట్ పిరమిడ్ల రహస్యం"
    else:
        script_script_name = "English script"
        example_title = "Amazing Cosmic Mystery Revealed"

    if video_type == "short":
        cta_instruction = f"5. BRIDGE & CTA (FINAL SCENE): The final scene MUST end with a powerful curiosity loop Call-to-Action in pure {script_lang_name} instructing viewers that to discover more such unbelievable secrets and hidden truths, they must subscribe to the channel right now." if linked_long_video_url else f"5. BRIDGE & CTA (FINAL SCENE): The final scene MUST end with a powerful curiosity loop Call-to-Action in pure {script_lang_name} instructing viewers that to discover more such unbelievable secrets and hidden truths, they must subscribe to the channel right now."
        mid_cta_instruction = "6. MID-VIDEO RETENTION HOOK: Around scene 5, drop an intense secondary teaser to keep viewers locked in until the very end."
        
        angle_instruction = ""
        if short_angle == "shocking_fact":
            angle_instruction = "Focus strictly on ONE single, hard-hitting, mind-blowing core fact or piece of evidence (No generic summaries or multiple points; dive deep into one startling reality)."
        elif short_angle == "hidden_truth":
            angle_instruction = "Focus strictly on ONE unique hidden truth or mysterious origin story related to this topic."
        elif short_angle == "unsolved_mystery":
            angle_instruction = "Focus strictly on ONE baffling unanswered question or missing piece of evidence."
        elif short_angle == "bizarre_experiment":
            angle_instruction = "Focus strictly on ONE strange historical anomaly or bizarre event."
        else:
            angle_instruction = "Focus on ONE fascinating scientific paradox or mind-bending perspective."

        language_instruction = f"The script narration text MUST be written entirely in pure {script_lang_name} using authentic {script_script_name}. ABSOLUTELY NO mixed English words or romanized English words in the narration text or subtitles." if script_lang_name.lower() in ["telugu", "hindi"] else f"The script narration text MUST be written entirely in {language}."

        prompt = f"""
        Create a viral, high-retention YouTube Short script about the topic: "{topic}".
        {angle_instruction}
        CRITICAL MANDATE FOR TITLE: DO NOT copy any example title. The title MUST be strictly DUAL-LANGUAGE in this exact format: "[Regional {language} Title] | [English Title]". First write the title in authentic {language} script, followed by a pipe (|), and then the English title. Include "#shorts" at the end. Maximum 90 characters total.
        {language_instruction}
        Requirements (5 Viral Execution Steps):
        1. ZERO-SECOND HOOK: Start directly with an arresting, hard-hitting statement or shocking reality about the topic. NO slow intros, NO "hey guys", NO command words like "agu/apu". Jump straight into the mystery.
        2. DIRECT HARD-HITTING FACTS: Instead of listing multiple random points, explain ONE single deep core truth/proof powerfully and dynamically.
        3. FAST PACING & LENGTH: Keep total length STRICTLY around 80-100 words (approx 40-45 seconds when spoken, ensuring total duration never exceeds 50 seconds) with punchy, fast-moving sentences.
        4. 8-12 VISUAL SCENES & KEYWORDS: Break the script into 8 to 12 short scenes. For each scene, provide a distinct, high-impact visual search term IN ENGLISH (e.g., "ancient stone carving closeup dramatic lighting", "dark mysterious laboratory macro shot") for Pexels stock footage.
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
        duration_desc = "exact 5 to 6 minute master-class documentary-style long-form YouTube video script (~800 words across exactly 20 scenes for fast-paced professional documentary pacing)"
        structure_desc = """
        Requirements & Investigative Structure (Total Exact 5 to 6 Minutes / ~800 Words across exactly 20 scenes):
        1. PART 1: HOOK & ENIGMA SETUP (Scenes 1-5) - Arresting hook, geographical location coordinates, and deep historical mystery introduction.
        2. PART 2: ANCIENT CONTEXT & BACKSTORY (Scenes 6-10) - Detailed exploration of historical records, local legends, and previous expeditions.
        3. PART 3: LIVE PROOFS, SATELLITE MAPS & EVIDENCE (Scenes 11-15) - Deep dive into concrete archaeological findings, satellite map analysis, scientific measurements, and expert proofs.
        4. PART 4: UNRESOLVED ANOMALIES & CLIMAX CTA (Scenes 16-20) - Deep philosophical analysis, final unsolved questions, and powerful Call-to-Action.
        5. PACING: Exactly 20 scenes. Each scene in the "scenes" array MUST contain narration text of about 35-40 words to ensure fast-paced documentary visual variety.
        6. VISUAL KEYWORDS (STRICT PROOFS & MAPS): For each scene, explicitly include terms like "satellite map view with coordinates", "archaeological excavation artifact closeup", "real historical archive photography", "ancient manuscript map", or "historical expedition photo".
        """
        json_scenes_example = ",\n".join([f'                {{"text": "Paragraph {i} with 35-40 words...", "visual_keyword": "keyword{i}"}}' for i in range(1, 21)])

        prompt = f"""
        Create a rich, high-retention, and deeply engaging {duration_desc} focusing on ONE SINGLE specific topic/mystery: "{topic}".
        CRITICAL MANDATE FOR TITLE: DO NOT copy any example title. The title MUST be strictly DUAL-LANGUAGE in this exact format: "[Regional {language} Title] | [English Title]". First write the title in authentic {language} script, followed by a pipe (|), and then the English title. Maximum 90 characters total.
        The description and script narration text MUST be written entirely in pure {script_lang_name} using authentic {script_script_name}. ABSOLUTELY NO mixed English words or romanized English words.
        
        {structure_desc}
        
        Return ONLY valid JSON in this exact format:
        {{
            "title": "Dual language title",
            "description": "Detailed SEO description with timestamps and reference proofs",
            "scenes": [
{json_scenes_example}
            ]
        }}
        """

    text_result = None

    max_tokens_val = 16384 if video_type == "long" else 8192

    def parse_json_safely(raw_text):
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        import re
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        try:
            return json.loads(cleaned, strict=False)
        except Exception as e:
            print(f"[Warning] JSON parse failed ({e}), attempting truncation repair...")
            last_brace = cleaned.rfind("}")
            if last_brace != -1:
                fixed = cleaned[:last_brace+1]
                if not fixed.endswith("]"):
                    if not fixed.strip().endswith("}"):
                        fixed = fixed[:fixed.rfind("}")] + "}"
                    fixed += "\n  ]\n}"
                try:
                    return json.loads(fixed, strict=False)
                except Exception:
                    pass
            raise e

    # 1. Try Gemini first as primary provider
    if not text_result and GEMINI_API_KEY:
        model_names = [
            "gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-flash-latest",
            "gemini-pro-latest"
        ]
        response = None
        import time
        
        for m_name in model_names:
            success_gemini = False
            for attempt in range(2):
                try:
                    model = genai.GenerativeModel(m_name, tools=['google_search'])
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens_val)
                    )
                    if response and response.text:
                        print(f"[Success] Used Gemini model with Google Search grounding: {m_name}")
                        success_gemini = True
                        break
                except Exception as e:
                    print(f"[Note] Model '{m_name}' with search tools failed ({e}), trying without tools (attempt {attempt+1})...")
                    try:
                        model = genai.GenerativeModel(m_name)
                        response = model.generate_content(
                            prompt,
                            generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens_val)
                        )
                        if response and response.text:
                            print(f"[Success] Used Gemini model (fallback without search): {m_name}")
                            success_gemini = True
                            break
                    except Exception as e2:
                        print(f"[Note] Model '{m_name}' attempt {attempt+1} completely failed ({e2})")
                        time.sleep(3)
            if success_gemini:
                break
                
        if response and response.text:
            text_result = response.text.strip()

    # 2. Try Groq models as first fallback
    if not text_result and groq_client:
        groq_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.2-90b-vision-preview",
            "llama3-70b-8192"
        ]
        import time
        for g_model in groq_models:
            success_groq = False
            for attempt in range(2):
                try:
                    print(f"[Info] Generating script using Groq ({g_model}) [attempt {attempt+1}]...")
                    completion = groq_client.chat.completions.create(
                        model=g_model,
                        messages=[
                            {"role": "system", "content": "You are a professional YouTube scriptwriter and JSON generator. Return ONLY valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=max_tokens_val
                    )
                    text_result = completion.choices[0].message.content.strip()
                    print(f"[Success] Generated script via Groq ({g_model}).")
                    success_groq = True
                    break
                except Exception as e:
                    print(f"[Note] Groq model '{g_model}' attempt {attempt+1} failed ({e})")
                    time.sleep(3)
            if success_groq:
                try:
                    return parse_json_safely(text_result)
                except Exception as jde:
                    print(f"[Warning] Groq JSON output was truncated/invalid ({jde}), trying next model...")
                    text_result = None
                    continue

    # 3. Try Local Ollama second fallback
    if not text_result and ollama_client:
        try:
            print("[Info] Generating script using Local Ollama (llama3)...")
            completion = ollama_client.chat.completions.create(
                model="llama3",
                messages=[
                    {"role": "system", "content": "You are a professional YouTube scriptwriter and JSON generator. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens_val
            )
            text_result = completion.choices[0].message.content.strip()
            print("[Success] Generated script via Local Ollama.")

            try:
                return parse_json_safely(text_result)
            except Exception as jde:
                print(f"[Warning] Local Ollama JSON output was truncated/invalid ({jde}), falling back to OpenAI...")
                text_result = None
        except Exception as e:
            print(f"[Note] Local Ollama generation failed ({e}), falling back to OpenAI...")
            text_result = None

    # 4. Fallback to OpenAI GPT-4o-mini if others failed
    if not text_result and openai_client:
        try:
            print("[Info] Generating script using OpenAI (gpt-4o-mini)...")
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional YouTube scriptwriter and JSON generator. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens_val
            )
            text_result = completion.choices[0].message.content.strip()
            print("[Success] Generated script via OpenAI.")

            try:
                return parse_json_safely(text_result)
            except Exception as jde:
                print(f"[Warning] OpenAI JSON output was truncated/invalid ({jde}).")
                text_result = None
        except Exception as e:
            print(f"[Note] OpenAI generation failed ({e})")
            text_result = None

    if not text_result:
        raise RuntimeError("All LLM providers (Gemini, Groq, Ollama, OpenAI) reached quota limits or failed.")

    return parse_json_safely(text_result)

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
    Generate one unique, highly catchy, and viral YouTube video topic strictly under this category: "{category_prompt}".
    The topic must be focused strictly on physical geography, earth wonders, nature, places, landmarks, mysteries of nature, maps, or geographical anomalies on Earth. 
    STRICTLY FORBIDDEN: Do NOT generate topics about space, astronomy, planets, stars, galaxies, psychology, dark psychology, human brain, mind control, or human behavior unless the category explicitly asks for it.
    The topic must be fresh, intriguing, and written entirely in {language}.
    {exclusion_list_str}
    Return ONLY the topic title as a plain string, with no extra formatting, quotes, or markdown.
    """

    topic_text = None

    # 1. Try Gemini first as primary provider
    if not topic_text and GEMINI_API_KEY:
        model_names = [
            "gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-flash-latest",
            "gemini-pro-latest"
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

    # 2. Try Groq as first fallback
    if not topic_text and groq_client:
        groq_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-90b-vision-preview"]
        import time
        for g_model in groq_models:
            success = False
            for attempt in range(2):
                try:
                    completion = groq_client.chat.completions.create(
                        model=g_model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.85,
                        max_tokens=100
                    )
                    topic_text = completion.choices[0].message.content.strip()
                    success = True
                    break
                except Exception:
                    time.sleep(2)
            if success and topic_text:
                break

    # 3. Try Local Ollama as second fallback
    if not topic_text and ollama_client:
        try:
            completion = ollama_client.chat.completions.create(
                model="llama3",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
                max_tokens=100
            )
            topic_text = completion.choices[0].message.content.strip()
        except Exception:
            pass

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
