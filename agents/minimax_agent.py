"""
minimax_agent.py: Implements the Minimax agent.
"""

from agents.base_agent import BaseAgent


class MinimaxAgent(BaseAgent):
    """
    Agent that uses the Minimax algorithm to make moves.
    """

    def __init__(self, player: str):
        """
        Initializes the MinimaxAgent.

        Args:
            player (str): The player this agent represents ("X" or "O").
        """
        super().__init__(player)

    def get_move(self, board: list) -> tuple[int, int] | None:
        """
        Gets the agent's move using the Minimax algorithm.

        Args:
            board (list): The current game board.

        Returns:
            tuple[int, int] | None: The (row, col) of the move.
        """
        best_score = float("-inf")
        best_move = None
        for row in range(3):
            for col in range(3):
                if board[row][col] == " ":
                    board[row][col] = self.player
                    score = self.minimax(board, 0, False)
                    board[row][col] = " "
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)
        return best_move

    def minimax(self, board: list, depth: int, is_maximizing: bool) -> int:
        """
        Minimax algorithm.

        Args:
            board (list): The current game board.
            depth (int): The current depth of the search.
            is_maximizing (bool): True if maximizing player's turn.

        Returns:
            int: The score of the current board state.
        """
        winner = self.check_winner(board)
        if winner == self.player:
            return 100 - depth  # Favor quicker wins
        if winner == self.get_opponent(self.player):
            return -100 + depth  # Penalize slower losses
        if self.is_board_full(board):
            return 0

        if is_maximizing:
            best_score = float("-inf")
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = self.player
                        score = self.minimax(board, depth + 1, False)
                        board[row][col] = " "
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float("inf")
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = self.get_opponent(self.player)
                        score = self.minimax(board, depth + 1, True)
                        board[row][col] = " "
                        best_score = min(score, best_score)
            return best_score

    def check_winner(self, board: list) -> str | None:
        """
        Check if a player has won.

        Args:
            board (list): The current game board.

        Returns:
            str | None: "X" or "O" if a player wins, None otherwise.
        """
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != " ":
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != " ":
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != " ":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != " ":
            return board[0][2]
        return None

    def is_board_full(self, board: list) -> bool:
        """
        Checks if the board is full.

        Args:
            board (list): The current game board.

        Returns:
            bool: True if the board is full, False otherwise.
        """
        return all(cell != " " for row in board for cell in row)

    def get_opponent(self, player: str) -> str:
        """
        Gets the opponent of the given player.

        Args:
            player (str): The player ("X" or "O").

        Returns:
            str: The opponent ("X" or "O").
        """
        return "O" if player == "X" else "X"
