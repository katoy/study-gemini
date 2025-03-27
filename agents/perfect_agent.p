import unittest
from agents.perfect_agent import PerfectAgent


class TestPerfectAgent(unittest.TestCase):
    def setUp(self):
        self.agent = PerfectAgent("X")

    def test_get_move_center_empty(self):
        """盤面が空の時、中央が選択されるか"""
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (1, 1))

    def test_get_move_specific_pattern1(self):
        """特定盤面パターンで期待する手が選ばれるか"""
        board = [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (2, 2))

    def test_get_move_specific_pattern2(self):
        """特定盤面パターンで期待する手が選ばれるか"""
        board = [[" ", " ", "X"], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (0, 0))

    def test_get_move_specific_pattern3(self):
        """特定盤面パターンで期待する手が選ばれるか"""
        board = [["X", " ", " "], [" ", " ", " "], [" ", " ", "X"]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (0, 1))

    def test_get_move_already_taken(self):
        """選択されようとする手が既に埋まっている場合はランダムに動くか"""
        board = [[" ", " ", "X"], [" ", " ", " "], [" ", " ", " "]]
        # すでに埋まっている手をperfect_moveにセット
        self.agent.perfect_moves["  X      "] = 2
        move = self.agent.get_move(board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3) if not (i == 0 and j == 2)])

    def test_get_move_not_in_perfect_moves(self):
        """辞書にないパターンの場合、ランダムに返すか"""
        board = [["X", "O", " "], [" ", " ", " "], [" ", " ", " "]]
        self.agent.perfect_moves = {} # 辞書を初期化
        move = self.agent.get_move(board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "])

    def test_board_to_string(self):
        """board_to_string() が正しく動作するか"""
        board = [["X", "O", " "], [" ", "X", " "], [" ", " ", "O"]]
        self.assertEqual(self.agent.board_to_string(board), "XO  X   O")

    def test_index_to_move(self):
        """index_to_move() が正しく動作するか"""
        self.assertEqual(self.agent.index_to_move(0), (0, 0))
        self.assertEqual(self.agent.index_to_move(4), (1, 1))
        self.assertEqual(self.agent.index_to_move(8), (2, 2))

    def test_get_random_move(self):
        """get_random_move() が正しく動作するか"""
        empty_board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_random_move(empty_board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3)])

        full_board = [["X", "O", "X"], ["X", "O", "X"], ["O", "X", "O"]]
        move = self.agent.get_random_move(full_board)
        self.assertIsNone(move)

if __name__ == "__main__":
    unittest.main()
