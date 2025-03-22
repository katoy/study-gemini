"""
game_logic.py: Implements the core logic of the Tic Tac Toe game.
"""

from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent

class TicTacToe:
    def __init__(self, player_first: bool, agent_type: str):
        """
        Initialize a new Tic Tac Toe game.

        Args:
            player_first (bool): True if the human plays first (as "X"), False otherwise.
            agent_type (str): Agent type ("ランダム" or "Minimax").
        """
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        # In Tic Tac Toe, "X" always goes first.
        self.current_player = "X"
        if player_first:
            self.human_player = "X"
            self.agent_player = "O"
        else:
            self.human_player = "O"
            self.agent_player = "X"
        self.agent = self._create_agent(agent_type)
        self.winner_line = None
        self.game_over = False

    def _create_agent(self, agent_type: str):
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
            row (int): Row index (0-2)
            col (int): Column index (0-2)

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
            str: "X" or "O" if a player wins, "draw" if board is full, or None if the game continues.
        """
        # Check rows and columns
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                self.winner_line = ((i, 0), (i, 1), (i, 2)) # 3つのマス全てを格納
                self.game_over = True
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                self.winner_line = ((0, i), (1, i), (2, i)) # 3つのマス全てを格納
                self.game_over = True
                return self.board[0][i]
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            self.winner_line = ((0, 0), (1, 1), (2, 2)) # 3つのマス全てを格納
            self.game_over = True
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            self.winner_line = ((0, 2), (1, 1), (2, 0)) # 3つのマス全てを格納
            self.game_over = True
            return self.board[0][2]
        # Check for draw
        if self._is_board_full():
            self.game_over = True
            return "draw"
        return None

    def _is_board_full(self) -> bool:
        return all(cell != " " for row in self.board for cell in row)

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def agent_move(self) -> bool:
        move = self.agent.get_move(self.board)
        if move is not None:
            row, col = move
            return self.make_move(row, col)
        return False
