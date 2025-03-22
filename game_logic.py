from agents.base_agent import BaseAgent
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent

class TicTacToe:
    def __init__(self, player_first, agent_type):
        """
        三目並べゲームの初期化

        Args:
            player_first (bool): 人間が先手かどうか (True: 先手, False: 後手)
            agent_type (str): エージェントの種類 ("ランダム" または "Minimax")
        """
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        # 三目並べでは "X" が必ず先手となるため、current_player を "X" に固定する
        self.current_player = "X"
        if player_first:
            self.human_player = "X"
            self.agent_player = "O"
        else:
            self.human_player = "O"
            self.agent_player = "X"
        self.agent = self.create_agent(agent_type)
        self.winner_line = None
        self.game_over = False  # ゲーム終了フラグの初期化

    def create_agent(self, agent_type):
        if agent_type == "ランダム":
            return RandomAgent(self.agent_player)
        elif agent_type == "Minimax":
            return MinimaxAgent(self.agent_player)
        else:
            raise ValueError("Invalid agent type")

    def make_move(self, row, col):
        """
        指定されたマスに手を打つ

        Args:
            row (int): 行 (0-2)
            col (int): 列 (0-2)

        Returns:
            bool: 手を打てたかどうか (True: 打てた, False: 打てなかった)
        """
        # ゲーム終了している場合は手を打たない
        if self.game_over:
            return False

        if self.board[row][col] == " ":
            self.board[row][col] = self.current_player
            return True
        return False

    def check_winner(self):
        """
        勝敗を判定する

        Returns:
            str or None: 勝者 ("X" または "O")、引き分け ("draw")、またはゲームが継続中 (None)
        """
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                self.winner_line = ((i, 0), (i, 2))
                self.game_over = True
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                self.winner_line = ((0, i), (2, i))
                self.game_over = True
                return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            self.winner_line = ((0, 0), (2, 2))
            self.game_over = True
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            self.winner_line = ((0, 2), (2, 0))
            self.game_over = True
            return self.board[0][2]
        if self.is_board_full():
            self.game_over = True
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
        if move is not None:
            row, col = move
            self.make_move(row, col)
            return True
        return False
