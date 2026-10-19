"""
random_agent.py: Implements the Random agent.
"""

import random
from typing import List, Tuple, Optional

from agents.base_agent import BaseAgent


class RandomAgent(BaseAgent):
    """
    Agent that makes random moves.
    """

    def __init__(self, player: str):
        """
        Initializes the RandomAgent.

        Args:
            player (str): The player this agent represents ("X" or "O").
        """
        super().__init__(player)

    def get_move(self, board: List[List[str]]) -> Optional[Tuple[int, int]]:
        """
        Gets a random move.

        Args:
            board (List[List[str]]): The current game board.

        Returns:
            Optional[Tuple[int, int]]: The (row, col) of the move, or None.
        """
        available_moves = []
        for row in range(3):
            for col in range(3):
                if board[row][col] == " ":
                    available_moves.append((row, col))
        if available_moves:
            return random.choice(available_moves)
        return None
