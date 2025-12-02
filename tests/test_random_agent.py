import unittest
from agents.random_agent import RandomAgent


class TestRandomAgent(unittest.TestCase):
    def setUp(self):
        # エージェントを "O" として初期化（任意の設定でOK）
        self.agent = RandomAgent("O")

    def test_get_move_on_empty_board(self):
        """空の盤面で、返される手が有効な範囲内にあるかを確認する"""
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3)])

    def test_get_move_no_available_moves(self):
        """盤面が埋まっている場合、Noneが返るかを確認する"""
        board = [["X", "O", "X"], ["X", "O", "X"], ["O", "X", "O"]]
        move = self.agent.get_move(board)
        self.assertIsNone(move)


if __name__ == "__main__":
    unittest.main()
