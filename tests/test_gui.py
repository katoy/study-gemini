import unittest
import tkinter as tk
from gui import TicTacToeGUI
from game_logic import TicTacToe

class TestTicTacToeGUI(unittest.TestCase):
    def setUp(self):
        # Tk のルートウィンドウを生成し、テスト実行中は表示しない
        self.root = tk.Tk()
        self.root.withdraw()
        self.gui = TicTacToeGUI(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_initial_settings_ui(self):
        """初回の設定画面が正しく構築されていることを確認する"""
        self.assertIsNotNone(self.gui.start_game_frame)
        # 設定画面のウィジェットが存在していること
        self.assertTrue(self.gui.start_game_frame.winfo_exists())
        # ゲーム開始ボタンが設定画面内にあるかチェック
        self.assertTrue(self.gui.start_button.winfo_exists())

    def test_start_game_creates_tictactoe_instance(self):
        """設定画面からゲーム開始した際、TicTacToe のインスタンスが生成されることを確認する"""
        # 設定値を変更
        self.gui.player_var.set(True)
        self.gui.agent_var.set("Minimax")
        self.gui.start_game()
        self.assertIsInstance(self.gui.game, TicTacToe)
        # 設定画面が破棄されていることを確認
        self.assertFalse(self.gui.start_game_frame.winfo_exists())

    def test_game_over_shows_restart_buttons(self):
        """ゲーム終了後、再開用ボタンフレームが表示されることを確認する"""
        self.gui.player_var.set(True)
        self.gui.agent_var.set("Minimax")
        self.gui.start_game()
        # 仮にゲーム終了処理を呼び出す（ここでは "X" の勝ちとして）
        self.gui.game_over("X")
        # 再開用ボタンフレームが表示されているか
        self.assertTrue(self.gui.restart_buttons_frame.winfo_ismapped())

    def test_restart_game_same_settings(self):
        """同じ設定で再開した場合に、新しいゲームインスタンスが生成されることを確認する"""
        self.gui.player_var.set(True)
        self.gui.agent_var.set("Minimax")
        self.gui.start_game()
        original_game = self.gui.game
        # ゲーム終了状態をシミュレーション
        self.gui.game_over("X")
        # 同じ設定で再開
        self.gui.restart_game_same_settings()
        self.assertIsInstance(self.gui.game, TicTacToe)
        self.assertNotEqual(self.gui.game, original_game)
        # キャンバスにクリックイベントがバインドされているか（バインド情報が空でないことを確認）
        binding = self.gui.canvas.bind("<Button-1>")
        self.assertIsNotNone(binding)
        self.assertNotEqual(binding, "")

    def test_restart_game_with_settings(self):
        """条件再設定を選んだ場合、設定画面が再構築されることを確認する"""
        self.gui.player_var.set(False)
        self.gui.agent_var.set("Random")
        self.gui.start_game()
        # ゲーム終了処理を呼び出す
        self.gui.game_over("O")
        # 条件再設定を実行
        self.gui.restart_game_with_settings()
        # 設定画面用のウィジェットが再構築されているはず
        self.assertTrue(hasattr(self.gui, 'start_game_frame'))
        self.assertTrue(self.gui.start_game_frame.winfo_exists())

if __name__ == '__main__':
    unittest.main()
