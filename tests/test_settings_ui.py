import unittest
from unittest.mock import MagicMock
import tkinter as tk

from settings_ui import SettingsUI


class TestSettingsUI(unittest.TestCase):
    def setUp(self):
        self.master = tk.Tk()
        self.mock_gui = MagicMock()
        self.settings_ui = SettingsUI(self.mock_gui, self.master)

    def tearDown(self):
        self.master.destroy()

    def test_build_settings_ui(self):
        self.settings_ui.build_settings_ui()
        self.start_button = self.settings_ui.start_button
        self.start_button.invoke()
        self.assertEqual(self.mock_gui.start_game.call_count, 1)

    def test_save_and_load_settings(self):
        self.settings_ui.build_settings_ui()
        self.settings_ui.player_var.set(False)
        self.settings_ui.agent_var.set("Minimax")
        saved_settings = self.settings_ui.save_settings()
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

if __name__ == "__main__":
    unittest.main()
