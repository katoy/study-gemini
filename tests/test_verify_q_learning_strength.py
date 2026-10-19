"""verify_q_learning_strength モジュールのテスト。"""

import sys
from collections.abc import Iterator
from typing import Optional
from unittest.mock import MagicMock, call

import pytest

import verify_q_learning_strength
from verify_q_learning_strength import evaluate, main, parse_args

Move = Optional[tuple[int, int]]

# X が上段を揃えて勝つ手順
X_WINS: list[Move] = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]
# O が中段を揃えて勝つ手順
O_WINS: list[Move] = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2), (1, 2)]
# 勝者なしで盤面が埋まる手順
DRAW: list[Move] = [
    (0, 0),
    (0, 1),
    (0, 2),
    (1, 1),
    (1, 0),
    (1, 2),
    (2, 1),
    (2, 0),
    (2, 2),
]
# X の手番で手が返らないケース
X_NO_MOVE: list[Move] = [None]
# O の手番で手が返らないケース
O_NO_MOVE: list[Move] = [(0, 0), None]


class ScriptedAgent:
    """共有の手順リストから順番に手を返すテスト用エージェント。"""

    moves: Iterator[Move] = iter([])

    def __init__(self, player: str, is_training: bool = False) -> None:
        """QLearningAgent / 対戦相手クラスと同じ形の引数を受け取る。"""
        self.player = player
        self.is_training = is_training

    def get_move(self, board: list[list[str]]) -> Move:
        """共有手順から次の手を返す。"""
        return next(ScriptedAgent.moves)


def test_parse_args(monkeypatch: pytest.MonkeyPatch) -> None:
    """--num_games の指定と既定値を確認する。"""
    monkeypatch.setattr(sys, "argv", ["verify.py", "--num_games", "7"])
    assert parse_args().num_games == 7
    monkeypatch.setattr(sys, "argv", ["verify.py"])
    assert parse_args().num_games == 10


@pytest.mark.parametrize(
    ("q_player", "expected"),
    [
        # X 勝ち・O 勝ち・引き分け・X 手なし・O 手なし の順
        ("X", ("勝ち: 2 (40.0%)", "負け: 2 (40.0%)", "引き分け: 1 (20.0%)")),
        ("O", ("勝ち: 2 (40.0%)", "負け: 2 (40.0%)", "引き分け: 1 (20.0%)")),
    ],
)
def test_evaluate(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    q_player: str,
    expected: tuple[str, str, str],
) -> None:
    """勝ち・負け・引き分け・手なしの全分岐を集計できることを確認する。"""
    ScriptedAgent.moves = iter(X_WINS + O_WINS + DRAW + X_NO_MOVE + O_NO_MOVE)
    monkeypatch.setattr(verify_q_learning_strength, "QLearningAgent", ScriptedAgent)

    evaluate(q_player, ScriptedAgent, "Dummy", 5)

    out = capsys.readouterr().out
    opponent = "O" if q_player == "X" else "X"
    assert f"Q-Agent({q_player}) vs Dummy({opponent})" in out
    for text in expected:
        assert text in out


def test_main(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """main が先手・後手それぞれ 3 種類の相手で evaluate を呼ぶことを確認する。"""
    mock_eval = MagicMock()
    monkeypatch.setattr(verify_q_learning_strength, "evaluate", mock_eval)
    monkeypatch.setattr(sys, "argv", ["verify.py", "--num_games", "2"])

    main()

    m = verify_q_learning_strength
    assert mock_eval.call_args_list == [
        call("X", m.RandomAgent, "RandomAgent", 2),
        call("X", m.MinimaxAgent, "MinimaxAgent", 2),
        call("X", m.PerfectAgent, "PerfectAgent", 2),
        call("O", m.RandomAgent, "RandomAgent", 2),
        call("O", m.MinimaxAgent, "MinimaxAgent", 2),
        call("O", m.PerfectAgent, "PerfectAgent", 2),
    ]
    assert "=== 強さ検証レポート ===" in capsys.readouterr().out
