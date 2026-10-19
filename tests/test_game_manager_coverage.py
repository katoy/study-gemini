"""server/game_manager.py の未カバー分岐を補うテスト。"""

import pytest

from server.game_manager import GameManager


@pytest.fixture
def gm_instance():
    """GameManager のインスタンスを提供するフィクスチャ。"""
    return GameManager()


def test_check_winner(gm_instance):
    """_check_winner は勝者と勝利ラインのタプルを返す。"""
    board = [["X", "X", "X"], ["O", "O", " "], [" ", " ", " "]]
    winner, winner_line = gm_instance._check_winner(board)
    assert winner == "X"
    assert winner_line == ((0, 0), (0, 1), (0, 2))


def test_check_winner_no_winner(gm_instance):
    """勝者がいない場合は (None, None) を返す。"""
    board = [[" "] * 3 for _ in range(3)]
    assert gm_instance._check_winner(board) == (None, None)


def test_run_ai_move(gm_instance):
    """人間の手番（エージェントなし）の場合はゲームをそのまま返す。"""
    game = gm_instance.create_game_instance("Human", "Human")
    result = gm_instance.run_ai_move(game)
    assert result is game
    assert result.board == [[" "] * 3 for _ in range(3)]


def test_run_ai_move_game_over(gm_instance):
    """ゲーム終了済みの場合はゲームをそのまま返す。"""
    game = gm_instance.create_game_instance("ランダム", "ランダム")
    game.game_over = True
    result = gm_instance.run_ai_move(game)
    assert result is game
    assert result.board == [[" "] * 3 for _ in range(3)]
