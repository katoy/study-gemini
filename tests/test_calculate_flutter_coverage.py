"""calculate_flutter_coverage モジュールのテスト。"""

from pathlib import Path

import pytest

from calculate_flutter_coverage import parse_lcov


def test_parse_lcov(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """lcov ファイルを解析してファイル別と合計のカバレッジを出力することを確認する。"""
    lcov = tmp_path / "lcov.info"
    lcov.write_text(
        "\n".join(
            [
                "SF:/proj/lib/main.dart",
                "DA:1,1",
                "DA:2,0",
                "DA:3",  # 要素数が 2 未満の行は無視される
                "end_of_record",
                "SF:/proj/lib/empty.dart",
                "end_of_record",
            ]
        )
        + "\n"
    )
    parse_lcov(str(lcov))
    out = capsys.readouterr().out
    assert "main.dart" in out
    assert "50.0%" in out
    assert "empty.dart" in out
    assert "0.0%" in out
    assert "TOTAL" in out


def test_parse_lcov_no_current_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """SF 行がない場合は記録されず合計 0 % になることを確認する。"""
    lcov = tmp_path / "lcov.info"
    lcov.write_text("end_of_record\nOTHER:line\n")
    parse_lcov(str(lcov))
    out = capsys.readouterr().out
    assert "TOTAL" in out
    assert "0.0%" in out


def test_parse_lcov_missing_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """ファイルが存在しない場合はエラーメッセージを出して None を返すことを確認する。"""
    missing = tmp_path / "missing.info"
    assert parse_lcov(str(missing)) is None
    assert "not found" in capsys.readouterr().out
