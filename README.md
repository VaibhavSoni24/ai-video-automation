# AI Video Pipeline

Fully automated **one-trigger → one-video** pipeline. Enter a topic, get a complete YouTube video or Short with voiceover, visuals, subtitles, and thumbnail — ready to upload.

## Features

- **Landscape Videos** (1920×1080) for regular YouTube uploads
- **Portrait Videos** (1080×1920) for YouTube Shorts
- **Interactive prompts** — choose video/short, public/private, and auto-cleanup at runtime
- **Scene-based visuals** — script is split into scenes, each scene gets a matching stock image
- **Auto-cleanup** — optionally delete all generated files after successful upload
- **Public or Private** upload — choose privacy level before uploading

## Pipeline Steps

| Step | Action | Tool |
|------|--------|------|
| 1 | Generate script from topic | Google Gemini API (free) |
| 2 | Split script into visual scenes | Google Gemini API |
| 3 | Convert script to voiceover | Edge TTS (free) |
| 4 | Fetch background visuals per scene | Pexels API (free) |
| 5 | Combine into `.mp4` video | MoviePy + FFmpeg |
| 6 | Generate & burn subtitles | OpenAI Whisper + FFmpeg |
| 7 | Create thumbnail | Pillow |
| 8 | Upload to YouTube | YouTube Data API v3 |

## Project Structure

```
ai-video-pipeline/
├── scripts/
│   ├── generate_script.py   # Gemini AI script generation
│   ├── generate_voice.py    # Edge TTS voiceover
│   ├── fetch_visuals.py     # Pexels image downloader
│   ├── make_video.py        # MoviePy video composer
│   ├── subtitles.py         # Whisper STT + FFmpeg subtitle burn
│   ├── thumbnail.py         # Pillow thumbnail generator
│   └── upload_youtube.py    # YouTube Data API uploader
├── assets/
│   ├── images/              # Downloaded background images
│   ├── audio/               # Generated voiceover
│   └── video/               # Final output video
├── main.py                  # Pipeline orchestrator
├── requirements.txt
└── .env                     # API keys (not committed)
```

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 3. Configure API keys

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
PEXELS_API_KEY=your_pexels_api_key
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
```

- **Gemini API**: Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Pexels API**: Sign up at [pexels.com/api](https://www.pexels.com/api/)
- **YouTube API**: Set up OAuth2 credentials in [Google Cloud Console](https://console.cloud.google.com/)

## Usage

### Quick run (interactive)

```bash
python main.py
```

You will be prompted for:
1. **Topic** — Enter your video topic
2. **Format** — `(1) Video` (landscape 1920×1080) or `(2) Short` (portrait 1080×1920)
3. **Upload?** — Whether to upload to YouTube
4. **Privacy** — `(1) Public` or `(2) Private` (only if uploading)
5. **Cleanup** — Delete generated files after upload? (only if uploading)

### With CLI arguments

```bash
# Generate video only (no upload) — will still ask format
python main.py "5 Amazing Facts About Black Holes"

# Generate + upload to YouTube — will ask format, privacy, and cleanup
python main.py "5 Amazing Facts About Black Holes" --upload
```

### Run individual steps

```bash
python -m scripts.generate_script    # Generate script only
python -m scripts.generate_voice     # Generate voiceover only
python -m scripts.fetch_visuals      # Fetch images only
python -m scripts.make_video         # Create video only
python -m scripts.subtitles          # Generate subtitles only
python -m scripts.thumbnail          # Create thumbnail only
python -m scripts.upload_youtube     # Upload to YouTube only
```

## Output

After running the pipeline:

| File | Description |
|------|-------------|
| `script.txt` | Generated narration script |
| `assets/audio/voice.mp3` | AI voiceover |
| `assets/images/img0-5.jpg` | Background visuals |
| `assets/video/final.mp4` | Video without subtitles |
| `assets/video/final_subtitled.mp4` | Video with burned subtitles |
| `assets/video/thumbnail.jpg` | Auto-generated thumbnail |

## Notes

- First YouTube upload will open a browser for OAuth2 consent (credentials cached in `token.json`)
- **Portrait format** videos are automatically tagged as **#Shorts** on YouTube
- Choose **public** or **private** privacy when prompted before upload
- Enable **auto-cleanup** to delete all images, audio, script, and video files after successful upload
- Whisper subtitle generation requires a one-time model download (~75 MB for `tiny`)
- All APIs used are **free tier** — be mindful of rate limits
