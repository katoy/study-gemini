import unittest
import sqlite3
import os
from agents.database_agent import DatabaseAgent


class TestDatabaseAgent(unittest.TestCase):
    def setUp(self):
        # 一時テスト用 SQLite データベースを作成
        self.test_db = "test_tictactoe.db"
        self.conn = sqlite3.connect(self.test_db)
        self.cursor = self.conn.cursor()

        # テーブル作成
        self.cursor.execute(
            """
            CREATE TABLE tictactoe (
                board TEXT PRIMARY KEY,
                best_move INTEGER,
                result TEXT
            )
        """
        )

        # テスト用データを挿入
        self.test_data = {
            "         ": (4, "continue"),
            "X        ": (8, "continue"),
            "XXX      ": (-1, "X"),
            "OOO      ": (-1, "O"),
            "XOXOXOXOX": (-1, "draw"),
        }

        for board, (best_move, result) in self.test_data.items():
            self.cursor.execute(
                """
                INSERT INTO tictactoe (board, best_move, result)
                VALUES (?, ?, ?)
            """,
                (board, best_move, result),
            )

        self.conn.commit()
        self.agent = DatabaseAgent("X", self.test_db)

    def tearDown(self):
        self.conn.close()
        os.remove(self.test_db)

    def test_get_move_from_database(self):
        """データベースに存在する盤面から正しい手を取得できるか"""
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (1, 1))  # index 4 → (1, 1)

        board = [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (2, 2))  # index 8 → (2, 2)

    def test_get_move_best_move_minus_one(self):
        """best_move = -1 の場合、None を返すか"""
        board = [["X", "X", "X"], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertIsNone(move)

    def test_get_move_not_in_database(self):
        """データベースに存在しない盤面ではランダムな手を返すか"""
        board = [["O", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertIn(
            move,
            [(i, j) for i in range(3) for j in range(3) if not (i == 0 and j == 0)],
        )

    def test_board_to_string(self):
        """盤面が正しく文字列に変換されるか"""
        board = [["X", "O", " "], [" ", "X", " "], [" ", " ", "O"]]
        self.assertEqual(self.agent.board_to_string(board), "XO  X   O")

    def test_index_to_move(self):
        """index が (row, col) に正しく変換されるか"""
        self.assertEqual(self.agent.index_to_move(0), (0, 0))
        self.assertEqual(self.agent.index_to_move(4), (1, 1))
        self.assertEqual(self.agent.index_to_move(8), (2, 2))

    def test_get_random_move(self):
        """空きがあればランダムな手を返す / 埋まっていれば None を返す"""
        empty_board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_random_move(empty_board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3)])

        full_board = [["X", "O", "X"], ["X", "O", "X"], ["O", "X", "O"]]
        move = self.agent.get_random_move(full_board)
        self.assertIsNone(move)


if __name__ == "__main__":
    unittest.main()
