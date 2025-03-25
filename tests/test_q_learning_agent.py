import unittest
import os
import json
from unittest.mock import patch, MagicMock
from agents.q_learning_agent import QLearningAgent
from game_logic import TicTacToe

class TestQLearningAgent(unittest.TestCase):
    def setUp(self):
        self.q_table_file = "test_q_table.json"
        self.agent = QLearningAgent("O", q_table_file=self.q_table_file)
        self.empty_board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        self.full_board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]

    def tearDown(self):
        if os.path.exists(self.q_table_file):
            os.remove(self.q_table_file)

    def test_get_move_on_empty_board(self):
        """空の盤面で、返される手が有効な範囲内にあるかを確認する"""
        move = self.agent.get_move(self.empty_board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3)])

    def test_get_move_no_available_moves(self):
        """盤面が埋まっている場合、Noneが返るかを確認する"""
        move = self.agent.get_move(self.full_board)
        self.assertIsNone(move)

    def test_update_q_table(self):
        """Qテーブルが正しく更新されるかを確認する"""
        initial_q_value = self.agent.q_table.get("         ", [0] * 9)[0]
        self.agent.update_q_table("         ", 0, 100, "X        ")
        updated_q_value = self.agent.q_table["         "][0]
        self.assertNotEqual(initial_q_value, updated_q_value)

    def test_save_and_load_q_table(self):
        """Qテーブルが正しく保存・読み込みされるかを確認する"""
        self.agent.update_q_table("         ", 0, 100, "X        ")
        self.agent.save_q_table()
        self.assertTrue(os.path.exists(self.q_table_file))

        new_agent = QLearningAgent("O", q_table_file=self.q_table_file)
        self.assertEqual(self.agent.q_table, new_agent.q_table)

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
        move = self.agent.get_random_move(self.empty_board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3)])

        move = self.agent.get_random_move(self.full_board)
        self.assertIsNone(move)

    def test_get_available_moves(self):
        """空きマスが正しく取得できるか"""
        available_moves = self.agent.get_available_moves(self.empty_board)
        self.assertEqual(len(available_moves), 9)
        self.assertIn((0,0), available_moves)

        available_moves = self.agent.get_available_moves(self.full_board)
        self.assertEqual(len(available_moves), 0)

    @patch('random.uniform')
    def test_get_move_exploration(self, mock_random_uniform):
        """探索が正しく行われるか"""
        mock_random_uniform.return_value = 0.1  # 探索率より小さい値を返す
        self.agent.exploration_rate = 0.2
        move = self.agent.get_move(self.empty_board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3)])

    @patch('random.uniform')
    @patch('numpy.argmax')
    def test_get_move_exploitation(self, mock_argmax, mock_random_uniform):
        """利用が正しく行われるか"""
        mock_random_uniform.return_value = 0.3  # 探索率より大きい値を返す
        mock_argmax.return_value = 4
        self.agent.exploration_rate = 0.2
        move = self.agent.get_move(self.empty_board)
        self.assertEqual(move, (1, 1))

if __name__ == "__main__":
    unittest.main()
