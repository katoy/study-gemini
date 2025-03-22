"""
agents/random_agent.py: A simple agent that selects a random available move.
"""

import random
from .base_agent import BaseAgent

class RandomAgent(BaseAgent):
    def get_move(self, board):
        available_moves = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]
        return random.choice(available_moves) if available_moves else None
