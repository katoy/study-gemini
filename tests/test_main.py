import unittest
from unittest.mock import patch
import sys


class TestMain(unittest.TestCase):
    @patch("main.tk.Tk")
    @patch("main.TicTacToeGUI")
    def test_main_function(self, mock_gui, mock_tk):
        """main関数が正しく実行されるか"""
        mock_root = mock_tk.return_value
        mock_root.mainloop = unittest.mock.Mock()

        # main.pyをインポート
        import main

        # main関数を実行
        main.main()

        # Tkインスタンスが作成されたことを確認
        mock_tk.assert_called_once()
        # GUIが作成されたことを確認
        mock_gui.assert_called_once_with(mock_root)
        # mainloopが呼ばれたことを確認
        mock_root.mainloop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
