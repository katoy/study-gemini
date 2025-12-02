import pytest
from unittest.mock import MagicMock, patch, call
import requests

from CUI.tic_tac_toe_client import TicTacToeClient
from CUI.cui_display import display_board  # Imported for mocking

SERVER_URL = "http://127.0.0.1:8000"


@pytest.fixture
def client():
    return TicTacToeClient(SERVER_URL)


# --- _send_request tests ---


@patch("requests.post")
@patch("requests.get")
def test_send_request_post_success(mock_get, mock_post, client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "ok"}
    mock_post.return_value.raise_for_status.return_value = None

    response = client._send_request("POST", "game/start", {"player_x_type": "Human"})
    mock_post.assert_called_once_with(
        f"{SERVER_URL}/game/start", json={"player_x_type": "Human"}
    )
    assert response == {"status": "ok"}


@patch("requests.post")
@patch("requests.get")
def test_send_request_get_success(mock_get, mock_post, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"status": "ok"}
    mock_get.return_value.raise_for_status.return_value = None

    response = client._send_request("GET", "game/status")
    mock_get.assert_called_once_with(f"{SERVER_URL}/game/status")
    assert response == {"status": "ok"}


@patch("requests.post")
def test_send_request_http_error_400(mock_post, client):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Invalid move"}

    # Configure mock_post to return mock_response and then have raise_for_status raise the error
    mock_post.return_value = mock_response
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response
    )

    with pytest.raises(ValueError, match="Invalid move"):
        client._send_request("POST", "game/move", {"row": 0, "col": 0})
    mock_post.assert_called_once()


