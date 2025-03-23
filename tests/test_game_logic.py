import unittest
from unittest.mock import patch, MagicMock
from game_logic import TicTacToe
from agents.database_agent import DatabaseAgent # 追加

class TestTicTacToeAgentMove(unittest.TestCase):
    def setUp(self):
        self.empty_board = [[" " for _ in range(3)] for _ in range(3)]
        self.full_board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]

    def test_agent_move_makes_move_random(self):
        """ランダムエージェントが手を打つことを確認"""
        game = TicTacToe(False, "ランダム")
        game.agent_move()
        self.assertNotEqual(game.board, self.empty_board)

    def test_agent_move_makes_move_minimax(self):
        """Minimaxエージェントが手を打つことを確認"""
        game = TicTacToe(False, "Minimax")
        game.agent_move()
        self.assertNotEqual(game.board, self.empty_board)

    def test_agent_move_makes_move_database(self):
        """Databaseエージェントが手を打つことを確認"""
        game = TicTacToe(False, "Database")
        game.agent_move()
        self.assertNotEqual(game.board, self.empty_board)

    def test_agent_move_no_move_when_board_full_random(self):
        """盤面が埋まっている場合、ランダムエージェントが手を打たないことを確認"""
        game = TicTacToe(False, "ランダム")
        game.board = self.full_board
        game.agent_move()
        self.assertEqual(game.board, self.full_board)

    def test_agent_move_no_move_when_board_full_minimax(self):
        """盤面が埋まっている場合、Minimaxエージェントが手を打たないことを確認"""
        game = TicTacToe(False, "Minimax")
        game.board = self.full_board
        game.agent_move()
        self.assertEqual(game.board, self.full_board)

    def test_agent_move_no_move_when_board_full_database(self):
        """盤面が埋まっている場合、Databaseエージェントが手を打たないことを確認"""
        game = TicTacToe(False, "Database")
        game.board = self.full_board
        game.agent_move()
        self.assertEqual(game.board, self.full_board)

    @patch.object(DatabaseAgent, "get_move")
    def test_agent_move_database_agent_returns_none(self, mock_get_move):
        """DatabaseエージェントがNoneを返した場合、agent_moveがFalseを返すことを確認"""
        mock_get_move.return_value = None
        game = TicTacToe(False, "Database")
        result = game.agent_move()
        self.assertFalse(result)

    def test_agent_move_when_game_over(self):
        """ゲームが終了している場合、agent_moveが実行されないことを確認"""
        game = TicTacToe(False, "Database")
        game.game_over = True
        original_board = [row[:] for row in game.board]
        game.agent_move()
        self.assertEqual(game.board, original_board)

if __name__ == "__main__":
    unittest.main()
