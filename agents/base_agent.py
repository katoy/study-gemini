"""
agents/base_agent.py: Abstract base class for all agents.
"""

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, player: str):
        self.player = player

    @abstractmethod
    def get_move(self, board):
        """
        Determine a move given the current board.

        Args:
            board: Current board state.

        Returns:
            Tuple (row, col) representing the move, or None if no move is possible.
        """
        pass

    def check_winner(self, board):
        # Simple winner check (can be overridden if needed)
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != " ":
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != " ":
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != " ":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != " ":
            return board[0][2]
        if all(cell != " " for row in board for cell in row):
            return "draw"
        return None
