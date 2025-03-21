# --- agents/random_agent.py ---
import random
from .base_agent import BaseAgent

class RandomAgent(BaseAgent):
    def get_move(self, board):
        available_moves = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]
        if available_moves:
            return random.choice(available_moves)
        return None
