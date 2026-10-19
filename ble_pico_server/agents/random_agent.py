import random
from .base_agent import BaseAgent


class RandomAgent(BaseAgent):
    def __init__(self, symbol):
        super().__init__(symbol)

    def choose_move(self, game):
        """
        Chooses a random available move on the board.
        Args:
            game: The current TicTacToe game instance.
        Returns:
            tuple: (row, col) of the chosen move.
        """
        available_moves = []
        for r in range(3):
            for c in range(3):
                if game.board[r][c] == " ":
                    available_moves.append((r, c))
        if available_moves:
            return random.choice(available_moves)
        return None
