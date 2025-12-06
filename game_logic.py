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
        self.winner = None
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

    @staticmethod
    def _check_winner_logic(board):
        """
        Check if a player has won or if the game is a draw, without side effects.

        Args:
            board (list[list[str]]): The game board.

        Returns:
            tuple(str or None, tuple or None): A tuple containing the winner ('X', 'O', 'draw')
                                                and the winning line coordinates, or (None, None).
        """
        # Check rows and columns
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != " ":
                return board[i][0], ((i, 0), (i, 1), (i, 2))
            if board[0][i] == board[1][i] == board[2][i] != " ":
                return board[0][i], ((0, i), (1, i), (2, i))
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != " ":
            return board[0][0], ((0, 0), (1, 1), (2, 2))
        if board[0][2] == board[1][1] == board[2][0] != " ":
            return board[0][2], ((0, 2), (1, 1), (2, 0))

        # Check for draw
        if all(cell != " " for row in board for cell in row):
            return "draw", None

        return None, None

    def check_winner(self):
        """
        Check if a player has won or if the game is a draw and updates instance state.

        Returns:
            str: "X" or "O" if a player wins, "draw" if board is full,
                or None if the game continues.
        """
        if self.winner: # Already decided
            return self.winner

        winner, winner_line = self._check_winner_logic(self.board)
        if winner:
            self.winner = winner
            self.winner_line = winner_line
            self.game_over = True
        return self.winner

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