import unittest
from game_logic import TicTacToe

class TestTicTacToe(unittest.TestCase):
    def setUp(self):
        # ここでは人間が先手、エージェントはランダムエージェントを使用して初期化
        self.game = TicTacToe(player_first=True, agent_type="ランダム")

    def test_initial_board_is_empty(self):
        """初期化時に盤面が全て空であることを確認する"""
        expected_board = [[" ", " ", " "],
                          [" ", " ", " "],
                          [" ", " ", " "]]
        self.assertEqual(self.game.board, expected_board)

    def test_make_move(self):
        """有効な手が盤面に反映されるかを確認する"""
        self.assertTrue(self.game.make_move(0, 0))
        self.assertEqual(self.game.board[0][0], "X")
        # 同じ場所への手は打てない
        self.assertFalse(self.game.make_move(0, 0))

    def test_switch_player(self):
        """switch_playerでターンが正しく切り替わるかを確認する"""
        current = self.game.current_player
        self.game.switch_player()
        self.assertEqual(self.game.current_player, "O" if current == "X" else "X")

    def test_check_winner_horizontal(self):
        """横一列が揃った場合に勝者が正しく返るかを確認する"""
        self.game.board = [
            ["X", "X", "X"],
            ["O", " ", " "],
            ["O", " ", " "]
        ]
        self.assertEqual(self.game.check_winner(), "X")

    def test_check_winner_vertical(self):
        """縦一列が揃った場合に勝者が正しく返るかを確認する"""
        self.game.board = [
            ["O", "X", " "],
            ["O", "X", " "],
            [" ", "X", " "]
        ]
        self.assertEqual(self.game.check_winner(), "X")

    def test_check_winner_diagonal(self):
        """斜めが揃った場合に勝者が正しく返るかを確認する"""
        self.game.board = [
            ["O", "X", "X"],
            [" ", "O", " "],
            ["X", " ", "O"]
        ]
        self.assertEqual(self.game.check_winner(), "O")

    def test_check_winner_draw(self):
        """盤面が埋まっていて引き分けの場合、"draw" が返るかを確認する"""
        self.game.board = [
            ["X", "O", "X"],
            ["X", "O", "O"],
            ["O", "X", "X"]
        ]
        self.assertEqual(self.game.check_winner(), "draw")

if __name__ == "__main__":
    unittest.main()
