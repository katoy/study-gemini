"""CUI/tic_tac_toe_client.py の未カバー分岐を補うテスト。"""

from unittest.mock import patch

from CUI.tic_tac_toe_client import TicTacToeClient

SERVER_URL = "http://127.0.0.1:8000"


@patch("builtins.print")
@patch("CUI.tic_tac_toe_client.display_board")
@patch.object(TicTacToeClient, "_send_request")
@patch.object(TicTacToeClient, "get_user_move", return_value=(0, 0))
@patch.object(TicTacToeClient, "get_agent_type_choice", side_effect=["Random", "Human"])
def test_play_single_game(
    mock_get_agent_type,
    mock_get_user_move,
    mock_send_request,
    mock_display_board,
    mock_print,
):
    """人間が O を担当し、O の手番で 1 手打ってゲームが終了する。"""
    mock_send_request.side_effect = [
        {
            "board": [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]],
            "current_player": "O",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },
        {
            "board": [["X", "O", " "], [" ", " ", " "], [" ", " ", " "]],
            "current_player": "X",
            "winner": "draw",
            "winner_line": None,
            "game_over": True,
        },
    ]
    client = TicTacToeClient(SERVER_URL)

    assert client.play_single_game() is None

    assert mock_send_request.call_args_list[0].args == (
        "POST",
        "game/start",
        {
            "human_player_symbol": "O",
            "player_x_type": "Random",
            "player_o_type": "Human",
        },
    )
    mock_send_request.assert_called_with("POST", "game/move", {"row": 0, "col": 0})
    mock_get_user_move.assert_called_once()
    assert mock_display_board.call_count == 2


@patch("builtins.print")
@patch("CUI.tic_tac_toe_client.display_board")
@patch.object(TicTacToeClient, "_send_request")
@patch.object(TicTacToeClient, "get_user_move")
@patch.object(TicTacToeClient, "get_agent_type_choice", side_effect=["Human", "Random"])
def test_play_single_game_agent_turn(
    mock_get_agent_type,
    mock_get_user_move,
    mock_send_request,
    mock_display_board,
    mock_print,
):
    """サーバーがエージェントの手番を進めずに返した場合は無限ループせずゲームを終了する。"""
    mock_send_request.return_value = {
        "board": [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]],
        "current_player": "O",
        "winner": None,
        "winner_line": None,
        "game_over": False,
    }
    client = TicTacToeClient(SERVER_URL)

    assert client.play_single_game() is None

    mock_send_request.assert_called_once()
    mock_get_user_move.assert_not_called()
    mock_print.assert_any_call(
        "Error: The server did not process Player O (Agent)'s move. Ending the game."
    )
