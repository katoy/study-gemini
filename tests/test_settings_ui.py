import unittest
from unittest.mock import MagicMock
from settings_ui import SettingsUI
import tkinter as tk


class TestSettingsUI(unittest.TestCase):
    def test_build_settings_ui(self):
        root = tk.Tk()  # ルートウィンドウを作成
        mock_gui = MagicMock()
        mock_master = root
        settings_ui = SettingsUI(mock_gui, mock_master)
        settings_ui.build_settings_ui()
        self.assertEqual(mock_gui.start_game.call_count, 1)
        root.destroy()
