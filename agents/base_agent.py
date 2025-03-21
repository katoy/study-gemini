# --- agents/base_agent.py ---
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, player):
        self.player = player

    @abstractmethod
    def get_move(self, board):
        """
        Gets the agent's move.

        Args:
            board: The current state of the board.

        Returns:
            A tuple (row, col) representing the move.
        """
        pass

    def check_winner(self, board):
        """
        Checks if there is a winner or a draw.

        Args:
            board: The current state of the board.

        Returns:
            The winner ('X' or 'O') or 'draw' or None if the game is not over.
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
        if self.is_board_full(board):
            return "draw"
        return None

    def is_board_full(self, board):
        """
        Checks if the board is full.

        Args:
            board: The current state of the board.

        Returns:
            True if the board is full, False otherwise.
        """
        for row in board:
            for cell in row:
                if cell == " ":
                    return False
        return True
