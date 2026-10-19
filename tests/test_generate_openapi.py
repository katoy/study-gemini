"""generate_openapi スクリプトのテスト。"""

import json
import runpy
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "generate_openapi.py"


def test_generate_openapi(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """カレントディレクトリを tmp_path に移して実行し、OpenAPI スキーマが出力されることを確認する。"""
    # スクリプトが sys.path を書き換えるので、テスト後に元へ戻す
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.chdir(tmp_path)

    runpy.run_path(str(SCRIPT_PATH))

    output = tmp_path / "server" / "apidoc" / "openapi.json"
    assert output.exists()
    schema = json.loads(output.read_text(encoding="utf-8"))
    assert "openapi" in schema
    assert "paths" in schema
    assert "generated successfully" in capsys.readouterr().out
