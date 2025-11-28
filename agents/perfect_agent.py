"""
perfect_agent.py: Implements the Perfect agent.
"""

import json
import os
from agents.base_agent import BaseAgent


class PerfectAgent(BaseAgent):
    """
    Agent that plays perfectly in Tic Tac Toe.
    """

    def __init__(self, player: str, perfect_moves_file: str = "perfect_moves.json"):
        """
        Initializes the PerfectAgent.

        Args:
            player (str): The player this agent represents ("X" or "O").
            perfect_moves_file (str): The path to the JSON file containing the perfect moves.
        """
        super().__init__(player)
        self.perfect_moves_file = perfect_moves_file
        self.perfect_moves = self.load_perfect_moves()

    def load_perfect_moves(self) -> dict:
        """Loads the perfect moves from the JSON file."""
        if not os.path.exists(self.perfect_moves_file):
            raise FileNotFoundError(f"Perfect moves file not found: {self.perfect_moves_file}")
        with open(self.perfect_moves_file, "r", encoding="latin-1") as f:
            return json.loads(f.read())

    def get_move(self, board: list) -> tuple[int, int]:
        """
        Gets the perfect move for the current board state.

        Args:
            board (list): The current game board.

        Returns:
            tuple[int, int]: The (row, col) of the move.

        Raises:
            KeyError: If no perfect move is found for the given board.
        """
        board_str = self.board_to_string(board)
        if board_str in self.perfect_moves:
            best_move_index = self.perfect_moves[board_str]
            if best_move_index == -1:
                raise KeyError(f"The game is over for the board: {board_str}")
            return self.index_to_move(best_move_index)
        else:
            raise KeyError(f"No perfect move found in perfect_moves for board: {board_str}. This pattern is not registered in the dictionary.")

    def board_to_string(self, board: list) -> str:
        return "".join(cell if cell != " " else " " for row in board for cell in row)

    def index_to_move(self, index: int) -> tuple[int, int]:
        return index // 3, index % 3
