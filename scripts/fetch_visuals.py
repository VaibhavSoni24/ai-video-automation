"""
Step 4 — Fetch Visuals from Pexels (free API).
Downloads high-quality stock images to use as video backgrounds.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

IMAGES_DIR = os.path.join("assets", "images")


def fetch_images(query: str, count: int = 6) -> list[str]:
    """
    Search Pexels for `query` and download `count` images.
    Returns list of saved file paths.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY not found in environment variables.")

    headers = {"Authorization": api_key}
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "per_page": count, "orientation": "landscape"}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    photos = response.json().get("photos", [])
    if not photos:
        print(f"[Visuals] No photos found for '{query}', trying fallback...")
        # Fallback to a generic search
        params["query"] = "nature landscape"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        photos = response.json().get("photos", [])

    os.makedirs(IMAGES_DIR, exist_ok=True)
    saved = []

    for i, photo in enumerate(photos[:count]):
        img_url = photo["src"]["large"]  # Higher quality than 'medium'
        img_data = requests.get(img_url, timeout=30).content
        filepath = os.path.join(IMAGES_DIR, f"img{i}.jpg")
        with open(filepath, "wb") as f:
            f.write(img_data)
        saved.append(filepath)
        print(f"[Visuals] Downloaded img{i}.jpg  ({photo['src']['large']})")

    return saved


def fetch_images_for_keywords(keywords: list[str]) -> list[str]:
    """
    Download one image per keyword (up to 6 total).
    Gives more variety than searching a single term.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY not found in environment variables.")

    headers = {"Authorization": api_key}
    url = "https://api.pexels.com/v1/search"
    os.makedirs(IMAGES_DIR, exist_ok=True)
    saved = []

    for i, keyword in enumerate(keywords[:6]):
        params = {"query": keyword, "per_page": 1, "orientation": "landscape"}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            photos = response.json().get("photos", [])
            if photos:
                img_url = photos[0]["src"]["large"]
                img_data = requests.get(img_url, timeout=30).content
                filepath = os.path.join(IMAGES_DIR, f"img{i}.jpg")
                with open(filepath, "wb") as f:
                    f.write(img_data)
                saved.append(filepath)
                print(f"[Visuals] img{i}.jpg ← '{keyword}'")
            else:
                print(f"[Visuals] No result for '{keyword}', skipping.")
        except Exception as e:
            print(f"[Visuals] Error fetching '{keyword}': {e}")

    return saved


def fetch_images_for_scenes(scene_descriptions: list[str]) -> list[str]:
    """
    Download one image per scene description.
    Each description comes from Gemini's scene breakdown of the script,
    so the images directly match the video's visual narrative.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY not found in environment variables.")

    headers = {"Authorization": api_key}
    url = "https://api.pexels.com/v1/search"
    os.makedirs(IMAGES_DIR, exist_ok=True)
    saved = []

    for i, description in enumerate(scene_descriptions):
        params = {"query": description, "per_page": 1, "orientation": "landscape"}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            photos = response.json().get("photos", [])

            if not photos:
                # Simplify the query by taking the first 3 words as fallback
                short_query = " ".join(description.split()[:3])
                print(f"[Visuals] No result for scene {i+1}, retrying with '{short_query}'...")
                params["query"] = short_query
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                photos = response.json().get("photos", [])

            if photos:
                img_url = photos[0]["src"]["large"]
                img_data = requests.get(img_url, timeout=30).content
                filepath = os.path.join(IMAGES_DIR, f"img{i}.jpg")
                with open(filepath, "wb") as f:
                    f.write(img_data)
                saved.append(filepath)
                print(f"[Visuals] img{i}.jpg ← Scene {i+1}: '{description}'")
            else:
                print(f"[Visuals] No image found for scene {i+1}: '{description}', skipping.")
        except Exception as e:
            print(f"[Visuals] Error fetching scene {i+1} '{description}': {e}")

    return saved


if __name__ == "__main__":
    query = input("Search query: ")
    fetch_images(query)
