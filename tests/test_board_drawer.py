import unittest
from unittest.mock import MagicMock, Mock, patch
import tkinter as tk

from board_drawer import BoardDrawer


class TestBoardDrawer(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=300, height=300)
        self.mock_gui = MagicMock()
        self.mock_gui.game = MagicMock()
        self.mock_gui.game.board = [[" " for _ in range(3)] for _ in range(3)]
        self.board_drawer = BoardDrawer(self.mock_gui, self.canvas)

    def tearDown(self):
        self.root.destroy()

    def test_init(self):
        """BoardDrawerが正しく初期化されるか"""
        self.assertEqual(self.board_drawer.gui, self.mock_gui)
        self.assertEqual(self.board_drawer.canvas, self.canvas)

    def test_create_board_lines(self):
        """ボードの線が正しく描画されるか"""
        self.board_drawer.create_board_lines()
        # Canvas上に線が描画されていることを確認
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_draw_board_empty(self):
        """空のボードが正しく描画されるか"""
        self.board_drawer.draw_board()
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_draw_board_with_x(self):
        """X が正しく描画されるか"""
        self.mock_gui.game.board[0][0] = "X"
        self.board_drawer.draw_board()
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_draw_board_with_o(self):
        """O が正しく描画されるか"""
        self.mock_gui.game.board[1][1] = "O"
        self.board_drawer.draw_board()
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_draw_x(self):
        """draw_x が正しく機能するか"""
        self.board_drawer.draw_x(10, 10, 90, 90)
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_draw_o(self):
        """draw_o が正しく機能するか"""
        self.board_drawer.draw_o(10, 10, 90, 90)
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_highlight_winner_cells(self):
        """勝利セルのハイライトが正しく機能するか"""
        self.mock_gui.game.board[0][0] = "X"
        self.mock_gui.game.board[0][1] = "X"
        self.mock_gui.game.board[0][2] = "X"
        winner_line = ((0, 0), (0, 1), (0, 2))
        self.board_drawer.highlight_winner_cells(winner_line)
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_highlight_winner_cells_with_o(self):
        """勝利セル（O）のハイライトが正しく機能するか"""
        self.mock_gui.game.board[1][0] = "O"
        self.mock_gui.game.board[1][1] = "O"
        self.mock_gui.game.board[1][2] = "O"
        winner_line = ((1, 0), (1, 1), (1, 2))
        self.board_drawer.highlight_winner_cells(winner_line)
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_remove_winner_highlight(self):
        """勝利ハイライトが正しく削除されるか"""
        # まずハイライトを追加
        self.canvas.create_rectangle(0, 0, 100, 100, fill="yellow", tags="winner_cell")
        # 削除
        self.board_drawer.remove_winner_highlight()
        # winner_cellタグのアイテムがないことを確認
        items = self.canvas.find_withtag("winner_cell")
        self.assertEqual(len(items), 0)


if __name__ == "__main__":
    unittest.main()
