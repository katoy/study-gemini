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

    def test_get_move_specific_pattern4(self):
        """特定盤面パターンで期待する手が選ばれるか"""
        board = [["X", " ", "X"], [" ", " ", " "], [" ", " ", "O"]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (1, 0))

    def test_get_move_not_in_perfect_moves(self):
        """辞書にないパターンの場合、ValueErrorを返すか"""
        board = [["X", "O", " "], [" ", " ", " "], [" ", " ", " "]]
        with self.assertRaises(ValueError):
            self.agent.get_move(board)

    def test_board_to_string(self):
        """board_to_string() が正しく動作するか"""
        board = [["X", "O", " "], [" ", "X", " "], [" ", " ", "O"]]
        self.assertEqual(self.agent.board_to_string(board), "XO  X   O")

    def test_index_to_move(self):
        """index_to_move() が正しく動作するか"""
        self.assertEqual(self.agent.index_to_move(0), (0, 0))
        self.assertEqual(self.agent.index_to_move(4), (1, 1))
        self.assertEqual(self.agent.index_to_move(8), (2, 2))

if __name__ == "__main__":
    unittest.main()
