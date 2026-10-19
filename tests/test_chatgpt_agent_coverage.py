"""agents/chatgpt_agent.py の未カバー分岐を補うテスト。"""

import json
import os
from typing import Iterator
from unittest.mock import MagicMock, mock_open, patch

import pytest

from agents.chatgpt_agent import ChatGPTAgent

# 手作りの重要局面の数
HANDCRAFTED_COUNT = 3


@pytest.fixture
def mock_openai_client() -> Iterator[MagicMock]:
    """openai.OpenAI をモックし、実通信を防ぐ。"""
    with patch("openai.OpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def chatgpt_agent(mock_openai_client: MagicMock) -> Iterator[ChatGPTAgent]:
    """ダミーの API キーで ChatGPTAgent を生成する。"""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        yield ChatGPTAgent(player="X")


def _set_response(client: MagicMock, content: str) -> None:
    """モッククライアントの応答内容を設定する。"""
    client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=content))]
    )


def test_load_few_shot_examples(mock_openai_client: MagicMock) -> None:
    """有効手の数が例数以下なら全件を使う分岐を確認する。"""
    data = {"X........": 4, "XO.......": 4, "XOXOXOXOX": -1}
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        agent = ChatGPTAgent(player="O", num_few_shot_examples=5)
    # 有効手 2 件 + 手作り局面
    assert len(agent.few_shot_examples) == 2 + HANDCRAFTED_COUNT
    first = agent.few_shot_examples[0]
    assert first["board_state"] == "X..\n...\n..."
    assert first["player_to_move"] == "O"
    assert first["optimal_move"] == "1,1"


@pytest.mark.parametrize(
    "side_effect",
    [
        FileNotFoundError(),
        json.JSONDecodeError("bad", "doc", 0),
        RuntimeError("boom"),
    ],
)
def test_load_few_shot_examples_errors(
    mock_openai_client: MagicMock, side_effect: Exception
) -> None:
    """ファイル読み込みで例外が起きても手作り局面のみで続行することを確認する。"""
    with patch("builtins.open", side_effect=side_effect):
        agent = ChatGPTAgent(player="X")
    assert len(agent.few_shot_examples) == HANDCRAFTED_COUNT


def test_get_move_without_move_tags(
    chatgpt_agent: ChatGPTAgent, mock_openai_client: MagicMock
) -> None:
    """<move> タグが無い応答ではランダムな有効手にフォールバックする。"""
    _set_response(mock_openai_client, "0,0")
    board = [["X", "O", "X"], ["O", "X", "O"], ["O", "X", ""]]
    assert chatgpt_agent.get_move(board) == (2, 2)


def test_get_move_unparseable_move(
    chatgpt_agent: ChatGPTAgent, mock_openai_client: MagicMock
) -> None:
    """数値に変換できない手ではランダムな有効手にフォールバックする。"""
    _set_response(mock_openai_client, "<move>a,b</move>")
    board = [["X", "O", "X"], ["O", " ", "O"], ["O", "X", "O"]]
    assert chatgpt_agent.get_move(board) == (1, 1)


def test_find_random_valid_move(chatgpt_agent: ChatGPTAgent) -> None:
    """空きマスが無い盤面では None を返す。"""
    board = [["X", "O", "X"], ["O", "X", "O"], ["O", "X", "O"]]
    assert chatgpt_agent._find_random_valid_move(board) is None
