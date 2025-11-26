import unittest

from game_logic import TicTacToe


class TestTicTacToe(unittest.TestCase):
    def setUp(self):
        self.game = TicTacToe(human_player="X")

    def test_initial_board_is_empty(self):
        """初期化時に盤面が全て空であることを確認する"""
        for row in self.game.board:
            for cell in row:
                self.assertEqual(cell, " ")

    def test_make_move(self):
        """有効な手が盤面に反映されるかを確認する"""
        self.assertTrue(self.game.make_move(0, 0))
        self.assertEqual(self.game.board[0][0], "X")

    def test_switch_player(self):
        """switch_playerでターンが正しく切り替わるかを確認する"""
        self.assertEqual(self.game.current_player, "X")
        self.game.switch_player()
        self.assertEqual(self.game.current_player, "O")

    def test_check_winner_horizontal(self):
        """横一列が揃った場合に勝者が正しく返り、winner_lineが正しく設定されるかを確認する"""
        self.game.board = [
            ["X", "X", "X"],
            [" ", " ", " "],
            [" ", " ", " "],
        ]
        self.assertEqual(self.game.check_winner(), "X")
        self.assertEqual(self.game.winner_line, ((0, 0), (0, 1), (0, 2)))

    def test_check_winner_vertical(self):
        """縦一列が揃った場合に勝者が正しく返り、winner_lineが正しく設定されるかを確認する"""
        self.game.board = [
            ["X", " ", " "],
            ["X", " ", " "],
            ["X", " ", " "],
        ]
        self.assertEqual(self.game.check_winner(), "X")
        self.assertEqual(self.game.winner_line, ((0, 0), (1, 0), (2, 0)))

    def test_check_winner_diagonal(self):
        """斜めが揃った場合に勝者が正しく返り、winner_lineが正しく設定されるかを確認する"""
        self.game.board = [
            ["X", " ", " "],
            [" ", "X", " "],
            [" ", " ", "X"],
        ]
        self.assertEqual(self.game.check_winner(), "X")
        self.assertEqual(self.game.winner_line, ((0, 0), (1, 1), (2, 2)))

    def test_check_winner_draw(self):
        """盤面が埋まっていて引き分けの場合、"draw" が返るかを確認する"""
        self.game.board = [
            ["X", "O", "X"],
            ["X", "O", "O"],
            ["O", "X", "X"],
        ]
        self.assertEqual(self.game.check_winner(), "draw")
