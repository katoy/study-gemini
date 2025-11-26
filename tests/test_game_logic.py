import unittest
from unittest.mock import patch, MagicMock
from game_logic import TicTacToe
from agents.database_agent import DatabaseAgent # 追加

class TestGameLogic(unittest.TestCase): # 新しいテストクラス
    def setUp(self):
        self.empty_board = [[" " for _ in range(3)] for _ in range(3)]
        self.full_board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]

    def test_make_move_when_game_over(self):
        """ゲーム終了後に移動できないことを確認"""
        game = TicTacToe(human_player="X") # 修正
        game.game_over = True
        result = game.make_move(0, 0)
        self.assertFalse(result)
        self.assertEqual(game.board[0][0], " ")

    def test_check_winner_diagonal_reverse(self):
        """右上から左下への対角線の勝利を確認"""
        game = TicTacToe(human_player="X") # 修正
        game.board = [
            [" ", " ", "X"],
            [" ", "X", " "],
            ["X", " ", " "]
        ]
        winner = game.check_winner()
        self.assertEqual(winner, "X")
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner_line, ((0, 2), (1, 1), (2, 0)))

    def test_make_move_on_occupied_cell(self):
        """既に埋まっているセルへの移動が失敗することを確認"""
        game = TicTacToe(human_player="X") # 修正
        # セル(0,0)に移動
        game.make_move(0, 0)
        # 同じセルに再度移動しようとする
        result = game.make_move(0, 0)
        self.assertFalse(result)
        # ボードの状態が変わっていないことを確認
        self.assertEqual(game.board[0][0], "X")

    def test_check_winner_no_winner_yet(self):
        """勝者がまだいない状態でNoneが返されることを確認"""
        game = TicTacToe(human_player="X") # 修正
        # 部分的に埋まっているが勝者も引き分けでもない盤面
        game.board = [
            ["X", "O", " "],
            [" ", "X", " "],
            [" ", " ", " "]
        ]
        winner = game.check_winner()
        self.assertIsNone(winner)
        self.assertFalse(game.game_over)

    def test_get_current_agent_o_player(self):
        """現在のプレイヤーがOの場合にagent_oが返されることを確認"""
        mock_agent_x = MagicMock()
        mock_agent_o = MagicMock() # MagicMock に戻す
        game = TicTacToe(agent_x=mock_agent_x, agent_o=mock_agent_o, human_player="X")
        game.current_player = "O" # current_player を O に設定
        current_agent = game.get_current_agent()
        self.assertIs(current_agent, mock_agent_o) # assertEqual の代わりに assertIs を使用


