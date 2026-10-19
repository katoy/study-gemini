"""
base_agent.py: Defines the base class for agents.
"""

from typing import Optional, List, Tuple


class BaseAgent:
    """
    Base class for all agents.
    Provides common utility methods for Tic Tac Toe games.
    """

    def __init__(self, player: str):
        """
        Initializes the BaseAgent.

        Args:
            player (str): The player this agent represents ("X" or "O").
        """
        self.player = player

    def get_move(self, board: List[List[str]]) -> Optional[Tuple[int, int]]:
        """
        Gets the agent's move.

        Args:
            board (List[List[str]]): The current game board.

        Returns:
            Optional[Tuple[int, int]]: The (row, col) of the move, or None.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def check_winner(self, board: List[List[str]]) -> Optional[str]:
        """
        Checks if a player has won.

        Args:
            board (List[List[str]]): The current game board.

        Returns:
            Optional[str]: "X" or "O" if a player wins, otherwise None.
        """
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] != " ":
                return row[0]

        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != " ":
                return board[0][col]

        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != " ":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != " ":
            return board[0][2]

        return None

    def is_board_full(self, board: List[List[str]]) -> bool:
        """
        Checks if the board is full.

        Args:
            board (List[List[str]]): The current game board.

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
            str: The opponent ("O" or "X").
        """
        return "O" if player == "X" else "X"
