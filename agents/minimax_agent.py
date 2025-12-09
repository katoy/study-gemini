"""
minimax_agent.py: Implements the Minimax agent.
"""

from typing import List, Tuple, Optional
from agents.base_agent import BaseAgent


class MinimaxAgent(BaseAgent):
    """
    Agent that uses the Minimax algorithm to determine the best move.
    """

    def __init__(self, player: str):
        """
        Initializes the MinimaxAgent.

        Args:
            player (str): The player this agent represents ("X" or "O").
        """
        super().__init__(player)

    def get_move(self, board: List[List[str]]) -> Optional[Tuple[int, int]]:
        """
        Gets the agent's move using the Minimax algorithm.

        Args:
            board (List[List[str]]): The current game board.

        Returns:
            Optional[Tuple[int, int]]: The (row, col) of the move.
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

    def minimax(self, board: List[List[str]], depth: int, is_maximizing: bool) -> int:
        """
        The Minimax algorithm.

        Args:
            board (List[List[str]]): The current game board.
            depth (int): The current depth of the search.
            is_maximizing (bool): True if it's the maximizing player's turn.

        Returns:
            int: The score of the board state.
        """
        winner = self.check_winner(board)
        if winner == self.player:
            return 100 - depth
        if winner == self.get_opponent(self.player):
            return -100 + depth
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
            return int(best_score)
        else:
            best_score = float("inf")
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = self.get_opponent(self.player)
                        score = self.minimax(board, depth + 1, True)
                        board[row][col] = " "
                        best_score = min(score, best_score)
            return int(best_score)
