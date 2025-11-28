import pytest
from unittest.mock import MagicMock
from game_logic import TicTacToe

@pytest.fixture
def game():
    """TicTacToe インスタンスを提供するフィクスチャ"""
    return TicTacToe(human_player="X")

@pytest.fixture
def mock_game():
    """エージェントをモックした TicTacToe インスタンスを提供するフィクスチャ"""
    mock_agent_x = MagicMock()
    mock_agent_o = MagicMock()
    return TicTacToe(agent_x=mock_agent_x, agent_o=mock_agent_o, human_player="X")

def test_make_move_when_game_over(game):
    """ゲーム終了後に移動できないことを確認"""
    game.game_over = True
    result = game.make_move(0, 0)
    assert not result
    assert game.board[0][0] == " "

def test_check_winner_diagonal_reverse(game):
    """右上から左下への対角線の勝利を確認"""
    game.board = [
        [" ", " ", "X"],
        [" ", "X", " "],
        ["X", " ", " "]
    ]
    winner = game.check_winner()
    assert winner == "X"
    assert game.game_over
    assert game.winner_line == ((0, 2), (1, 1), (2, 0))

def test_make_move_on_occupied_cell(game):
    """既に埋まっているセルへの移動が失敗することを確認"""
    game.make_move(0, 0)
    result = game.make_move(0, 0)
    assert not result
    assert game.board[0][0] == "X"

def test_check_winner_no_winner_yet(game):
    """勝者がまだいない状態でNoneが返されることを確認"""
    game.board = [
        ["X", "O", " "],
        [" ", "X", " "],
        [" ", " ", " "]
    ]
    winner = game.check_winner()
    assert winner is None
    assert not game.game_over

def test_get_current_agent_x_player(mock_game):
    """現在のプレイヤーがXの場合にagent_xが返されることを確認"""
    mock_game.current_player = "X"
    current_agent = mock_game.get_current_agent()
    assert current_agent is mock_game.agent_x

def test_get_current_agent_o_player(mock_game):
    """現在のプレイヤーがOの場合にagent_oが返されることを確認"""
    mock_game.current_player = "O"
    current_agent = mock_game.get_current_agent()
    assert current_agent is mock_game.agent_o


