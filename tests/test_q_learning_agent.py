import unittest
import os
import json
from unittest.mock import patch
from agents.q_learning_agent import QLearningAgent
from game_logic import TicTacToe
import numpy as np


class TestQLearningAgent(unittest.TestCase):
    def setUp(self):
        self.q_table_file = "test_q_table.json"
        # q_table_file が存在する場合はリネームしてテストの clean state を確保
        if os.path.exists(self.q_table_file):
            os.rename(self.q_table_file, self.q_table_file + ".bak")

        self.agent = QLearningAgent(
            "O", q_table_file=self.q_table_file, exploration_rate=0.5
        )

        self.empty_board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        self.almost_full_board = [["X", "O", "X"], ["X", "O", " "], ["O", "X", "X"]]
        self.full_board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]

    def tearDown(self):
        if os.path.exists(self.q_table_file):
            os.remove(self.q_table_file)
        # バックアップファイルを元に戻す
        if os.path.exists(self.q_table_file + ".bak"):
            os.rename(self.q_table_file + ".bak", self.q_table_file)

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

        original_pytest_current_test = os.getenv("PYTEST_CURRENT_TEST")
        if original_pytest_current_test:
            del os.environ["PYTEST_CURRENT_TEST"]

        new_agent = QLearningAgent(
            "O", q_table_file=self.q_table_file, is_training=False
        )
        self.assertEqual(self.agent.q_table, new_agent.q_table)

        if original_pytest_current_test:
            os.environ["PYTEST_CURRENT_TEST"] = original_pytest_current_test

    @patch("random.uniform")
    def test_get_move_exploration(self, mock_random_uniform):
        """探索が正しく行われるか"""
        mock_random_uniform.return_value = 0.1  # 探索率より小さい値を返す
        self.agent.exploration_rate = 0.2
        move = self.agent.get_move(self.empty_board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3)])

    @patch("random.uniform")
    @patch("numpy.argmax")
    def test_get_move_exploitation(self, mock_argmax, mock_random_uniform):
        """利用が正しく行われるか(ほぼ埋まっている盤面)"""
        mock_random_uniform.return_value = 0.3  # 探索率より大きい値を返す(利用)
        mock_argmax.return_value = 5  # 5番目のマスが空いている
        self.agent.exploration_rate = 0.2  # 探索率
        move = self.agent.get_move(self.almost_full_board)
        self.assertEqual(move, (1, 2))

    def test_exploration_rate_decay(self):
        """探索率が正しく減衰するかを確認する"""
        initial_exploration_rate = self.agent.exploration_rate
        self.agent.decay_exploration_rate(1, 100)
        self.assertLess(self.agent.exploration_rate, initial_exploration_rate)
        for i in range(100000):
            self.agent.decay_exploration_rate(i, 100000)
        self.assertAlmostEqual(
            self.agent.exploration_rate, self.agent.min_exploration_rate, places=2
        )  # Changed to self.agent.min_exploration_rate

    def test_set_exploration_rate(self):
        """exploration_rate のセッターが正しく動作するか"""
        new_rate = 0.5
        self.agent.exploration_rate = new_rate
        self.assertEqual(self.agent.exploration_rate, new_rate)

    def test_set_min_exploration_rate(self):
        """min_exploration_rate のセッターが正しく動作するか"""
        new_rate = 0.02
        self.agent.min_exploration_rate = new_rate
        self.assertEqual(self.agent.min_exploration_rate, new_rate)

    @patch("builtins.print")
    def test_load_q_table_with_invalid_json(self, mock_print):
        """無効なQテーブルファイルでエラー処理が正しく行われるかを確認する"""
        # PYTEST_CURRENT_TEST 環境変数を一時的に削除
        original_pytest_current_test = os.getenv("PYTEST_CURRENT_TEST")
        if original_pytest_current_test:
            del os.environ["PYTEST_CURRENT_TEST"]

        # 無効なJSONファイルを作成
        with open(self.q_table_file, "w") as f:
            f.write("{invalid json}")

        # QLearningAgentを初期化（load_q_tableが呼ばれる）
        agent = QLearningAgent("X", q_table_file=self.q_table_file, is_training=False)

        # q_tableが空であることを確認
        self.assertEqual(agent.q_table, {})
        # エラーメッセージがプリントされたことを確認
        mock_print.assert_called_with(
            f"Warning: Could not read Q-table file '{self.q_table_file}'. Starting with an empty table."
        )

        # 環境変数を元に戻す
        if original_pytest_current_test:
            os.environ["PYTEST_CURRENT_TEST"] = original_pytest_current_test
