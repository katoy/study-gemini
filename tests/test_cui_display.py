import pytest
from unittest.mock import patch
from CUI.cui_display import display_board

def test_display_board_empty_board(capsys):
    board_state = {
        "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
        "current_player": "X",
        "winner": None,
        "winner_line": None,
        "game_over": False
    }
    display_board(board_state)
    captured = capsys.readouterr()
    expected_output = """
--- Tic Tac Toe Board ---
| 1 | 2 | 3 |
| 4 | 5 | 6 |
| 7 | 8 | 9 |
-------------------------

Current Player: X
"""
    assert captured.out == expected_output

def test_display_board_in_progress(capsys):
    board_state = {
        "board": [["X", " ", " "], [" ", "O", " "], [" ", " ", " "]],
        "current_player": "X",
        "winner": None,
        "winner_line": None,
        "game_over": False
    }
    display_board(board_state)
    captured = capsys.readouterr()
    expected_output = """
--- Tic Tac Toe Board ---
| X | 2 | 3 |
| 4 | O | 6 |
| 7 | 8 | 9 |
-------------------------

Current Player: X
"""
    assert captured.out == expected_output

def test_display_board_x_wins(capsys):
    board_state = {
        "board": [["X", "X", "X"], ["O", "O", " "], [" ", " ", " "]],
        "current_player": "O",
        "winner": "X",
        "winner_line": ((0,0), (0,1), (0,2)),
        "game_over": True
    }
    display_board(board_state)
    captured = capsys.readouterr()
    expected_output = """
--- Tic Tac Toe Board ---
| X | X | X |
| O | O | 6 |
| 7 | 8 | 9 |
-------------------------

Game Over: Player X wins!
"""
    assert captured.out == expected_output

def test_display_board_draw(capsys):
    board_state = {
        "board": [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]],
        "current_player": "O",
        "winner": "draw",
        "winner_line": None,
        "game_over": True
    }
    display_board(board_state)
    captured = capsys.readouterr()
    expected_output = """
--- Tic Tac Toe Board ---
| X | O | X |
| X | O | O |
| O | X | X |
-------------------------

Game Over: It's a draw!
"""
    assert captured.out == expected_output

def test_display_board_game_over_no_winner_no_draw_should_not_happen(capsys):
    board_state = {
        "board": [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]],
        "current_player": "O",
        "winner": None,
        "winner_line": None,
        "game_over": True
    }
    display_board(board_state)
    captured = capsys.readouterr()
    expected_output = """
--- Tic Tac Toe Board ---
| X | O | X |
| X | O | O |
| O | X | X |
-------------------------

Game Over.
"""
    assert captured.out == expected_output
