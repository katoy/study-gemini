import pytest
import os
from unittest.mock import MagicMock, patch
from agents.chatgpt_agent import ChatGPTAgent
from agents.base_agent import BaseAgent


# Mock the OpenAI client for testing purposes
@pytest.fixture
def mock_openai_client():
    with patch("openai.OpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def chatgpt_agent(mock_openai_client):
    os.environ["OPENAI_API_KEY"] = "test_key"  # Set a dummy API key for testing
    agent = ChatGPTAgent(player="X")
    yield agent
    del os.environ["OPENAI_API_KEY"]


def test_chatgpt_agent_initialization(chatgpt_agent):
    assert chatgpt_agent.player == "X"
    assert (
        chatgpt_agent.model == "gpt-5.1"
    )  # Changed to gpt-5.1 based on chatgpt_agent.py
    assert isinstance(chatgpt_agent.client, MagicMock)


def test_get_move_valid_response(chatgpt_agent, mock_openai_client):
    # Mock a valid response from ChatGPT
    mock_openai_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="<move>0,0</move>"))]
    )

    board = [
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
    ]
    move = chatgpt_agent.get_move(board)
    assert move == (0, 0)
    mock_openai_client.chat.completions.create.assert_called_once()


def test_get_move_invalid_response_fallback(chatgpt_agent, mock_openai_client):
    # Mock an invalid response (e.g., trying to move to an occupied cell)
    mock_openai_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="<move>0,0</move>"))]
    )

    board = [
        ["X", "", ""],
        ["", "", ""],
        ["", "", ""],
    ]
    # ChatGPT suggests (0,0) which is occupied. Should fall back to a random valid move.
    move = chatgpt_agent.get_move(board)
    assert move != (0, 0)  # Should not be the invalid move suggested by ChatGPT
    assert 0 <= move[0] < 3
    assert 0 <= move[1] < 3
    assert board[move[0]][move[1]] == ""  # Ensure the fallback move is valid
    mock_openai_client.chat.completions.create.assert_called_once()


def test_get_move_api_error_fallback(chatgpt_agent, mock_openai_client):
    # Mock an API error
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

    board = [
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
    ]
    move = chatgpt_agent.get_move(board)
    # Should fall back to a random valid move
    assert 0 <= move[0] < 3
    assert 0 <= move[1] < 3
    assert board[move[0]][move[1]] == ""  # Ensure the fallback move is valid
    mock_openai_client.chat.completions.create.assert_called_once()
