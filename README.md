# AI-Powered YouTube Automation Pipeline

Fully automated YouTube content pipeline that generates and uploads videos without manual intervention. Creates daily Shorts and weekly long-form videos using Python, n8n, and free-tier AI tools.

## Features

- 🤖 **Fully Autonomous** - Generates topics, scripts, voiceovers, visuals, subtitles, and thumbnails
- 📱 **Automated Shorts** - Daily YouTube Shorts (portrait 9:16)
- 🎬 **Automated Videos** - Weekly long-form content (landscape 16:9)
- 💰 **Free Tools Only** - Uses Gemini, Edge TTS, Pexels, and Whisper
- 🔄 **Scheduled Execution** - n8n-based automation with cron scheduling
- 🧹 **Auto Cleanup** - Isolated run directories with automatic cleanup

## How It Works

```
n8n Scheduler → Gemini Topic Generation → Flask API → Python Pipeline → YouTube Upload
```

**Pipeline Steps:**
1. **Script Generation** - AI creates video script (Gemini)
2. **Voiceover** - Text-to-speech conversion (Edge TTS)
3. **Visual Fetching** - Scene-based image selection (Pexels)
4. **Video Composition** - Combine images + audio (MoviePy + FFmpeg)
5. **Subtitles** - Auto-generate and burn subtitles (Whisper)
6. **Thumbnail** - Generate thumbnail for videos
7. **Upload** - Publish to YouTube with metadata (YouTube Data API v3)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 3. Configure API Keys

Create `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
PEXELS_API_KEY=your_pexels_api_key
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
```

**Get API Keys:**
- [Gemini API](https://aistudio.google.com/app/apikey)
- [Pexels API](https://www.pexels.com/api/)
- [YouTube API](https://console.cloud.google.com/) (OAuth2 credentials)

### 4. YouTube OAuth

First run opens browser for OAuth2 consent. Credentials cached in `token.json`.

### 5. Setup n8n (Optional - for automation)

```bash
docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

Access at `http://localhost:5678` and import [n8n/YouTube Automation.json](n8n/YouTube%20Automation.json).

## Usage

### Interactive Mode

```bash
python main.py
```

Prompts for topic, format, upload settings, and privacy.

### CLI Mode

```bash
python main.py "Why black holes bend time" short true public
```

**Arguments:** `topic`, `format` (short/video), `upload` (true/false), `privacy` (public/private/unlisted)

### API Mode (Automation)

Start server:

```bash
python server.py
```

Make requests:

```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{"topic":"How AI works","format":"short","upload":true,"privacy":"public"}'
```

**Response Codes:**
- `200` - Success
- `429` - Pipeline busy (thread-locked)
- `500` - Error

### Full Automation

1. Start Flask server: `python server.py`
2. Start n8n: `docker start n8n`
3. Import workflow from `n8n/YouTube Automation.json`
4. Configure endpoint: `http://host.docker.internal:5000/run` (Docker) or `http://localhost:5000/run`
5. Activate workflow

**Schedules:**
- Daily Shorts: 11:00 PM
- Weekly Videos: Sunday 11:30 PM

## Project Structure

```
ai-video-pipeline/
├── server.py              # Flask API server
├── main.py                # Pipeline orchestrator
├── requirements.txt       # Dependencies
├── scripts/               # Pipeline modules
│   ├── generate_script.py
│   ├── generate_voice.py
│   ├── fetch_visuals.py
│   ├── make_video.py
│   ├── subtitles.py
│   ├── thumbnail.py
│   └── upload_youtube.py
├── n8n/                   # Automation workflow
└── output/                # Final videos

```

## Tech Stack

- **Automation**: n8n
- **AI**: Google Gemini API
- **Voiceover**: Edge TTS
- **Visuals**: Pexels API
- **Video**: MoviePy + FFmpeg
- **Subtitles**: Whisper
- **Upload**: YouTube Data API v3
- **Backend**: Flask

## License

MIT
