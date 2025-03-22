import unittest
import tkinter as tk
from gui import TicTacToeGUI
from game_logic import TicTacToe

class TestTicTacToeGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        # テスト実行時にウィンドウが実際に表示されなくても、geometry マネージャの状態を確認するために withdraw は行います
        self.root.withdraw()
        self.gui = TicTacToeGUI(self.root)
        self.root.update_idletasks()

    def tearDown(self):
        self.root.destroy()

    def test_initial_settings_ui(self):
        """初回の設定画面が正しく構築されていることを確認する"""
        self.assertTrue(self.gui.start_game_frame.winfo_exists())
        self.assertTrue(self.gui.start_button.winfo_exists())

    def test_start_game_creates_tictactoe_instance(self):
        """設定画面からゲーム開始時、TicTacToe インスタンスが生成され、設定画面が破棄されることを確認する"""
        self.gui.player_var.set(True)
        self.gui.agent_var.set("Minimax")
        self.gui.start_game()
        self.root.update()
        self.assertIsInstance(self.gui.game, TicTacToe)
        self.assertFalse(self.gui.start_game_frame.winfo_exists())

    def test_game_over_shows_restart_buttons(self):
        """ゲーム終了後、再開用ボタンフレームが表示されることを確認する"""
        self.gui.player_var.set(True)
        self.gui.agent_var.set("Minimax")
        self.gui.start_game()
        self.gui.game_over("X")
        self.root.update_idletasks()
        self.root.update()
        # withdraw されている場合、winfo_ismapped() は False となるため、pack_info() によりウィジェットが pack されていることをチェックする
        self.assertNotEqual(self.gui.restart_buttons_frame.winfo_manager(), '')

    def test_restart_game_same_settings_human_first(self):
        """人間が先手の場合、同じ設定で再開すると新しいゲームインスタンスが生成され、キャンバスにクリックイベントがバインドされることを確認する"""
        self.gui.player_var.set(True)
        self.gui.agent_var.set("Minimax")
        self.gui.start_game()
        original_game = self.gui.game
        self.gui.game_over("X")
        self.root.update_idletasks()
        self.gui.restart_game_same_settings()
        self.root.update_idletasks()
        binding = self.gui.canvas.bind("<Button-1>")
        self.assertIsNotNone(binding)
        self.assertNotEqual(binding, "")

    def test_restart_game_same_settings_human_second(self):
        """人間が後手の場合、同じ設定で再開するとエージェントの初手が実行され、盤面に少なくとも1セル以上が更新されることを確認する"""
        self.gui.player_var.set(False)
        self.gui.agent_var.set("Minimax")
        self.gui.start_game()
        self.root.update_idletasks()
        self.gui.game_over("O")
        self.root.update_idletasks()
        self.gui.restart_game_same_settings()
        self.root.update_idletasks()
        board_filled = any(cell != " " for row in self.gui.game.board for cell in row)
        self.assertTrue(board_filled)

    def test_restart_game_with_settings(self):
        """条件再設定を選んだ場合、設定画面が再構築されることを確認する"""
        self.gui.player_var.set(True)
        self.gui.agent_var.set("ランダム")
        self.gui.start_game()
        self.gui.game_over("O")
        self.root.update_idletasks()
        self.gui.restart_game_with_settings()
        self.root.update_idletasks()
        self.assertTrue(hasattr(self.gui, 'start_game_frame'))
        self.assertTrue(self.gui.start_game_frame.winfo_exists())

if __name__ == '__main__':
    unittest.main()