@patch("requests.post")
def test_send_request_http_error_404(mock_post, client):
    """404エラーの場合のテスト"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response
    )
    mock_post.return_value = mock_response
    with pytest.raises(ValueError, match="Game not started"):
        client._send_request("POST", "test")


@patch("requests.post")
def test_send_request_connection_error(mock_post, client):
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(requests.exceptions.ConnectionError, match="Connection failed"):
        client._send_request("POST", "game/start", {"player_x_type": "Human"})
    mock_post.assert_called_once()


# --- get_player_symbol_choice tests ---


@patch("builtins.input", side_effect=["x"])
def test_get_player_symbol_choice_x(mock_input, client):
    assert client.get_player_symbol_choice() == "X"


@patch("builtins.input", side_effect=["o"])
def test_get_player_symbol_choice_o(mock_input, client):
    assert client.get_player_symbol_choice() == "O"


@patch("builtins.input", side_effect=["a", "b", "X"])  # First invalid, then valid
@patch("builtins.print")
def test_get_player_symbol_choice_multiple_invalid(mock_print, mock_input, client):
    assert client.get_player_symbol_choice() == "X"
    assert mock_input.call_count == 3
    mock_print.assert_any_call("Invalid choice. Please enter 'X' or 'O'.")


# --- get_agent_type_choice tests ---


@patch("builtins.input", side_effect=["1"])
def test_get_agent_type_choice_human(mock_input, client):
    assert client.get_agent_type_choice("X") == "Human"


@patch("builtins.input", side_effect=["6"])
def test_get_agent_type_choice_perfect(
    mock_input, client
):  # Assuming Perfect is 6th option
    assert client.get_agent_type_choice("O") == "Perfect"


@patch.object(
    TicTacToeClient,
    "get_available_agents",
    return_value=["Human", "Database", "Minimax", "Perfect", "QLearning", "Random"],
)
@patch("builtins.input", side_effect=["0", "7", "2"])  # Invalid, invalid, then valid
@patch("builtins.print")
def test_get_agent_type_choice_invalid_then_valid(
    mock_print, mock_input, mock_get_agents, client
):
    # 動的に取得される agent リストの2番目の要素を期待
    result = client.get_agent_type_choice("X")
    # 2番目の要素は "Database"
    assert result == "Database"
    assert mock_print.call_count >= 2  # 少なくとも2回のエラーメッセージ


# --- get_user_move tests ---


@patch("builtins.input", side_effect=["1"])
def test_get_user_move_valid(mock_input, client):
    assert client.get_user_move() == (0, 0)


@patch("builtins.input", side_effect=["q"])
def test_get_user_move_quit(mock_input, client):
    assert client.get_user_move() is None


@patch(
    "builtins.input", side_effect=["0", "10", "a", "5"]
)  # Invalid, invalid, invalid, then valid
@patch("builtins.print")
def test_get_user_move_invalid_then_valid(mock_print, mock_input, client):
    assert client.get_user_move() == (1, 1)  # '5' -> (1,1)
    assert mock_print.call_count == 3  # Three calls for invalid input


@patch("builtins.input", side_effect=["10", "0", "1"])
@patch("builtins.print")
def test_get_user_move_out_of_range_multiple(mock_print, mock_input, client):
    """1-9以外の数値を入力するケース"""
    client.get_user_move()
    assert mock_input.call_count == 3
    mock_print.assert_any_call("Invalid input. Please enter a number between 1 and 9.")


# --- play_single_game tests ---


@patch("CUI.tic_tac_toe_client.display_board")
@patch.object(TicTacToeClient, "_send_request")
@patch.object(TicTacToeClient, "get_player_symbol_choice", return_value="X")
@patch.object(TicTacToeClient, "get_agent_type_choice", side_effect=["Human", "Random"])
def test_play_single_game_start_error(
    mock_get_agent_type,
    mock_get_player_symbol,
    mock_send_request,
    mock_display_board,
    client,
):
    mock_send_request.side_effect = requests.exceptions.RequestException("Start failed")

    result = client.play_single_game()
    assert result is None  # Should return None on error
    mock_send_request.assert_called_once_with(
        "POST",
        "game/start",
        {
            "human_player_symbol": "X",
            "player_x_type": "Human",
            "player_o_type": "Random",
        },
    )
    mock_display_board.assert_not_called()


@patch("CUI.tic_tac_toe_client.display_board")
@patch.object(TicTacToeClient, "_send_request")
@patch.object(TicTacToeClient, "get_player_symbol_choice", return_value="X")
@patch.object(TicTacToeClient, "get_agent_type_choice", side_effect=["Human", "Random"])
@patch.object(
    TicTacToeClient, "get_user_move", side_effect=[(0, 0), (0, 1), None]
)  # User quits on 3rd move
def test_play_single_game_human_quits(
    mock_get_user_move,
    mock_get_agent_type,
    mock_get_player_symbol,
    mock_send_request,
    mock_display_board,
    client,
):
    # Simulate game start
    mock_send_request.side_effect = [
        {
            "board": [[" ", " ", " "]] * 3,
            "current_player": "X",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Start game (1)
        {
            "board": [["X", " ", " "]] * 3,
            "current_player": "O",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Human move 1 (2)
        {
            "board": [["X", "O", " "]] * 3,
            "current_player": "X",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Agent move 1 (3)
        {
            "board": [["X", "O", "X"]] * 3,
            "current_player": "O",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Human move 2 (4)
        {
            "board": [["X", "O", "X"], ["O", " ", " "], [" ", " ", " "]],
            "current_player": "X",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Agent move 2 (5)
    ]

    with patch("builtins.print") as mock_print:
        client.play_single_game()
        mock_print.assert_any_call("Game interrupted by user.")

    assert mock_get_user_move.call_count == 3
    assert mock_send_request.call_count == 5  # Corrected from 4
    mock_display_board.assert_called()


@patch("CUI.tic_tac_toe_client.display_board")
@patch.object(TicTacToeClient, "_send_request")
@patch.object(TicTacToeClient, "get_player_symbol_choice", return_value="X")
@patch.object(TicTacToeClient, "get_agent_type_choice", side_effect=["Human", "Random"])
@patch.object(TicTacToeClient, "get_user_move", side_effect=[(0, 0), (0, 1), (0, 2)])
def test_play_single_game_human_win(
    mock_get_user_move,
    mock_get_agent_type,
    mock_get_player_symbol,
    mock_send_request,
    mock_display_board,
    client,
):
    # Simulate game start, 2 human moves, and then human wins
    mock_send_request.side_effect = [
        {
            "board": [[" ", " ", " "]] * 3,
            "current_player": "X",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Start game (1)
        {
            "board": [["X", " ", " "]] * 3,
            "current_player": "O",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Human move 1 (2)
        {
            "board": [["X", "O", " "]] * 3,
            "current_player": "X",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Agent move 1 (3)
        {
            "board": [["X", "O", "X"], [" ", " ", " "], [" ", " ", " "]],
            "current_player": "O",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Human move 2 (4)
        {
            "board": [["X", "O", "X"], ["O", " ", " "], [" ", " ", " "]],
            "current_player": "X",
            "winner": "X",
            "winner_line": ((0, 0), (0, 1), (0, 2)),
            "game_over": True,
        },  # Agent move 2 (O) -> human X wins (5)
    ]

    client.play_single_game()
    assert mock_get_user_move.call_count == 2
    assert mock_send_request.call_count == 5  # Corrected from 4
    mock_display_board.assert_called()


@patch("CUI.tic_tac_toe_client.display_board")
@patch.object(TicTacToeClient, "_send_request")
@patch.object(TicTacToeClient, "get_player_symbol_choice", return_value="O")
@patch.object(TicTacToeClient, "get_agent_type_choice", side_effect=["Random", "Human"])
@patch("time.sleep")  # Mock time.sleep for agent turn
def test_play_single_game_agent_turn_and_request_error(
    mock_sleep,
    mock_get_agent_type,
    mock_get_player_symbol,
    mock_send_request,
    mock_display_board,
    client,
):
    # Simulate game start with O as human, X as agent
    mock_send_request.side_effect = [
        {
            "board": [[" ", " ", " "]] * 3,
            "current_player": "X",
            "winner": None,
            "winner_line": None,
            "game_over": False,
        },  # Start game (1)
        # Agent's turn, status GET fails
        requests.exceptions.RequestException,
    ]

    with patch.object(TicTacToeClient, "get_user_move"):
        client.play_single_game()

    assert mock_send_request.call_count == 2
    mock_sleep.assert_called_once()
    mock_display_board.assert_called_once()  # Only at the start
