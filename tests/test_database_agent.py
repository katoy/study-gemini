import unittest
from unittest.mock import patch, mock_open
from agents.database_agent import DatabaseAgent
import json

class TestDatabaseAgent(unittest.TestCase):
    def setUp(self):
        # テスト用のダミーデータベース
        self.dummy_database = {
            "         ": {"best_move": 4, "result": "continue"},  # 空の盤面
            "X        ": {"best_move": 8, "result": "continue"},  # 左上にX
            "XXX      ": {"best_move": -1, "result": "X"},  # Xの勝ち
            "OOO      ": {"best_move": -1, "result": "O"},  # Oの勝ち
            "XOXOXOXOX": {"best_move": -1, "result": "draw"},  # 引き分け
        }
        self.dummy_database_str = json.dumps(self.dummy_database)

        # テスト用のDatabaseAgent
        with patch("builtins.open", mock_open(read_data=self.dummy_database_str)):
            self.agent = DatabaseAgent("X", "dummy_database.json")

    def test_load_database(self):
        """データベースが正しく読み込まれるか"""
        self.assertEqual(self.agent.database, self.dummy_database)

    def test_get_move_from_database(self):
        """データベースに存在する盤面に対して、正しい手を返すか"""
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (1, 1))  # 中央

        board = [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (2, 2))  # 右下

    def test_get_move_not_in_database(self):
        """データベースに存在しない盤面に対して、ランダムな手を返すか"""
        board = [["O", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        with patch.object(self.agent, "get_random_move") as mock_random_move:
            self.agent.get_move(board)
            mock_random_move.assert_called_once()

    def test_get_move_best_move_is_minus_one(self):
        """best_moveが-1の場合にNoneを返すか"""
        board = [["X", "X", "X"], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertIsNone(move)

    def test_board_to_string(self):
        """盤面が正しく文字列に変換されるか"""
        board = [["X", "O", " "], [" ", "X", " "], [" ", " ", "O"]]
        self.assertEqual(self.agent.board_to_string(board), "XO  X   O") # 修正

    def test_index_to_move(self):
        """インデックスが正しく(row, col)に変換されるか"""
        self.assertEqual(self.agent.index_to_move(0), (0, 0))
        self.assertEqual(self.agent.index_to_move(1), (0, 1))
        self.assertEqual(self.agent.index_to_move(2), (0, 2))
        self.assertEqual(self.agent.index_to_move(3), (1, 0))
        self.assertEqual(self.agent.index_to_move(4), (1, 1))
        self.assertEqual(self.agent.index_to_move(5), (1, 2))
        self.assertEqual(self.agent.index_to_move(6), (2, 0))
        self.assertEqual(self.agent.index_to_move(7), (2, 1))
        self.assertEqual(self.agent.index_to_move(8), (2, 2))

    def test_get_random_move(self):
        """ランダムな手が正しく返されるか"""
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_random_move(board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3)])

        board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]
        move = self.agent.get_random_move(board)
        self.assertIsNone(move)

if __name__ == "__main__":
    unittest.main()
