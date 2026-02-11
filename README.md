# AI Video Pipeline

Fully automated **one-trigger → one-video** pipeline. Enter a topic, get a complete YouTube video or Short with voiceover, visuals, subtitles, and thumbnail — ready to upload.

## Features

- **Landscape Videos** (1920×1080, 60-90s) for regular YouTube uploads
- **Portrait Shorts** (1080×1920, under 60s) for YouTube Shorts
- **Interactive prompts** — choose video/short, upload, and public/private at runtime
- **Scene-based visuals** — script is split into scenes, each scene gets a matching stock image from Pexels
- **Auto-cleanup** — generated files (images, audio, script, SRT) are automatically deleted after the pipeline finishes, keeping only the final subtitled video
- **Public or Private** upload — choose privacy level before uploading (only asked when uploading)
- **Smart thumbnails** — auto-generated for landscape videos, skipped for Shorts

## Pipeline Steps

| Step | Action | Tool |
|------|--------|------|
| 1 | Generate script (60-90s for video, 30-45s for Shorts) | Google Gemini API (free) |
| 2 | Split script into visual scenes | Google Gemini API |
| 3 | Generate YouTube metadata (title, description, tags) | Google Gemini API |
| 4 | Convert script to voiceover | Edge TTS (free) |
| 5 | Fetch background visuals per scene | Pexels API (free) |
| 6 | Combine into `.mp4` video | MoviePy + FFmpeg |
| 7 | Generate & burn subtitles | OpenAI Whisper + FFmpeg |
| 7b | Create thumbnail (landscape only) | Pillow |
| 8 | Upload to YouTube (optional) | YouTube Data API v3 |

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
4. **Privacy** — `(1) Public` or `(2) Private` (only asked if uploading)

### With CLI arguments

```bash
# Pass topic as argument — will still ask format, upload, and privacy
python main.py "5 Amazing Facts About Black Holes"
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

After the pipeline completes, all intermediate files are automatically cleaned up.
Only the final video is kept:

| File | Description |
|------|-------------|
| `assets/video/final_subtitled.mp4` | Final video with burned subtitles |

## Notes

- First YouTube upload will open a browser for OAuth2 consent (credentials cached in `token.json` for future runs)
- **Shorts** are automatically kept under 60 seconds with a shorter script (30-45s)
- **Portrait format** videos are automatically tagged with **#Shorts** on YouTube
- Choose **public** or **private** privacy when prompted (only if uploading)
- Thumbnail generation is **skipped for Shorts** (YouTube auto-generates one)
- All intermediate files (images, audio, script, SRT, thumbnail) are **auto-deleted** after the pipeline — only the final video is preserved
- Whisper subtitle generation requires a one-time model download (~75 MB for `tiny`)
- All APIs used are **free tier** — be mindful of rate limits
