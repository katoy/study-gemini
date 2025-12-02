# game_logic.py


class TicTacToe:
    """
    Represents the Tic Tac Toe game logic.
    """

    def __init__(self, agent_x=None, agent_o=None, human_player="X"):
        """
        Initializes a new Tic Tac Toe game.
        Args:
            agent_x: The agent playing as 'X' (first player).
            agent_o: The agent playing as 'O' (second player).
            human_player: The symbol for the human player ('X' or 'O').
        """
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.agent_x = agent_x
        self.agent_o = agent_o
        self.human_player = human_player
        self.agent_player = "O" if human_player == "X" else "X"
        # "X" always goes first.
        self.current_player = "X"
        self.winner_line = None
        self.game_over = False

    def get_current_agent(self):
        if self.current_player == "X":
            return self.agent_x
        return self.agent_o

    def make_move(self, row: int, col: int) -> bool:
        """
        Attempt to make a move at the given position.

        Args:
            row (int): Row index (0-2).
            col (int): Column index (0-2).

        Returns:
            bool: True if the move was made, False otherwise.
        """
        if self.game_over:
            return False
        if self.board[row][col] == " ":
            self.board[row][col] = self.current_player
            return True
        return False

    def check_winner(self):
        """
        Check if a player has won or if the game is a draw.

        Returns:
            str: "X" or "O" if a player wins, "draw" if board is full,
                or None if the game continues.
        """
        # Check rows and columns
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                self.winner_line = ((i, 0), (i, 1), (i, 2))  # All 3 cells
                self.game_over = True
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                self.winner_line = ((0, i), (1, i), (2, i))  # All 3 cells
                self.game_over = True
                return self.board[0][i]
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            self.winner_line = ((0, 0), (1, 1), (2, 2))  # All 3 cells
            self.game_over = True
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            self.winner_line = ((0, 2), (1, 1), (2, 0))  # All 3 cells
            self.game_over = True
            return self.board[0][2]
        # Check for draw
        if self._is_board_full():
            self.game_over = True
            return "draw"
        return None

    def _is_board_full(self) -> bool:
        """
        Checks if the board is full.

        Returns:
            bool: True if the board is full, False otherwise.
        """
        return all(cell != " " for row in self.board for cell in row)

    def switch_player(self):
        """Switches the current player."""
        self.current_player = "O" if self.current_player == "X" else "X"
