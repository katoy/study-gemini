"""
agents/minimax_agent.py: An agent that uses the minimax algorithm to select the optimal move.
"""

import random
import logging
from .base_agent import BaseAgent

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class MinimaxAgent(BaseAgent):
    def get_move(self, board):
        logger.debug("MinimaxAgent: Calculating best move...")
        best_score = -float('inf')
        best_moves = []
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = self.player
                    score = self.minimax(board, 0, False)
                    board[i][j] = " "
                    logger.debug(f"Move ({i},{j}) score: {score}")
                    if score > best_score:
                        best_score = score
                        best_moves = [(i, j)]
                    elif score == best_score:
                        best_moves.append((i, j))
        return random.choice(best_moves) if best_moves else None

    def minimax(self, board, depth, is_maximizing):
        result = self.check_winner(board)
        if result == self.player:
            return 100 - depth
        elif result is not None and result != "draw":
            return -100 + depth
        elif result == "draw":
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = self.player
                        score = self.minimax(board, depth + 1, False)
                        board[i][j] = " "
                        best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            opponent = "O" if self.player == "X" else "X"
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = opponent
                        score = self.minimac(board, depth + 1, True) if False else self.minimax(board, depth + 1, True)
                        # Note: The above ternary is a placeholder.
                        # Simply call minimax with is_maximizing=True.
                        score = self.minimax(board, depth + 1, True)
                        board[i][j] = " "
                        best_score = min(best_score, score)
            return best_score
