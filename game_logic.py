# --- game_logic.py ---
from agents.base_agent import BaseAgent
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent

class TicTacToe:
    def __init__(self, player_first, agent_type):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X" if player_first else "O"
        self.human_player = "X" if player_first else "O"
        self.agent_player = "O" if player_first else "X"
        self.agent = self.create_agent(agent_type)
        self.winner_line = None

    def create_agent(self, agent_type):
        if agent_type == "ランダム":
            return RandomAgent(self.agent_player)
        elif agent_type == "Minimax":
            return MinimaxAgent(self.agent_player)
        else:
            raise ValueError("Invalid agent type")

    def make_move(self, row, col):
        if self.board[row][col] == " ":
            self.board[row][col] = self.current_player
            return True
        return False

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                self.winner_line = ((i, 0), (i, 2))
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                self.winner_line = ((0, i), (2, i))
                return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            self.winner_line = ((0, 0), (2, 2))
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            self.winner_line = ((0, 2), (2, 0))
            return self.board[0][2]
        if self.is_board_full():
            return "draw"
        return None

    def is_board_full(self):
        for row in self.board:
            for cell in row:
                if cell == " ":
                    return False
        return True

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def agent_move(self):
        move = self.agent.get_move(self.board)
        if move:
            row, col = move
            self.make_move(row, col)
            return True
        return False
