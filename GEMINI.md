# YouTube Automation Project (`Youtube-Automation`)

## Architecture & Pipeline
- **Core Purpose**: Fully automated daily generation and publishing of YouTube videos (1 long video + 2 shorts daily).
- **Modules**:
  - `main.py`: Core pipeline orchestration (script generation, voiceover, stock footage fetching, video rendering, and YouTube uploading).
  - `script_generator.py`: Generates scripts using Google Gemini API (`google-generativeai`).
  - `tts_engine.py`: Generates neural voiceovers and `.srt` subtitles using `edge-tts`.
  - `media_fetcher.py`: Downloads stock footage from Pexels API (`requests`).
  - `video_renderer.py`: Renders final MP4 videos using `moviepy`.
  - `youtube_uploader.py`: Uploads videos and subtitles to YouTube using YouTube Data API v3 (`google-api-python-client`, OAuth2).
  - `run_daily_batch.py`: Orchestrates the daily batch of 3 videos.

## GitHub Actions Workflow
- **File**: `.github/workflows/daily_video.yml`
- **Schedule**: Daily at 9:00 AM IST (`30 3 * * *`) and `workflow_dispatch` (manual trigger).
- **Secrets Required**:
  - `GEMINI_API_KEY`
  - `PEXELS_API_KEY`
  - `YOUTUBE_CLIENT_SECRET_B64`: Base64-encoded `client_secret.json` for YouTube OAuth.
  - `YOUTUBE_TOKEN_B64`: Base64-encoded `token.pickle` for YouTube OAuth token persistence.
- **Credential Setup in CI**: Automatically decoded into `client_secret.json` and `token.pickle` during the workflow run before executing `run_daily_batch.py`.
