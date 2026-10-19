"""generate_screenshots モジュールのテスト。"""

from pathlib import Path
from typing import Any

import pytest
from PIL import Image, ImageDraw, ImageFont

import generate_screenshots
from generate_screenshots import (
    BG_COLOR,
    CANVAS_SIZE,
    create_base_image,
    draw_board,
    draw_o,
    draw_x,
    generate_gameplay_screenshot,
    generate_win_screenshot,
)


def test_create_base_image() -> None:
    """盤面サイズの背景画像が生成されることを確認する。"""
    img = create_base_image()
    assert img.size == (CANVAS_SIZE, CANVAS_SIZE)
    assert img.getpixel((0, 0)) == Image.new("RGB", (1, 1), BG_COLOR).getpixel((0, 0))


def test_draw_board() -> None:
    """グリッド線が描画されることを確認する。"""
    img = create_base_image()
    draw_board(ImageDraw.Draw(img))
    assert img.getpixel((100, 50)) == (255, 255, 255)


def test_draw_x() -> None:
    """X 記号が指定セルに赤で描画されることを確認する。"""
    img = create_base_image()
    draw_x(ImageDraw.Draw(img), 0, 0)
    assert img.getpixel((50, 50)) == (255, 0, 0)


def test_draw_o() -> None:
    """O 記号が指定セルに青で描画されることを確認する。"""
    img = create_base_image()
    draw_o(ImageDraw.Draw(img), 1, 1)
    # 円周上 (左端の中央) の点が青になる
    assert img.getpixel((112, 150)) == (0, 0, 255)


def test_generate_gameplay_screenshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """対局中のスクリーンショットが tmp_path に保存されることを確認する。"""
    monkeypatch.setattr(generate_screenshots, "IMAGES_DIR", str(tmp_path))
    generate_gameplay_screenshot()
    output = tmp_path / "gui_screenshot_gameplay.png"
    assert output.exists()
    with Image.open(output) as img:
        assert img.size == (320, 380)
    assert "gui_screenshot_gameplay.png" in capsys.readouterr().out


@pytest.mark.parametrize("font_fails", [False, True])
def test_generate_win_screenshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    font_fails: bool,
) -> None:
    """勝利画面のスクリーンショットがフォント読み込みの成否に関わらず保存されることを確認する。"""
    monkeypatch.setattr(generate_screenshots, "IMAGES_DIR", str(tmp_path))
    original_truetype = ImageFont.truetype

    def fake_truetype(font: Any, *args: Any, **kwargs: Any) -> Any:
        # load_default は内部で BytesIO を渡して truetype を呼ぶので、それは本物に任せる
        if not isinstance(font, str):
            return original_truetype(font, *args, **kwargs)
        if font_fails:
            raise IOError("font not found")
        # 環境依存を避けるため、成功時もデフォルトフォントを返す
        return ImageFont.load_default()

    monkeypatch.setattr(ImageFont, "truetype", fake_truetype)

    generate_win_screenshot()

    output = tmp_path / "gui_screenshot_win.png"
    assert output.exists()
    with Image.open(output) as img:
        assert img.size == (320, 380)
    assert "gui_screenshot_win.png" in capsys.readouterr().out
