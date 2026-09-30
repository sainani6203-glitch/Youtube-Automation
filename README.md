# OmniDaily YouTube Automation Pipeline

This project is a fully engineered, automated YouTube video generation system for the **OmniDaily** channel. It creates daily multi-topic hybrid content (2 Shorts + 1 Long Video daily) with AI scripts, text-to-speech voiceovers, Pexels stock footage, and direct YouTube auto-upload.

---

## 🛠️ Project Structure
- `config.py`: Central configuration, topic schedule (Monday to Sunday categories), and paths.
- `script_generator.py`: Generates viral scripts & metadata using the Gemini API (with robust model fallback).
- `tts_engine.py`: Synthesizes studio-quality voiceovers using `edge-tts`.
- `media_fetcher.py`: Fetches high-definition stock video clips from the Pexels API.
- `video_renderer.py`: Assembles audio, clips, and captions into final MP4 videos using `MoviePy` (MoviePy v2.x compatible).
- `youtube_uploader.py`: Connects to YouTube Data API v3 for automated video uploading.
- `main.py`: Orchestrates individual video generation.
- `run_daily_batch.py`: Orchestrates the daily hybrid batch (2 Shorts + 1 Long).
- `run_omnidaily.bat`: 1-click batch runner shortcut.

---

## 🚀 How to Setup & Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables (`.env`)
```env
GEMINI_API_KEY=your_gemini_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
AUTOMATION_MODE=fully-automated
```

### 3. YouTube API Credentials
Place your `client_secret.json` from Google Cloud Console in the project root.

### 4. Run Batch
Double-click `run_omnidaily.bat` or run:
```bash
python run_daily_batch.py
```
