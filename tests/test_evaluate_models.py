"""evaluate_models モジュールのテスト。"""

import sys
from collections.abc import Iterator
from typing import Optional
from unittest.mock import MagicMock

import pytest

import evaluate_models

Move = Optional[tuple[int, int]]

# X が上段を揃えて勝つ手順
X_WINS: list[Move] = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]
# O が中段を揃えて勝つ手順
O_WINS: list[Move] = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2), (1, 2)]
# 先手がいきなり手を返さない (None) ケース
NO_MOVE: list[Move] = [None]


class ScriptedAgent:
    """共有の手順リストから順番に手を返すテスト用エージェント。"""

    moves: Iterator[Move] = iter([])

    def __init__(self, player: str, q_table_file: str, is_training: bool) -> None:
        """QLearningAgent と同じ引数を受け取る。"""
        self.player = player
        self.q_table_file = q_table_file
        self.is_training = is_training

    def get_move(self, board: list[list[str]]) -> Move:
        """共有手順から次の手を返す。"""
        return next(ScriptedAgent.moves)


def test_evaluate_models(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """X 勝ち・O 勝ち・手なし (引き分け扱い) を両方の手番で集計できることを確認する。"""
    one_round = X_WINS + O_WINS + NO_MOVE
    ScriptedAgent.moves = iter(one_round * 2)
    monkeypatch.setattr(evaluate_models, "QLearningAgent", ScriptedAgent)

    evaluate_models.evaluate_models("m1.json", "m2.json", 3)

    out = capsys.readouterr().out
    assert "総ゲーム数: 3回/対戦" in out
    # 各対戦で 1 勝 1 敗 1 分け
    assert "Agent1 (m1.json) の勝利: 1 (33.3%)" in out
    assert "Agent2 (m2.json) の勝利: 1 (33.3%)" in out
    assert "引き分け: 1 (33.3%)" in out
    assert "Agent1 (m1.json) の総勝利数: 2 (33.3%)" in out
    assert "Agent2 (m2.json) の総勝利数: 2 (33.3%)" in out
    assert "総引き分け数: 2 (33.3%)" in out


def test_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """コマンドライン引数が evaluate_models に渡されることを確認する。"""
    mock_eval = MagicMock()
    monkeypatch.setattr(evaluate_models, "evaluate_models", mock_eval)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "evaluate_models.py",
            "--model1",
            "a.json",
            "--model2",
            "b.json",
            "--num_games",
            "5",
        ],
    )
    evaluate_models.main()
    mock_eval.assert_called_once_with("a.json", "b.json", 5)


def test_main_default_num_games(monkeypatch: pytest.MonkeyPatch) -> None:
    """--num_games 省略時は 100 が使われることを確認する。"""
    mock_eval = MagicMock()
    monkeypatch.setattr(evaluate_models, "evaluate_models", mock_eval)
    monkeypatch.setattr(
        sys, "argv", ["evaluate_models.py", "--model1", "a.json", "--model2", "b.json"]
    )
    evaluate_models.main()
    mock_eval.assert_called_once_with("a.json", "b.json", 100)


def test_main_missing_required(monkeypatch: pytest.MonkeyPatch) -> None:
    """必須引数がない場合は SystemExit になることを確認する。"""
    monkeypatch.setattr(sys, "argv", ["evaluate_models.py"])
    with pytest.raises(SystemExit):
        evaluate_models.main()
