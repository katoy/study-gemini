import pytest
from pydantic import ValidationError
from typing import List, Optional, Tuple

from server.schemas import StartGameRequest, BoardState, MoveRequest


def test_start_game_request_valid():
    request = StartGameRequest(
        human_player_symbol="X", player_x_type="Human", player_o_type="Random"
    )
    assert request.human_player_symbol == "X"
    assert request.player_x_type == "Human"
    assert request.player_o_type == "Random"


def test_start_game_request_invalid_symbol():
    with pytest.raises(ValidationError):
        StartGameRequest(
            human_player_symbol="Z", player_x_type="Human", player_o_type="Random"
        )


def test_board_state_valid():
    board = [[" ", " ", " "], [" ", "X", " "], [" ", " ", " "]]
    state = BoardState(
        board=board, current_player="O", winner=None, winner_line=None, game_over=False
    )
    assert state.board == board
    assert state.current_player == "O"
    assert state.winner is None
    assert state.game_over is False


def test_board_state_invalid_board_size():
    with pytest.raises(ValidationError):
        BoardState(
            board=[[" ", " "]],
            current_player="X",
            winner=None,
            winner_line=None,
            game_over=False,
        )


def test_move_request_valid():
    request = MoveRequest(row=0, col=1)
    assert request.row == 0
    assert request.col == 1


def test_move_request_invalid_row():
    with pytest.raises(ValidationError):
        MoveRequest(row=3, col=1)


def test_move_request_invalid_col():
    with pytest.raises(ValidationError):
        MoveRequest(row=0, col=3)


def test_board_state_invalid_row_length():
    """Test BoardState with a row that doesn't have 3 elements."""
    with pytest.raises(
        ValidationError, match="Each row of the board must have 3 elements"
    ):
        BoardState(
            board=[
                [" ", " ", " "],
                [" ", "X"],
                [" ", " ", " "],
            ],  # Second row has only 2 elements
            current_player="O",
            winner=None,
            winner_line=None,
            game_over=False,
        )
