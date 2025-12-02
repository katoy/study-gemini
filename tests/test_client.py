import pytest
from unittest.mock import patch, MagicMock
from CUI.client import main


# TicTacToeClientをモック化
@patch("CUI.client.TicTacToeClient")
def test_main_loop_play_once_and_exit(MockTicTacToeClient):
    """
    1回プレイして終了するケースをテスト
    """
    # input()が'n'を返すように設定
    with patch("builtins.input", return_value="n"):
        mock_client_instance = MockTicTacToeClient.return_value
        main()
        # play_single_gameが1回呼ばれることを確認
        mock_client_instance.play_single_game.assert_called_once()


@patch("CUI.client.TicTacToeClient")
def test_main_loop_play_twice_and_exit(MockTicTacToeClient):
    """
    2回プレイして終了するケースをテスト
    """
    # input()が最初に'y'、次に'n'を返すように設定
    with patch("builtins.input", side_effect=["y", "n"]):
        mock_client_instance = MockTicTacToeClient.return_value
        main()
        # play_single_gameが2回呼ばれることを確認
        assert mock_client_instance.play_single_game.call_count == 2
