import os  # 標準ライブラリ

from PIL import Image, ImageDraw, ImageFont  # サードパーティライブラリ

# Constants matching gui.py and board_drawer.py
BG_COLOR = "#333333"
LINE_COLOR = "white"
LINE_WIDTH = 3
X_COLOR = "red"
O_COLOR = "blue"
SYMBOL_WIDTH = 5
WIN_HIGHLIGHT_COLOR = "yellow"
CANVAS_SIZE = 300
CELL_SIZE = 100
PADDING = 10


IMAGES_DIR = "images"


def draw_board(draw):
    """
    Draws the Tic Tac Toe grid lines on the given ImageDraw object.

    Args:
        draw (ImageDraw.Draw): The drawing context.
    """
    # Draw grid lines
    for i in range(1, 3):
        # Vertical
        draw.line([(i * CELL_SIZE, 0), (i * CELL_SIZE, CANVAS_SIZE)],
                  fill=LINE_COLOR, width=LINE_WIDTH)
        # Horizontal
        draw.line([(0, i * CELL_SIZE), (CANVAS_SIZE, i * CELL_SIZE)],
                  fill=LINE_COLOR, width=LINE_WIDTH)


def draw_x(draw, row, col):
    """
    Draws an 'X' symbol on the board at the specified row and column.

    Args:
        draw (ImageDraw.Draw): The drawing context.
        row (int): The row index (0-2).
        col (int): The column index (0-2).
    """
    x1 = col * CELL_SIZE + PADDING
    y1 = row * CELL_SIZE + PADDING
    x2 = (col + 1) * CELL_SIZE - PADDING
    y2 = (row + 1) * CELL_SIZE - PADDING
    draw.line([(x1, y1), (x2, y2)], fill=X_COLOR, width=SYMBOL_WIDTH)
    draw.line([(x1, y2), (x2, y1)], fill=X_COLOR, width=SYMBOL_WIDTH)


def draw_o(draw, row, col):
    """
    Draws an 'O' symbol on the board at the specified row and column.

    Args:
        draw (ImageDraw.Draw): The drawing context.
        row (int): The row index (0-2).
        col (int): The column index (0-2).
    """
    x1 = col * CELL_SIZE + PADDING
    y1 = row * CELL_SIZE + PADDING
    x2 = (col + 1) * CELL_SIZE - PADDING
    y2 = (row + 1) * CELL_SIZE - PADDING
    draw.ellipse([(x1, y1), (x2, y2)], outline=O_COLOR, width=SYMBOL_WIDTH)


def create_base_image():
    """
    Creates a new blank image for the Tic Tac Toe board.

    Returns:
        PIL.Image.Image: A new blank image.
    """
    return Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), BG_COLOR)


def generate_gameplay_screenshot():
    """
    Generates a screenshot of a Tic Tac Toe game in progress.
    """
    img = create_base_image()
    draw = ImageDraw.Draw(img)
    draw_board(draw)

    # Simulate some moves
    # X in (0, 0)
    draw_x(draw, 0, 0)
    # O in (1, 1)
    draw_o(draw, 1, 1)
    # X in (2, 2)
    draw_x(draw, 2, 2)
    # O in (0, 2)
    draw_o(draw, 0, 2)

    # Add a "window" frame simulation (optional, but good for context)
    # For now, just the board is fine as per request "GUI app screenshots" usually implies the window,
    # but the board is the main part. Let's add a small title bar simulation.

    window_img = Image.new("RGB", (320, 380), BG_COLOR)  # Extra height for title and label
    draw_win = ImageDraw.Draw(window_img)

    # Title bar
    draw_win.rectangle([(0, 0), (320, 30)], fill="#222222")
    # draw_win.text((10, 8), "三目並べ", fill="white") # Font might be an issue, skipping text on title bar

    # Paste board
    window_img.paste(img, (10, 40))

    window_img.save(os.path.join(IMAGES_DIR, "gui_screenshot_gameplay.png"))
    print("Generated gui_screenshot_gameplay.png")


def generate_win_screenshot():
    """
    Generates a screenshot of a Tic Tac Toe game with a winning state highlighted.
    """
    img = create_base_image()
    draw = ImageDraw.Draw(img)

    # Highlight winner cells (X wins on left column)
    winner_line = [(0, 0), (1, 0), (2, 0)]
    for row, col in winner_line:
        x1 = col * CELL_SIZE
        y1 = row * CELL_SIZE
        x2 = (col + 1) * CELL_SIZE
        y2 = (row + 1) * CELL_SIZE
        draw.rectangle([(x1, y1), (x2, y2)], fill=WIN_HIGHLIGHT_COLOR)

    draw_board(draw)

    # Moves
    # X wins on col 0
    draw_x(draw, 0, 0)
    draw_x(draw, 1, 0)
    draw_x(draw, 2, 0)

    # O moves
    draw_o(draw, 0, 1)
    draw_o(draw, 1, 1)

    window_img = Image.new("RGB", (320, 380), BG_COLOR)
    draw_win = ImageDraw.Draw(window_img)

    # Title bar
    draw_win.rectangle([(0, 0), (320, 30)], fill="#222222")

    # Paste board
    window_img.paste(img, (10, 40))

    # Result label
    try:
        # Try to load a font, otherwise default
        font = ImageFont.truetype("Arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    # Draw text "X wins!" (Simplified for font compatibility)
    text = "X wins!"

    # Simple positioning
    draw_win.text((120, 350), text, fill="yellow", font=font)

    window_img.save(os.path.join(IMAGES_DIR, "gui_screenshot_win.png"))
    print("Generated gui_screenshot_win.png")


if __name__ == "__main__":
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    generate_gameplay_screenshot()
    generate_win_screenshot()
