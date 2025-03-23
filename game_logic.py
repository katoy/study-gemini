# game_logic.py
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent


class TicTacToe:
    """
    Represents the Tic Tac Toe game logic.
    """

    def __init__(self, player_select: bool, agent_type: str):
        """
        Initializes a new Tic Tac Toe game.

        Args:
            player_select (bool): True if the human plays first (as "X"),
                False otherwise.
            agent_type (str): Agent type ("ランダム" or "Minimax").
        """
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        # In Tic Tac Toe, "X" always goes first.
        if player_select:
            self.human_player = "X"
            self.agent_player = "O"
            self.current_player = "X"
        else:
            self.human_player = "O"
            self.agent_player = "X"
            self.current_player = "X"
        self.agent = self._create_agent(agent_type)
        self.winner_line = None
        self.game_over = False

    def _create_agent(self, agent_type: str):
        """
        Creates an agent based on the specified type.

        Args:
            agent_type (str): The type of agent to create.

        Returns:
            Agent: An instance of the specified agent type.

        Raises:
            ValueError: If an invalid agent type is provided.
        """
        if agent_type == "ランダム":
            return RandomAgent(self.agent_player)
        elif agent_type == "Minimax":
            return MinimaxAgent(self.agent_player)
        else:
            raise ValueError("Invalid agent type provided")

    def make_move(self, row: int, col: int) -> bool:
        """
        Attempt to make a move at the given position.

        Args:
            row (int): Row index (0-2).
            col (int): Column index (0-2).

        Returns:
            bool: True if the move was made, False otherwise.
        """
        if self.game_over:
            return False
        if self.board[row][col] == " ":
            self.board[row][col] = self.current_player
            return True
        return False

    def check_winner(self):
        """
        Check if a player has won or if the game is a draw.

        Returns:
            str: "X" or "O" if a player wins, "draw" if board is full,
                or None if the game continues.
        """
        # Check rows and columns
        for i in range(3):
            if (
                self.board[i][0]
                == self.board[i][1]
                == self.board[i][2]
                != " "
            ):
                self.winner_line = ((i, 0), (i, 1), (i, 2))  # All 3 cells
                self.game_over = True
                return self.board[i][0]
            if (
                self.board[0][i]
                == self.board[1][i]
                == self.board[2][i]
                != " "
            ):
                self.winner_line = ((0, i), (1, i), (2, i))  # All 3 cells
                self.game_over = True
                return self.board[0][i]
        # Check diagonals
        if (
            self.board[0][0]
            == self.board[1][1]
            == self.board[2][2]
            != " "
        ):
            self.winner_line = ((0, 0), (1, 1), (2, 2))  # All 3 cells
            self.game_over = True
            return self.board[0][0]
        if (
            self.board[0][2]
            == self.board[1][1]
            == self.board[2][0]
            != " "
        ):
            self.winner_line = ((0, 2), (1, 1), (2, 0))  # All 3 cells
            self.game_over = True
            return self.board[0][2]
        # Check for draw
        if self._is_board_full():
            self.game_over = True
            return "draw"
        return None

    def _is_board_full(self) -> bool:
        """
        Checks if the board is full.

        Returns:
            bool: True if the board is full, False otherwise.
        """
        return all(cell != " " for row in self.board for cell in row)

    def switch_player(self):
        """Switches the current player."""
        self.current_player = "O" if self.current_player == "X" else "X"

    def agent_move(self) -> bool:
        """
        Makes a move for the agent.

        Returns:
            bool: True if the agent made a move, False otherwise.
        """
        move = self.agent.get_move(self.board)
        if move is not None:
            row, col = move
            return self.make_move(row, col)
        return False
