import pytest
from unittest.mock import patch
from ble_server.game_adapter import GameAdapter


@pytest.fixture
def adapter():
    return GameAdapter(default_ai_agent="Random")


def test_initialization(adapter):
    assert adapter.default_ai_agent == "Random"
    assert adapter.game_manager is not None


def test_start_game_human_x(adapter):
    """Test START command where Human is X (First player)."""
    response = adapter.handle_command("START:X")
    # Initial board should be empty (dots)
    # Result should be ONGOING
    # Format: ".........:ONGOING:"
    assert response == ".........:ONGOING:"


def test_start_game_human_o(adapter):
    """
    Test START command where Human is O.
    AI (X) moves first, so board should not be empty.
    """
    with patch(
        "random.choice", return_value=(1, 1)
    ):  # Mock AI move to center if Random
        # Ideally we'd mock the agent's get_move, but Random agent uses random.choice usually.
        # Let's check that the board has one 'X'.
        response = adapter.handle_command("START:O")

        parts = response.split(":")
        board_str = parts[0]
        status = parts[1]

        assert status == "ONGOING"
        assert board_str.count("X") == 1
        assert board_str.count("O") == 0


def test_move_command_valid(adapter):
    """Test a valid move for Human (X)."""
    # Start: X... (Human X)
    # Command: MOVE:0:X:.........
    # Response should have X at index 0.

    # We mock run_ai_move to do nothing or ensure it doesn't run if game not over
    # But usually adapter runs AI move immediately after human move.
    # If we want to test just the human move, we might need to mock game_manager.run_ai_move

    with patch.object(adapter.game_manager, "run_ai_move") as mock_ai_move:
        # Make AI move return the game object as is
        mock_ai_move.side_effect = lambda g: g

        response = adapter.handle_command("MOVE:0:X:.........")

        # Human moving at 0 -> 'X' at 0.
        # Board: X........
        assert response.startswith("X........:ONGOING")


def test_move_command_with_ai_response(adapter):
    """Test human move followed by AI move."""
    # Human X at 0. AI O.
    # AI should also move.
    # Human sends: MOVE:0:X:.........
    # Result board should have 1 X and 1 O.

    response = adapter.handle_command("MOVE:0:X:.........")

    parts = response.split(":")
    board_str = parts[0]

    assert board_str.count("X") == 1
    assert board_str.count("O") == 1  # AI should have moved


def test_move_command_game_over_win(adapter):
    """Test a move that results in a win."""
    # Board setup: X X . (row 0)
    # Human X plays at 2.
    # Input board: XX.......
    # Command: MOVE:2:X:XX.......

    # Note: Adapter recreates game.
    # XX....... -> X count=2, O count=0. Next is O?
    # Wait, in _recreate_game_from_str:
    # "game_instance.current_player = 'O' if x_count > o_count else 'X'"
    # If input is XX....... (X=2, O=0), current is O.
    # But the COMMAND says 'MOVE:2:X'.
    # The adapter forces current_player to human_symbol (line 76).
    # So valid.

    response = adapter.handle_command("MOVE:2:X:XX.......")

    # Response should be a tuple strings: (Ongoing-update, Result-notification)
    assert isinstance(response, tuple)
    ongoing, result = response

    # 1. Ongoing update: "XXX......:ONGOING:"
    assert ongoing.startswith("XXX......:ONGOING")

    # 2. Result: "RESULT:WIN:0,1,2"
    assert result == "RESULT:WIN:0,1,2"


def test_move_command_invalid_index(adapter):
    """Test invalid move index handling."""
    response = adapter.handle_command("MOVE:99:X:.........")
    # Should catch exception and return default safe state
    assert response == ".........:ONGOING:"


def test_move_command_invalid_format(adapter):
    response = adapter.handle_command("MOVE:INVALID:X:...")
    assert response == ".........:ONGOING:"


def test_reset(adapter):
    response = adapter.handle_command("RESET")
    assert response == ".........:ONGOING:"


def test_unknown_command(adapter):
    response = adapter.handle_command("UNKNOWN:FOO")
    # Returns default safe state
    assert response == ".........:ONGOING:"


def test_recreate_game_from_str(adapter):
    # Test reconstruction of X.O......
    # X at 0, O at 2.
    board_str = "X.O......"
    game = adapter._recreate_game_from_str(board_str, "X")

    assert game.board[0][0] == "X"
    assert game.board[0][2] == "O"
    assert game.board[1][1] == " "

    # x=1, o=1 -> next is X
    assert game.current_player == "X"


def test_move_on_finished_game(adapter):
    """Test receiving a move for a board that is already won/full."""
    # XXX...... is already won by X.
    response = adapter.handle_command("MOVE:4:O:XXX......")

    # Should detect game over and return current state
    # Likely returns "XXX......:WIN:0,1,2" (single string, not tuple, because it just returned info)
    # The code says:
    # if game_instance.game_over: ... return self._format_response(game_instance)

    assert "XXX......" in response
    assert "LOSE" in response


def test_move_command_occupied_cell(adapter):
    """Test moving to an occupied cell (ValueError)."""
    # X........
    response = adapter.handle_command("MOVE:0:O:X........")
    # Should log warning and return current state
    assert "X........" in response
    assert "ONGOING" in response


def test_invalid_command_exception(adapter):
    """Test generic exception handling."""
    with patch.object(adapter, "_start_game", side_effect=Exception("Generic Error")):
        response = adapter.handle_command("START:X")
        assert response == ".........:ONGOING:"


def test_draw_game(adapter):
    """Test a game ending in a draw."""
    # Board:
    # O X O
    # O X X
    # X O .
    # Only 8 is empty.
    # Player X moves to 8.
    # Result:
    # O X O
    # O X X
    # X O X
    # No winner, full board -> Draw.

    board_state = "OXOOXXXO."
    cmd = f"MOVE:8:X:{board_state}"

    response = adapter.handle_command(cmd)

    assert isinstance(response, tuple)
    ongoing, result = response

    # Should be draw
    assert "DRAW" in result
