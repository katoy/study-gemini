"""generate_cui_screenshot モジュールのテスト。"""

from pathlib import Path
from typing import Any

import pytest
from PIL import Image, ImageFont

import generate_cui_screenshot
from generate_cui_screenshot import create_cui_image


@pytest.mark.parametrize("fail_count", [0, 1, 2])
def test_create_cui_image(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fail_count: int,
) -> None:
    """フォント読み込みの成功・失敗の各分岐で画像が tmp_path に保存されることを確認する。

    fail_count は truetype が IOError を送出する回数 (2 回でデフォルトフォントへフォールバック)。
    """
    monkeypatch.setattr(generate_cui_screenshot, "IMAGES_DIR", str(tmp_path))
    calls: list[str] = []
    original_truetype = ImageFont.truetype

    def fake_truetype(font: Any, *args: Any, **kwargs: Any) -> Any:
        # load_default は内部で BytesIO を渡して truetype を呼ぶので、それは本物に任せる
        if not isinstance(font, str):
            return original_truetype(font, *args, **kwargs)
        calls.append(font)
        if len(calls) <= fail_count:
            raise IOError("font not found")
        # 環境依存を避けるため、成功時もデフォルトフォントを返す
        return ImageFont.load_default()

    monkeypatch.setattr(ImageFont, "truetype", fake_truetype)

    create_cui_image()

    output = tmp_path / "cui_screenshot.png"
    assert output.exists()
    with Image.open(output) as img:
        assert img.size[0] == 400
    assert len(calls) == min(fail_count + 1, 2)
    assert "Generated" in capsys.readouterr().out
