import os  # 標準ライブラリ

from PIL import Image, ImageDraw, ImageFont  # サードパーティライブラリ

# Constants
BG_COLOR = "#000000"  # Terminal black
TEXT_COLOR = "#FFFFFF"  # Terminal white
FONT_SIZE = 14
LINE_HEIGHT = 20
PADDING = 20
IMAGES_DIR = "images"


def create_cui_image():
    """
    Generates a screenshot of a simulated CUI Tic Tac Toe game.
    """
    # Simulated terminal output based on CUI/cui_display.py
    # Let's simulate a mid-game state
    lines = [
        "$ python3 CUI/client.py",
        "",
        "--- Tic Tac Toe Board ---",
        "| X | 2 | 3 |",
        "| 4 | O | 6 |",
        "| 7 | 8 | 9 |",
        "-------------------------",
        "",
        "Current Player: X",
        "Enter your move (1-9): "
    ]

    # Calculate image size

    width = 400
    height = len(lines) * LINE_HEIGHT + 2 * PADDING

    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        # Try to use a monospace font
        # MacOS usually has Menlo or Monaco
        font = ImageFont.truetype("Menlo.ttc", FONT_SIZE)
    except IOError:
        try:
            font = ImageFont.truetype("Courier New.ttf", FONT_SIZE)
        except IOError:
            font = ImageFont.load_default()

    y = PADDING
    for line in lines:
        draw.text((PADDING, y), line, fill=TEXT_COLOR, font=font)
        y += LINE_HEIGHT

    # Add a "cursor" block at the end

    cursor_x = PADDING + draw.textlength(lines[-1], font=font)
    draw.rectangle([(cursor_x, y - LINE_HEIGHT + 2),
                    (cursor_x + 8, y - 2)], fill=TEXT_COLOR)

    output_path = os.path.join(IMAGES_DIR, "cui_screenshot.png")
    img.save(output_path)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    create_cui_image()
