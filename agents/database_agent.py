import sqlite3
import random
import logging

from agents.base_agent import BaseAgent

# ロギング設定
logging.basicConfig(level=logging.INFO)


class DatabaseAgent(BaseAgent):
    """
    SQLite3 データベースを利用するエージェント
    """

    def __init__(self, player: str, database_file: str = "tictactoe.db"):
        super().__init__(player)
        self.conn = sqlite3.connect(database_file)
        self.cursor = self.conn.cursor()

    def get_move(self, board: list) -> tuple[int, int] | None:
        """
        盤面に応じたベストムーブを取得。なければランダム。
        """
        board_str = self.board_to_string(board)
        self.cursor.execute(
            "SELECT best_move, result FROM tictactoe WHERE board = ?", (board_str,)
        )
        row = self.cursor.fetchone()

        if row:
            best_move, result = row
            if best_move == -1:
                return None
            return self.index_to_move(best_move)
        else:
            logging.warning("🔍 データベースに盤面が見つかりません。ランダムな手を選びます。")
            return self.get_random_move(board)

    def board_to_string(self, board: list) -> str:
        return "".join(cell if cell != " " else " " for row in board for cell in row)

    def index_to_move(self, index: int) -> tuple[int, int]:
        return index // 3, index % 3

    def get_random_move(self, board: list) -> tuple[int, int] | None:
        available_moves = [
            (row, col)
            for row in range(3)
            for col in range(3)
            if board[row][col] == " "
        ]
        return random.choice(available_moves) if available_moves else None

    def __del__(self):
        self.conn.close()
