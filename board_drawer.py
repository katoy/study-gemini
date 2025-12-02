class BoardDrawer:
    """
    Class for drawing the game board.
    """

    def __init__(self, gui, canvas):
        self.gui = gui
        self.canvas = canvas
        self.create_board_lines()

    def create_board_lines(self):
        """Draws the lines of the board."""
        for i in range(1, 3):
            self.canvas.create_line(i * 100, 0, i * 100, 300, fill="white", width=3)
            self.canvas.create_line(0, i * 100, 300, i * 100, fill="white", width=3)

    def draw_board(self):
        """Draws the current state of the board."""
        self.canvas.delete("all")
        self.remove_winner_highlight()
        self.create_board_lines()
        for i in range(3):
            for j in range(3):
                x1, y1 = j * 100 + 10, i * 100 + 10
                x2, y2 = (j + 1) * 100 - 10, (i + 1) * 100 - 10
                if self.gui.game.board[i][j] == "X":
                    self.draw_x(x1, y1, x2, y2)
                elif self.gui.game.board[i][j] == "O":
                    self.draw_o(x1, y1, x2, y2)

    def draw_x(self, x1, y1, x2, y2):
        """Draws an 'X' on the canvas."""
        self.canvas.create_line(x1, y1, x2, y2, fill="red", width=5)
        self.canvas.create_line(x1, y2, x2, y1, fill="red", width=5)

    def draw_o(self, x1, y1, x2, y2):
        """Draws an 'O' on the canvas."""
        self.canvas.create_oval(x1, y1, x2, y2, outline="blue", width=5)

    def highlight_winner_cells(self, winner_line):
        """Highlights the winning cells."""
        for row, col in winner_line:
            x1, y1 = col * 100, row * 100
            x2, y2 = (col + 1) * 100, (row + 1) * 100
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill="yellow", tags="winner_cell"
            )
            # Redraw "X" or "O" on top of the cell
            if self.gui.game.board[row][col] == "X":
                self.draw_x(x1 + 10, y1 + 10, x2 - 10, y2 - 10)
            elif self.gui.game.board[row][col] == "O":
                self.draw_o(x1 + 10, y1 + 10, x2 - 10, y2 - 10)

    def remove_winner_highlight(self):
        self.canvas.delete("winner_cell")
