"""
Step 5 — Create Video (.mp4) from images + voiceover using MoviePy.
Combines downloaded images with the generated voice narration.
"""

import os
import glob

# Pillow 10+ removed ANTIALIAS; MoviePy 1.0.3 still references it.
from PIL import Image
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
)

IMAGES_DIR = os.path.join("assets", "images")
AUDIO_PATH = os.path.join("assets", "audio", "voice.mp3")
OUTPUT_PATH = os.path.join("assets", "video", "final.mp4")

# Standard YouTube resolutions
RESOLUTIONS = {
    "landscape": (1920, 1080),  # 16:9 for regular videos
    "portrait": (1080, 1920),   # 9:16 for Shorts
}

TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080


def _resize_image_clip(clip, target_width, target_height):
    """Resize and pad/crop an image clip to target dimensions."""
    w, h = clip.size
    # Scale to cover the target area
    scale = max(target_width / w, target_height / h)
    clip = clip.resize(newsize=(int(w * scale), int(h * scale)))
    # Center-crop to exact target
    clip = clip.crop(
        x_center=clip.w / 2,
        y_center=clip.h / 2,
        width=target_width,
        height=target_height,
    )
    return clip


def create_video(
    images_dir: str = IMAGES_DIR,
    audio_path: str = AUDIO_PATH,
    output_path: str = OUTPUT_PATH,
    format_type: str = "landscape",
) -> str:
    """
    Build the final video:
    1. Load voice audio to determine total duration
    2. Load images, resize to target resolution, distribute evenly across duration
    3. Concatenate and attach audio
    4. Export as .mp4

    format_type: "landscape" (1920×1080) or "portrait" (1080×1920 for Shorts)
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Get target dimensions based on format
    target_width, target_height = RESOLUTIONS.get(format_type, RESOLUTIONS["landscape"])
    print(f"[Video] Format: {format_type} ({target_width}×{target_height})")

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # Collect images sorted by name
    image_files = sorted(glob.glob(os.path.join(images_dir, "img*.jpg")))
    if not image_files:
        raise FileNotFoundError(f"No images found in {images_dir}")

    num_images = len(image_files)
    per_image_duration = total_duration / num_images

    print(f"[Video] Audio duration: {total_duration:.1f}s")
    print(f"[Video] {num_images} images × {per_image_duration:.1f}s each")

    clips = []
    for img_path in image_files:
        clip = ImageClip(img_path).set_duration(per_image_duration)
        clip = _resize_image_clip(clip, target_width, target_height)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger="bar",
    )

    # Cleanup
    audio.close()
    for c in clips:
        c.close()
    video.close()

    print(f"[Video] Saved → {output_path}")
    return output_path


if __name__ == "__main__":
    create_video()
