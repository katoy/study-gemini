class BaseAgent:
    def __init__(self, symbol):
        self.symbol = symbol

    def choose_move(self, game):
        """
        Subclasses should implement this method to choose a move.
        Args:
            game: The current TicTacToe game instance.
        Returns:
            tuple: (row, col) of the chosen move.
        """
        raise NotImplementedError

