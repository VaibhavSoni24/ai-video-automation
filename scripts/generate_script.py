"""
Step 2 — Script Generation using Google Gemini API (free tier).
Generates a 60-90 second YouTube script for a given topic.
"""

import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()


def generate_script(topic: str, format_type: str = "landscape") -> str:
    """Call Gemini API to generate a short YouTube script."""
    if format_type == "portrait":
        # Shorts: under 60 seconds → ~30-45 second script
        prompt = (
            f"Write a 30-45 second YouTube Shorts video script.\n"
            f"Topic: {topic}\n"
            f"Requirements:\n"
            f"- Maximum 30-45 seconds when read aloud\n"
            f"- Fast-paced, punchy, and attention-grabbing\n"
            f"- Include a hook in the first 3 seconds\n"
            f"- Use very short sentences suitable for voiceover\n"
            f"- Keep it concise — this is a Short, not a full video\n"
            f"- Do NOT include stage directions, timestamps, or formatting marks\n"
            f"- Just return the spoken narration text"
        )
    else:
        prompt = (
            f"Write a 60-90 second YouTube video script.\n"
            f"Topic: {topic}\n"
            f"Requirements:\n"
            f"- Clear, engaging, and educational tone\n"
            f"- Include a hook in the first 5 seconds\n"
            f"- Use short sentences suitable for voiceover\n"
            f"- Do NOT include stage directions, timestamps, or formatting marks\n"
            f"- Just return the spoken narration text"
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment variables.")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    response = requests.post(
        url,
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    try:
        script_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected Gemini response: {data}") from exc

    return script_text.strip()


def extract_keywords(topic: str, script_text: str) -> list[str]:
    """Use Gemini to pull 6 vivid image-search keywords from the script."""
    prompt = (
        f"Given this YouTube script about '{topic}':\n\n"
        f"{script_text}\n\n"
        f"Return exactly 6 short image search keywords (one per line) "
        f"that would make great background visuals for this video. "
        f"Only return the keywords, nothing else."
    )

    api_key = os.getenv("GEMINI_API_KEY")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    response = requests.post(
        url,
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    raw = data["candidates"][0]["content"]["parts"][0]["text"]
    keywords = [line.strip().strip("-•*").strip() for line in raw.splitlines() if line.strip()]
    # Clean numbering like "1. keyword"
    keywords = [re.sub(r"^\d+[\.\)]\s*", "", kw) for kw in keywords]
    return keywords[:6]


def extract_scenes(script_text: str, num_scenes: int = 6) -> list[str]:
    """
    Use Gemini to split a script into visual scenes.
    Returns a list of short image-search descriptions, one per scene.
    """
    prompt = (
        f"Split the following video script into {num_scenes} visual scenes.\n"
        f"For each scene, give a short (3-8 word) image search description "
        f"that would find a good stock photo for that part of the script.\n\n"
        f"Script:\n{script_text}\n\n"
        f"Return ONLY a JSON array of strings, nothing else. Example:\n"
        f'["student studying with laptop", "online learning dashboard"]'
    )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment variables.")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    response = requests.post(
        url,
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Parse JSON array from response (strip markdown fences if present)
    import json
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        scenes = json.loads(raw)
        if isinstance(scenes, list):
            return [str(s).strip() for s in scenes[:num_scenes]]
    except json.JSONDecodeError:
        pass

    # Fallback: treat each non-empty line as a scene description
    lines = [line.strip().strip('-•*"').strip() for line in raw.splitlines() if line.strip()]
    lines = [re.sub(r"^\d+[\.\)]\s*", "", ln) for ln in lines]
    return lines[:num_scenes]


def generate_metadata(topic: str, script_text: str) -> dict:
    """Generate YouTube title, description, and tags using Gemini."""
    prompt = (
        f"For a YouTube video about '{topic}' with this script:\n\n"
        f"{script_text[:500]}\n\n"
        f"Generate:\n"
        f"1. A catchy YouTube title (max 70 chars)\n"
        f"2. A YouTube description (2-3 sentences + relevant hashtags)\n"
        f"3. 8 comma-separated tags\n\n"
        f"Format your response EXACTLY like this:\n"
        f"TITLE: <title>\n"
        f"DESCRIPTION: <description>\n"
        f"TAGS: <tag1>, <tag2>, ..."
    )

    api_key = os.getenv("GEMINI_API_KEY")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    response = requests.post(
        url,
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    response.raise_for_status()

    raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]

    metadata = {"title": topic, "description": "", "tags": []}
    for line in raw.splitlines():
        if line.upper().startswith("TITLE:"):
            metadata["title"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("DESCRIPTION:"):
            metadata["description"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("TAGS:"):
            metadata["tags"] = [t.strip() for t in line.split(":", 1)[1].split(",")]

    return metadata


if __name__ == "__main__":
    topic = input("Enter video topic: ")
    script = generate_script(topic)
    print("\n--- Generated Script ---")
    print(script)

    keywords = extract_keywords(topic, script)
    print("\n--- Keywords ---")
    print(keywords)

    scenes = extract_scenes(script)
    print("\n--- Scenes ---")
    print(scenes)

    meta = generate_metadata(topic, script)
    print("\n--- Metadata ---")
    print(meta)
