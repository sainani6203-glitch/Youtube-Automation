# YouTube Automation Project (`Youtube-Automation`)

## Architecture & Pipeline
- **Core Purpose**: Fully automated daily generation and publishing of YouTube videos (2 Long Videos + 10 Shorts daily across 2 channels: Telugu & Hindi).
- **Modules**:
  - `main.py`: Core pipeline orchestration (script generation, voiceover, stock footage fetching, video rendering, and YouTube uploading).
  - `script_generator.py`: Generates scripts using Google Gemini API (`google-generativeai`) & Groq, with dynamic topic history tracking (`topic_history.json`).
  - `tts_engine.py`: Generates neural voiceovers and `.srt` subtitles using `edge-tts`.
  - `media_fetcher.py`: Downloads stock footage from Pexels API (`requests`).
  - `video_renderer.py`: Renders final MP4 videos using `moviepy`.
  - `thumbnail_generator.py`: Generates high-CTR cinematic thumbnails using Playwright.
  - `youtube_uploader.py`: Uploads videos and subtitles to YouTube using YouTube Data API v3 (`google-api-python-client`, OAuth2) supporting multi-language tokens (`token.pickle` & `token_hindi.pickle`).
  - `run_daily_batch.py`: Orchestrates the daily multi-language batch.

## Server Deployment (Contabo Performance VPS)
- **Host**: Contabo Performance VPS (Cloud VPS Plus 6 - 6 vCPU AMD EPYC, 12 GB RAM, 300 GB NVMe SSD).
- **IP Address**: `169.58.25.200`
- **OS**: Ubuntu 24.04.5 LTS
- **Automation Schedule**: Cron job configured to run daily at **2:00 AM IST** (`30 20 * * *`), which automatically performs `git pull origin main` to sync latest code updates before executing `run_daily_batch.py`.
- **Log File**: `/var/log/youtube_automation.log`

## GitHub Actions Workflow
- **File**: `.github/workflows/daily_video.yml`
- **Schedule/Trigger**: Manual trigger via `workflow_dispatch`.
- **Secrets Required**:
  - `GEMINI_API_KEY`
  - `PEXELS_API_KEY`
  - `YOUTUBE_CLIENT_SECRET_B64`: Base64-encoded `client_secret.json` for YouTube OAuth.
  - `YOUTUBE_TOKEN_B64`: Base64-encoded `token.pickle` for YouTube OAuth token persistence.
  - `YOUTUBE_TOKEN_HINDI_B64`: Base64-encoded `token_hindi.pickle` for Hindi YouTube OAuth.
