import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

from settings_ui import SettingsUI


class TestSettingsUI(unittest.TestCase):
    def setUp(self):
        self.master = tk.Tk()
        self.master.withdraw()  # ウィンドウを非表示にする
        self.mock_gui = MagicMock()
        # SettingsUIは実際のtk.Tkインスタンスを必要とする
        self.settings_ui = SettingsUI(self.mock_gui, self.master)

    def tearDown(self):
        self.master.destroy()

    def test_build_settings_ui(self):
        self.settings_ui.build_settings_ui()
        start_button = self.settings_ui.start_button
        # UIのテストではinvoke()の代わりにcommandを直接呼ぶ方が安定することがある
        self.settings_ui.start_game()
        self.mock_gui.start_game.assert_called_once()

    def test_save_and_load_settings(self):
        self.settings_ui.build_settings_ui()
        self.settings_ui.player_var.set(False)
        self.settings_ui.agent_var.set("Minimax")

        saved_settings = self.settings_ui.save_settings()

        # 新しい設定でロード
        self.settings_ui.player_var.set(True)
        self.settings_ui.agent_var.set("ランダム")
        self.settings_ui.load_settings(saved_settings)

        self.assertFalse(self.settings_ui.player_var.get())
        self.assertEqual(self.settings_ui.agent_var.get(), "Minimax")

    def test_build_settings_ui_twice(self):
        """build_settings_uiを2回呼び出しても正常に動作するか"""
        self.settings_ui.build_settings_ui()
        self.assertIsNotNone(self.settings_ui.settings_frame)
        # 2回目の呼び出し
        self.settings_ui.build_settings_ui()
        self.assertIsNotNone(self.settings_ui.settings_frame)

    @patch("os.path.exists", return_value=False)
    def test_discover_agents_no_directory(self, mock_exists):
        """agentsディレクトリが存在しないケースをテスト"""
        ui = SettingsUI(self.mock_gui, self.master)
        self.assertEqual(ui.agent_options_for_display, [])
        self.assertEqual(ui.agent_var.get(), "エージェントなし")

    @patch("os.listdir", return_value=[])
    @patch("os.path.exists", return_value=True)
    def test_discover_agents_no_agents_found(self, mock_exists, mock_listdir):
        """agentsディレクトリが空のケースをテスト"""
        ui = SettingsUI(self.mock_gui, self.master)
        self.assertEqual(ui.agent_options_for_display, [])
        self.assertEqual(ui.agent_var.get(), "エージェントなし")

    @patch("importlib.import_module", side_effect=ImportError("Test import error"))
    @patch("os.listdir", return_value=["faulty_agent.py"])
    @patch("os.path.exists", return_value=True)
    @patch("builtins.print")
    def test_discover_agents_import_error(
        self, mock_print, mock_exists, mock_listdir, mock_import
    ):
        """エージェントのインポートに失敗するケースをテスト"""
        # __init__内で_discover_agentsが呼ばれるので、インスタンス化するだけでよい
        ui = SettingsUI(self.mock_gui, self.master)
        # エージェントが見つからないので空のリストになる
        self.assertEqual(ui.AGENT_CLASSES, {})
        mock_print.assert_called_with(
            "Warning: Could not import agent from faulty_agent: Test import error"
        )
