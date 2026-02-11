"""
Step 3 — Voiceover Generation using Edge TTS (Microsoft, free).
Converts script text to high-quality speech audio.
"""

import edge_tts
import asyncio
import os

VOICE = "en-IN-NeerjaNeural"  # Free, clear Indian-English voice
OUTPUT_PATH = os.path.join("assets", "audio", "voice.mp3")


async def _make_voice(text: str, output_path: str = OUTPUT_PATH, voice: str = VOICE):
    """Async helper — synthesize speech and save to file."""
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(output_path)
    print(f"[Voice] Saved voiceover → {output_path}")


def make_voice(text: str, output_path: str = OUTPUT_PATH, voice: str = VOICE):
    """Public sync wrapper around the async Edge-TTS call."""
    asyncio.run(_make_voice(text, output_path, voice))


if __name__ == "__main__":
    script_path = "script.txt"
    if not os.path.exists(script_path):
        print(f"'{script_path}' not found. Run generate_script.py first.")
    else:
        with open(script_path, "r", encoding="utf-8") as f:
            script_text = f.read()
        make_voice(script_text)
