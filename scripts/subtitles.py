"""
Step 6 — Subtitles: generate .srt with Whisper and burn into video with FFmpeg.
Uses OpenAI Whisper (free, local) for speech-to-text.
"""

import subprocess
import os
import shutil

AUDIO_PATH = os.path.join("assets", "audio", "voice.mp3")
VIDEO_INPUT = os.path.join("assets", "video", "final.mp4")
VIDEO_OUTPUT = os.path.join("assets", "video", "final_subtitled.mp4")
SRT_OUTPUT = os.path.join("assets", "audio", "voice.srt")


def generate_srt(audio_path: str = AUDIO_PATH, output_dir: str = None) -> str:
    """
    Run Whisper on the audio file to produce an .srt subtitle file.
    Returns the path to the generated .srt file.
    """
    if output_dir is None:
        output_dir = os.path.dirname(audio_path)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    # Check if whisper CLI is available
    whisper_cmd = shutil.which("whisper")
    if whisper_cmd is None:
        # Try using the Python module directly
        print("[Subtitles] whisper CLI not found, using Python module...")
        return _generate_srt_python(audio_path, output_dir)

    cmd = [
        "whisper",
        audio_path,
        "--model", "tiny",
        "--output_format", "srt",
        "--output_dir", output_dir,
        "--language", "en",
    ]

    print(f"[Subtitles] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Whisper names the file based on input filename
    base = os.path.splitext(os.path.basename(audio_path))[0]
    srt_path = os.path.join(output_dir, f"{base}.srt")

    if os.path.exists(srt_path):
        print(f"[Subtitles] SRT generated → {srt_path}")
        return srt_path
    else:
        raise FileNotFoundError(f"Expected SRT file not found: {srt_path}")


def _generate_srt_python(audio_path: str, output_dir: str) -> str:
    """Fallback: use whisper Python API directly."""
    import whisper

    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path, language="en")

    base = os.path.splitext(os.path.basename(audio_path))[0]
    srt_path = os.path.join(output_dir, f"{base}.srt")

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], 1):
            start = _format_timestamp(seg["start"])
            end = _format_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    print(f"[Subtitles] SRT generated → {srt_path}")
    return srt_path


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def burn_subtitles(
    video_input: str = VIDEO_INPUT,
    srt_path: str = SRT_OUTPUT,
    video_output: str = VIDEO_OUTPUT,
) -> str:
    """
    Burn .srt subtitles into the video using FFmpeg.
    Returns the path to the subtitled video.
    """
    if not os.path.exists(video_input):
        raise FileNotFoundError(f"Video not found: {video_input}")
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"SRT not found: {srt_path}")

    # FFmpeg requires forward slashes or escaped backslashes in subtitle paths
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_input,
        "-vf", f"subtitles='{srt_escaped}':force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2'",
        "-c:a", "copy",
        video_output,
    ]

    print(f"[Subtitles] Burning subtitles into video...")
    subprocess.run(cmd, check=True)
    print(f"[Subtitles] Subtitled video → {video_output}")
    return video_output


if __name__ == "__main__":
    srt = generate_srt()
    burn_subtitles(srt_path=srt)
