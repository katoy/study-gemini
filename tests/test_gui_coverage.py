"""gui.py の未カバー分岐を補うテスト。"""

from unittest.mock import MagicMock, patch

import pytest

try:
    import tkinter as tk
except ImportError:  # pragma: no cover
    tk = MagicMock()


@pytest.fixture
def gui_factory():
    """machine_first を指定して TicTacToeGUI を生成するファクトリを提供する。"""
    sys_modules = {"tkinter": MagicMock(), "tkinter.font": MagicMock()}
    with patch.dict("sys.modules", sys_modules):
        from gui import TicTacToeGUI

        with (
            patch("gui.SettingsUI") as mock_settings_ui_class,
            patch("gui.BoardDrawer") as mock_board_drawer_class,
            patch("gui.GameInfoUI"),
            patch("gui.TicTacToe") as mock_tictactoe_class,
            patch("gui.tk") as mock_tk,
        ):

            def _create(machine_first: bool = False):
                instance = TicTacToeGUI(MagicMock(spec=tk.Tk), machine_first)
                instance.mock_settings_ui = mock_settings_ui_class.return_value
                instance.mock_board_drawer = mock_board_drawer_class.return_value
                instance.mock_tictactoe_class = mock_tictactoe_class
                instance.mock_tk = mock_tk
                return instance

            yield _create


def _make_training_game(winner, move=(1, 2)):
    """学習用のモックゲームを生成する。

    Args:
        winner: check_winner が返す値。
        move: エージェントの get_move が返す手。

    Returns:
        MagicMock: 設定済みのモックゲーム。
    """
    game = MagicMock()
    game.current_player = "X"
    game.agent_player = "X"
    game.get_opponent.return_value = "O"
    game.check_winner.return_value = winner
    game.agent.get_move.return_value = move
    game.agent.board_to_string.return_value = "state"
    return game


def test_init(gui_factory):
    """machine_first=True の場合はプレイヤー選択が False に設定される。"""
    gui = gui_factory(machine_first=True)
    gui.mock_settings_ui.player_var.set.assert_called_with(False)


def test_train_q_learning_agent(gui_factory):
    """学習ループが 1 回以上回り、終了後にクリックイベントがバインドされる。"""
    gui = gui_factory()
    game = gui.mock_tictactoe_class.return_value
    game.game_over = False

    def _finish_game():
        game.game_over = True

    with (
        patch.object(
            gui, "agent_turn_for_training", side_effect=_finish_game
        ) as mock_turn,
        patch.object(gui, "update_q_table_after_game") as mock_update,
        patch("builtins.print"),
    ):
        gui.train_q_learning_agent()

    mock_turn.assert_called_once()
    assert mock_update.call_count == 10000
    gui.canvas.bind.assert_called_with("<Button-1>", gui.on_canvas_click)
    gui.control_buttons_frame.pack.assert_called_with(pady=10)


@pytest.mark.parametrize(
    "winner, expected_reward",
    [("X", 100), ("O", -100), ("draw", 0), (None, 0)],
)
def test_agent_turn_for_training(gui_factory, winner, expected_reward):
    """勝敗に応じた報酬で Q テーブルが更新される。"""
    gui = gui_factory()
    gui.game = _make_training_game(winner)

    gui.agent_turn_for_training()

    gui.game.make_move.assert_called_once_with(1, 2)
    gui.game.switch_player.assert_called_once()
    gui.game.agent.update_q_table.assert_called_once_with(
        "state", 5, expected_reward, "state"
    )


def test_agent_turn_for_training_no_move(gui_factory):
    """エージェントが手を返さない場合は何もしない。"""
    gui = gui_factory()
    gui.game = _make_training_game(None, move=None)

    gui.agent_turn_for_training()

    gui.game.make_move.assert_not_called()
    gui.game.agent.update_q_table.assert_not_called()


def test_agent_turn_for_training_not_agent_turn(gui_factory):
    """エージェントの手番でなければ何もしない。"""
    gui = gui_factory()
    gui.game = _make_training_game(None)
    gui.game.current_player = "O"

    gui.agent_turn_for_training()

    gui.game.agent.get_move.assert_not_called()


@pytest.mark.parametrize(
    "winner, expected_reward",
    [("X", 100), ("O", -100), ("draw", 0), (None, 0)],
)
def test_update_q_table_after_game(gui_factory, winner, expected_reward):
    """ゲーム終了後に勝敗に応じた報酬で Q テーブルが更新される。"""
    gui = gui_factory()
    gui.game = _make_training_game(winner, move=(2, 0))
    gui.game.agent.get_available_moves.return_value = [(2, 0)]

    gui.update_q_table_after_game()

    gui.game.agent.update_q_table.assert_called_once_with(
        "state", 6, expected_reward, "state"
    )


def test_update_q_table_after_game_no_available_moves(gui_factory):
    """空きマスがない場合は Q テーブルを更新しない。"""
    gui = gui_factory()
    gui.game = _make_training_game("draw")
    gui.game.agent.get_available_moves.return_value = []

    gui.update_q_table_after_game()

    gui.game.agent.update_q_table.assert_not_called()


def test_update_q_table_after_game_move_none(gui_factory):
    """エージェントが手を返さない場合は Q テーブルを更新しない。"""
    gui = gui_factory()
    gui.game = _make_training_game("draw", move=None)
    gui.game.agent.get_available_moves.return_value = [(0, 0)]

    gui.update_q_table_after_game()

    gui.game.agent.update_q_table.assert_not_called()


def test_agent_turn(gui_factory):
    """エージェントの手で勝敗が決した場合は game_over が呼ばれる。"""
    gui = gui_factory()
    game = MagicMock()
    game.current_player = "O"
    game.agent_player = "O"
    game.get_current_agent.return_value.get_move.return_value = (0, 0)
    game.make_move.return_value = True
    game.check_winner.return_value = "O"
    gui.game = game

    with patch.object(gui, "game_over") as mock_game_over:
        gui.agent_turn()

    mock_game_over.assert_called_once_with("O")
    game.switch_player.assert_not_called()
