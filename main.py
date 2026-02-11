"""
AI Video Pipeline — main.py
============================
One trigger (topic) → fully automated YouTube video.

Pipeline Steps:
  1. Input topic
  2. Generate script with Gemini AI
  3. Generate voiceover with Edge TTS
  4. Fetch visuals from Pexels
  5. Combine into .mp4 with MoviePy
  6. Generate subtitles with Whisper & burn with FFmpeg
  7. Create thumbnail with Pillow
  8. Upload to YouTube (optional)
"""

import os
import sys
from dotenv import load_dotenv

# ── Load environment variables ──────────────────────────────────────
load_dotenv()

# ── Import pipeline modules ─────────────────────────────────────────
from scripts.generate_script import generate_script, extract_scenes, generate_metadata
from scripts.generate_voice import make_voice
from scripts.fetch_visuals import fetch_images_for_scenes, fetch_images
from scripts.make_video import create_video
from scripts.subtitles import generate_srt, burn_subtitles
from scripts.thumbnail import create_thumbnail
from scripts.upload_youtube import upload_video
import glob


def cleanup_generated_files(final_video: str = None):
    """Delete all generated files (images, audio, script, etc.) keeping only the final video."""
    print("\n[Cleanup] Removing generated files...")

    # Remove images
    images_dir = os.path.join("assets", "images")
    if os.path.exists(images_dir):
        for file in glob.glob(os.path.join(images_dir, "*.jpg")):
            os.remove(file)
            print(f"  Deleted {file}")

    # Remove audio
    audio_file = os.path.join("assets", "audio", "voice.mp3")
    if os.path.exists(audio_file):
        os.remove(audio_file)
        print(f"  Deleted {audio_file}")

    # Remove script
    if os.path.exists("script.txt"):
        os.remove("script.txt")
        print("  Deleted script.txt")

    # Remove SRT subtitles
    srt_file = os.path.join("assets", "audio", "voice.srt")
    if os.path.exists(srt_file):
        os.remove(srt_file)
        print(f"  Deleted {srt_file}")

    # Remove intermediate video (without subtitles) and thumbnail, keep final video
    video_dir = os.path.join("assets", "video")
    if os.path.exists(video_dir):
        for file in glob.glob(os.path.join(video_dir, "*.mp4")):
            if final_video and os.path.abspath(file) == os.path.abspath(final_video):
                continue  # Keep the final video
            os.remove(file)
            print(f"  Deleted {file}")
        for file in glob.glob(os.path.join(video_dir, "*.jpg")):
            os.remove(file)
            print(f"  Deleted {file}")

    print("[Cleanup] Done.")


def run_pipeline(
    topic: str,
    upload: bool = False,
    format_type: str = "landscape",
    privacy: str = "private",
):
    """Execute the full video-generation pipeline."""

    print("=" * 60)
    print(f"  AI VIDEO PIPELINE")
    print(f"  Topic: {topic}")
    print(f"  Format: {format_type.upper()} ({'Shorts' if format_type == 'portrait' else 'Video'})")
    print(f"  Privacy: {privacy.upper()}")
    print("=" * 60)

    # ── Step 1: Generate Script ──────────────────────────────────────
    print("\n[Step 1/8] Generating script...")
    script_text = generate_script(topic, format_type=format_type)

    # Save script to file
    with open("script.txt", "w", encoding="utf-8") as f:
        f.write(script_text)
    print(f"  Script saved → script.txt ({len(script_text)} chars)")

    # ── Step 2: Split script into visual scenes ─────────────────────
    print("\n[Step 2/8] Splitting script into visual scenes...")
    scenes = extract_scenes(script_text)
    for i, scene in enumerate(scenes, 1):
        print(f"  Scene {i}: {scene}")

    # ── Step 3: Generate metadata (title, description, tags) ─────────
    print("\n[Step 3/8] Generating YouTube metadata...")
    metadata = generate_metadata(topic, script_text)
    print(f"  Title: {metadata['title']}")

    # ── Step 4: Generate Voiceover ───────────────────────────────────
    print("\n[Step 4/8] Generating voiceover...")
    make_voice(script_text)

    # ── Step 5: Fetch Visuals (one per scene) ────────────────────────
    print("\n[Step 5/8] Fetching visuals from Pexels (per scene)...")
    if scenes:
        images = fetch_images_for_scenes(scenes)
    else:
        images = fetch_images(topic)

    if not images:
        print("  WARNING: No images fetched. Using fallback.")
        images = fetch_images("nature landscape")

    # ── Step 6: Create Video ─────────────────────────────────────────
    print("\n[Step 6/8] Creating video...")
    video_path = create_video(format_type=format_type)

    # ── Step 7: Subtitles ────────────────────────────────────────────
    print("\n[Step 7/8] Generating subtitles...")
    try:
        srt_path = generate_srt()
        final_video = burn_subtitles(srt_path=srt_path)
    except Exception as e:
        print(f"  Subtitle generation failed: {e}")
        print("  Continuing without subtitles...")
        final_video = video_path

    # ── Step 7b: Generate Thumbnail (skip for Shorts) ────────────────
    thumbnail_path = None
    if format_type == "landscape":
        print("\n[Step 7b] Creating thumbnail...")
        try:
            thumbnail_path = create_thumbnail(metadata["title"], format_type=format_type)
        except Exception as e:
            print(f"  Thumbnail generation failed: {e}")
            thumbnail_path = None
    else:
        print("\n[Step 7b] Skipping thumbnail (not needed for Shorts).")

    # ── Step 8: Upload to YouTube (optional) ─────────────────────────
    if upload:
        is_short = (format_type == "portrait")
        print(f"\n[Step 8/8] Uploading to YouTube {'Shorts' if is_short else ''}...")
        try:
            video_id = upload_video(
                video_path=final_video,
                title=metadata["title"],
                description=metadata["description"],
                tags=metadata["tags"],
                thumbnail_path=thumbnail_path,
                privacy=privacy,
                is_short=is_short,
            )
            print(f"\n  YouTube URL: https://youtube.com/watch?v={video_id}")
        except Exception as e:
            print(f"  Upload failed: {e}")
            print("  Video saved locally — you can upload manually.")
    else:
        print("\n[Step 8/8] Skipping upload.")

    # ── Cleanup (always, keep final video) ─────────────────────────
    cleanup_generated_files(final_video=final_video)

    # ── Done ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print(f"  Video  → {final_video}")
    if thumbnail_path:
        print(f"  Thumb  → {thumbnail_path}")
    print(f"  Script → script.txt")
    print("=" * 60)


if __name__ == "__main__":
    # ── Get topic from CLI args or prompt ────────────────────────────
    if len(sys.argv) > 1:
        args = [a for a in sys.argv[1:] if a != "--upload"]
        TOPIC = " ".join(args)
    else:
        TOPIC = input("Enter video topic: ").strip()

    if not TOPIC:
        print("Error: No topic provided.")
        sys.exit(1)

    # ── Interactive prompts (always asked) ────────────────────────────
    format_choice = input("Video type - (1) Video [landscape] or (2) Short [portrait]? (1/2): ").strip()
    format_type = "portrait" if format_choice == "2" else "landscape"

    upload_flag = input("Upload to YouTube? (y/N): ").strip().lower() == "y"

    if upload_flag:
        privacy_choice = input("Privacy - (1) Public or (2) Private? (1/2): ").strip()
        privacy = "public" if privacy_choice == "1" else "private"
    else:
        privacy = "private"

    run_pipeline(TOPIC, upload=upload_flag, format_type=format_type, privacy=privacy)
