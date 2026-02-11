"""
Step 7 — Auto Thumbnail Generation using Pillow.
Creates a bold, text-overlay thumbnail from the first downloaded image.
"""

import os
from PIL import Image, ImageDraw, ImageFont

IMAGES_DIR = os.path.join("assets", "images")
OUTPUT_PATH = os.path.join("assets", "video", "thumbnail.jpg")

# YouTube recommended thumbnail size
THUMB_WIDTH = 1280
THUMB_HEIGHT = 720


def create_thumbnail(
    title: str,
    image_path: str = None,
    output_path: str = OUTPUT_PATH,
) -> str:
    """
    Generate a YouTube thumbnail:
    1. Load background image (first downloaded image by default)
    2. Apply dark overlay for text contrast
    3. Draw bold title text centered on the image
    """
    # Pick background image
    if image_path is None:
        image_path = os.path.join(IMAGES_DIR, "img0.jpg")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Open and resize to thumbnail dimensions
    img = Image.open(image_path).convert("RGB")
    img = img.resize((THUMB_WIDTH, THUMB_HEIGHT), Image.LANCZOS)

    # Apply semi-transparent dark overlay for contrast
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 140))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")

    draw = ImageDraw.Draw(img)

    # Try to use a bold font; fall back to default
    font_size = 72
    font = None
    for font_name in ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"]:
        try:
            font = ImageFont.truetype(font_name, font_size)
            break
        except (IOError, OSError):
            continue

    if font is None:
        font = ImageFont.load_default()

    # Word-wrap the title text
    max_chars_per_line = 25
    words = title.upper().split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) <= max_chars_per_line:
            current_line = (current_line + " " + word).strip()
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Calculate total text height
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])

    total_text_height = sum(line_heights) + (len(lines) - 1) * 15  # 15px line spacing
    y_start = (THUMB_HEIGHT - total_text_height) // 2

    # Draw each line centered with a shadow effect
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (THUMB_WIDTH - text_width) // 2
        y = y_start + sum(line_heights[:i]) + i * 15

        # Shadow
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0))
        # Main text
        draw.text((x, y), line, font=font, fill=(255, 255, 255))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    print(f"[Thumbnail] Saved → {output_path}")
    return output_path


if __name__ == "__main__":
    title = input("Enter thumbnail title: ")
    create_thumbnail(title)
