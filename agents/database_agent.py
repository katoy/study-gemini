from agents.base_agent import BaseAgent
import json
import random
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)

class DatabaseAgent(BaseAgent):
    """
    完全解析済みデータベースを利用したエージェント
    """

    def __init__(self, player: str, database_file: str = "tictactoe_database.json"):
        super().__init__(player)
        self.database = self.load_database(database_file)

    def load_database(self, database_file: str) -> dict:
        """
        データベースを読み込む
        """
        try:
            with open(database_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Database file '{database_file}' not found.")
            return {}

    def get_move(self, board: list) -> tuple[int, int] | None:
        """
        データベースからベストの打ち手を取得する
        """
        board_str = self.board_to_string(board)
        # logging.info(f"get_move: Original board: {board_str}")  # この行を削除
        if board_str in self.database:
            best_move_index = self.database[board_str]["best_move"]
            # logging.info(f"get_move: best_move_index: {best_move_index}")  # この行を削除
            if best_move_index == -1:
                # logging.info("get_move: best_move_index is -1, returning None")  # この行を削除
                return None

            return self.index_to_move(best_move_index)
        else:
            logging.warning("get_move: Board state not found in database. Making a random move.")
            return self.get_random_move(board)

    def board_to_string(self, board: list) -> str:
        """
        盤面を文字列に変換する
        """
        return "".join(cell if cell != " " else " " for row in board for cell in row)

    def index_to_move(self, index: int) -> tuple[int, int]:
        """
        インデックスを (row, col) の形式に変換する
        """
        return index // 3, index % 3

    def get_random_move(self, board: list) -> tuple[int, int] | None:
        """
        ランダムな手を返す（データベースにない場合）
        """
        available_moves = []
        for row in range(3):
            for col in range(3):
                if board[row][col] == " ":
                    available_moves.append((row, col))
        if available_moves:
            return random.choice(available_moves)
        return None
