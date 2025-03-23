import unittest
from unittest.mock import MagicMock
from game_logic import TicTacToe


class TestTicTacToe(unittest.TestCase):
    def test_make_move(self):
        game = TicTacToe(True, "ランダム")
        self.assertTrue(game.make_move(0, 0))
        self.assertEqual(game.board[0][0], "X")
        self.assertFalse(game.make_move(0, 0))  # Already occupied
        game.switch_player()
        self.assertTrue(game.make_move(1, 1))
        self.assertEqual(game.board[1][1], "O")

    def test_check_winner_row(self):
        game = TicTacToe(True, "ランダム")
        game.board = [
            ["X", "X", "X"],
            [" ", " ", " "],
            [" ", " ", " "],
        ]
        self.assertEqual(game.check_winner(), "X")

    def test_check_winner_column(self):
        game = TicTacToe(True, "ランダム")
        game.board = [
            ["O", " ", " "],
            ["O", " ", " "],
            ["O", " ", " "],
        ]
        self.assertEqual(game.check_winner(), "O")

    def test_check_winner_diagonal(self):
        game = TicTacToe(True, "ランダム")
        game.board = [
            ["X", " ", " "],
            [" ", "X", " "],
            [" ", " ", "X"],
        ]
        self.assertEqual(game.check_winner(), "X")

    def test_check_winner_anti_diagonal(self):
        game = TicTacToe(True, "ランダム")
        game.board = [
            [" ", " ", "O"],
            [" ", "O", " "],
            ["O", " ", " "],
        ]
        self.assertEqual(game.check_winner(), "O")

    def test_check_winner_draw(self):
        game = TicTacToe(True, "ランダム")
        game.board = [
            ["X", "O", "X"],
            ["X", "O", "O"],
            ["O", "X", "X"],
        ]
        self.assertEqual(game.check_winner(), "draw")

    def test_check_winner_none(self):
        game = TicTacToe(True, "ランダム")
        game.board = [
            ["X", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "],
        ]
        self.assertIsNone(game.check_winner())

    def test_switch_player(self):
        game = TicTacToe(True, "ランダム")
        self.assertEqual(game.current_player, "X")
        game.switch_player()
        self.assertEqual(game.current_player, "O")
        game.switch_player()
        self.assertEqual(game.current_player, "X")

    def test_agent_move(self):
        game = TicTacToe(True, "ランダム")
        self.assertTrue(game.agent_move())
        game2 = TicTacToe(True, "Minimax")
        self.assertTrue(game2.agent_move())
