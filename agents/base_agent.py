"""
base_agent.py: Defines the base class for agents.
"""


class BaseAgent:
    """
    Base class for all agents.
    """

    def __init__(self, player: str):
        """
        Initializes the BaseAgent.

        Args:
            player (str): The player this agent represents ("X" or "O").
        """
        self.player = player

    def get_move(self, board: list) -> tuple[int, int]:
        """
        Gets the agent's move.

        Args:
            board (list): The current game board.

        Returns:
            tuple[int, int]: The (row, col) of the move.
        """
        raise NotImplementedError("Subclasses must implement this method")
