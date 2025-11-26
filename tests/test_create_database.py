import unittest
from unittest.mock import MagicMock, patch, call, mock_open
import tempfile
import os
from create_database import (
    check_winner,
    is_board_full,
    board_to_string,
    get_opponent,
    minimax,
    insert_to_db,
    create_database,
    main,
)


class TestCreateDatabase(unittest.TestCase):
    def test_check_winner_horizontal(self):
        """水平方向の勝利を検出できるか"""
        board = [["X", "X", "X"], [" ", " ", " "], [" ", " ", " "]]
        self.assertEqual(check_winner(board), "X")

    def test_check_winner_vertical(self):
        """垂直方向の勝利を検出できるか"""
        board = [["O", " ", " "], ["O", " ", " "], ["O", " ", " "]]
        self.assertEqual(check_winner(board), "O")

    def test_check_winner_diagonal(self):
        """対角線の勝利を検出できるか"""
        board = [["X", " ", " "], [" ", "X", " "], [" ", " ", "X"]]
        self.assertEqual(check_winner(board), "X")

    def test_check_winner_reverse_diagonal(self):
        """逆対角線の勝利を検出できるか"""
        board = [[" ", " ", "O"], [" ", "O", " "], ["O", " ", " "]]
        self.assertEqual(check_winner(board), "O")

    def test_check_winner_no_winner(self):
        """勝者がいない場合にNoneを返すか"""
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        self.assertIsNone(check_winner(board))

    def test_is_board_full_true(self):
        """ボードが満杯の場合にTrueを返すか"""
        board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]
        self.assertTrue(is_board_full(board))

    def test_is_board_full_false(self):
        """ボードが満杯でない場合にFalseを返すか"""
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        self.assertFalse(is_board_full(board))

    def test_board_to_string(self):
        """ボードを文字列に変換できるか"""
        board = [["X", "O", " "], [" ", "X", " "], [" ", " ", "O"]]
        self.assertEqual(board_to_string(board), "XO  X   O")

    def test_get_opponent(self):
        """相手プレイヤーを正しく取得できるか"""
        self.assertEqual(get_opponent("X"), "O")
        self.assertEqual(get_opponent("O"), "X")

    def test_minimax_win(self):
        """Xが勝利する盤面でminimaxが正のスコアを返すか"""
        board = [["X", "X", "X"], [" ", " ", " "], [" ", " ", " "]]
        score = minimax(board, 0, True, "X")
        self.assertGreater(score, 0)

    def test_minimax_loss(self):
        """Oが勝利する盤面でminimaxが負のスコアを返すか"""
        board = [["O", "O", "O"], [" ", " ", " "], [" ", " ", " "]]
        score = minimax(board, 0, True, "X")
        self.assertLess(score, 0)

    def test_minimax_draw(self):
        """引き分けの盤面でminimaxが0を返すか"""
        board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]
        score = minimax(board, 0, True, "X")
        self.assertEqual(score, 0)

    def test_minimax_maximizing(self):
        """minimax最大化プレイヤーの動作を確認"""
        board = [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        score = minimax(board, 0, True, "X")
        self.assertIsInstance(score, (int, float))

    def test_minimax_minimizing(self):
        """minimax最小化プレイヤーの動作を確認"""
        board = [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        score = minimax(board, 0, False, "X")
        self.assertIsInstance(score, (int, float))

    @patch('create_database.sqlite3')
    def test_insert_to_db(self, mock_sqlite3):
        """データベースにデータを挿入できるか"""
        mock_cursor = MagicMock()
        insert_to_db(mock_cursor, "XO  X   O", 4, "continue")
        mock_cursor.execute.assert_called_once()

    @patch('create_database.logging')
    def test_create_database_with_winner(self, mock_logging):
        """勝者がいる状態でcreate_databaseが正しく動作するか"""
        mock_cursor = MagicMock()
        board = [["X", "X", "X"], [" ", " ", " "], [" ", " ", " "]]
        seen = set()
        perfect_moves = {}
        
        create_database(board, "X", mock_cursor, seen, perfect_moves)
        
        self.assertIn("XXX      ", seen)
        self.assertEqual(perfect_moves["XXX      "], -1)
        mock_cursor.execute.assert_called()

    @patch('create_database.logging')
    def test_create_database_with_draw(self, mock_logging):
        """引き分け状態でcreate_databaseが正しく動作するか"""
        mock_cursor = MagicMock()
        board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]
        seen = set()
        perfect_moves = {}
        
        create_database(board, "X", mock_cursor, seen, perfect_moves)
        
        board_str = board_to_string(board)
        self.assertIn(board_str, seen)
        self.assertEqual(perfect_moves[board_str], -1)

    @patch('create_database.logging')
    def test_create_database_ongoing_game(self, mock_logging):
        """進行中のゲームでcreate_databaseが最適手を計算するか"""
        mock_cursor = MagicMock()
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        seen = set()
        perfect_moves = {}
        
        create_database(board, "X", mock_cursor, seen, perfect_moves)
        
        # 盤面が登録されたことを確認
        self.assertGreater(len(seen), 0)
        self.assertGreater(len(perfect_moves), 0)

    @patch('create_database.logging')
    def test_create_database_skip_seen(self, mock_logging):
        """既に処理済みの盤面をスキップするか"""
        mock_cursor = MagicMock()
        board = [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        board_str = board_to_string(board)
        seen = {board_str}  # 既に処理済み
        perfect_moves = {}
        
        create_database(board, "X", mock_cursor, seen, perfect_moves)
        
        # データベースへの挿入が行われないことを確認
        mock_cursor.execute.assert_not_called()

    @patch('create_database.json.dump')
    @patch('create_database.sqlite3.connect')
    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open)
    def test_main(self, mock_file, mock_print, mock_connect, mock_json_dump):
        """main関数が正しく実行されるか"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # main関数を実行
        main()
        
        # データベース接続が行われたことを確認
        mock_connect.assert_called_once_with("tictactoe.db")
        
        # テーブル作成が行われたことを確認（create_databaseで多数のexecuteが呼ばれる）
        self.assertGreater(mock_cursor.execute.call_count, 1)
        
        # コミットとクローズが行われたことを確認
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # 成功メッセージが表示されたことを確認
        self.assertEqual(mock_print.call_count, 2)
        
        # JSONファイルが保存されたことを確認
        mock_json_dump.assert_called_once()


if __name__ == "__main__":
    unittest.main()
