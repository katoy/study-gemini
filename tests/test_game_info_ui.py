import unittest
from unittest.mock import MagicMock, patch
from game_info_ui import GameInfoUI


class TestGameInfoUI(unittest.TestCase):
    @patch("game_info_ui.tk.Frame")
    @patch("game_info_ui.tk.Label")
    @patch.object(GameInfoUI, "update_game_info")
    def test_show_game_info(self, mock_update_game_info, MockLabel, MockFrame):
        mock_gui = MagicMock()
        mock_master = MagicMock()
        mock_frame = MagicMock()
        MockFrame.return_value = mock_frame
        game_info_ui = GameInfoUI(mock_gui, mock_master)
        game_info_ui.show_game_info()
        mock_frame.pack.assert_called_once_with(pady=10)
        self.assertEqual(mock_update_game_info.call_count, 1)

    @patch("game_info_ui.tk.Frame")
    @patch("game_info_ui.tk.Label")
    def test_update_game_info(self, MockLabel, MockFrame):
        mock_gui = MagicMock()
        mock_gui.selected_player = True
        mock_gui.selected_agent = "ランダム"
        mock_master = MagicMock()
        mock_player_label = MagicMock()
        mock_agent_label = MagicMock()
        MockLabel.side_effect = [mock_player_label, mock_agent_label]
        game_info_ui = GameInfoUI(mock_gui, mock_master)
        game_info_ui.update_game_info()
        mock_player_label.config.assert_called_once_with(text="先手: あなた")
        mock_agent_label.config.assert_called_once_with(text="エージェント: ランダム")
