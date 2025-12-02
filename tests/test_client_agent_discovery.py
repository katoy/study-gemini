import pytest
from unittest.mock import MagicMock, patch
import requests

from CUI.tic_tac_toe_client import TicTacToeClient

SERVER_URL = "http://127.0.0.1:8000"


@pytest.fixture
def client():
    return TicTacToeClient(SERVER_URL)


# --- get_available_agents tests ---


@patch("requests.get")
def test_get_available_agents_success(mock_get, client):
    """Test successful retrieval of agents from server"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"agents": ["Human", "Random", "Minimax"]}
    mock_get.return_value.raise_for_status.return_value = None

    agents = client.get_available_agents()

    assert agents == ["Human", "Random", "Minimax"]
    mock_get.assert_called_once_with(f"{SERVER_URL}/agents")


@patch("requests.get")
def test_get_available_agents_caches_result(mock_get, client):
    """Test that get_available_agents caches the result"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"agents": ["Human", "Random"]}
    mock_get.return_value.raise_for_status.return_value = None

    # First call
    agents1 = client.get_available_agents()
    # Second call
    agents2 = client.get_available_agents()

    # Should only call the server once
    assert mock_get.call_count == 1
    assert agents1 == agents2


@patch("requests.get")
@patch("builtins.print")
def test_get_available_agents_connection_error(mock_print, mock_get, client):
    """Test fallback when server connection fails"""
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

    agents = client.get_available_agents()

    # Should return fallback list
    assert "Human" in agents
    assert "Random" in agents

    # Should print warning
    mock_print.assert_called_with(
        "Warning: Could not fetch agent list from server. Using fallback list."
    )


@patch("requests.get")
@patch("builtins.print")
def test_get_available_agents_http_error(mock_print, mock_get, client):
    """Test fallback when server returns HTTP error"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response
    )

    agents = client.get_available_agents()

    # Should return fallback list
    assert "Human" in agents

    # Should print warning
    mock_print.assert_called_with(
        "Warning: Could not fetch agent list from server. Using fallback list."
    )


@patch("requests.get")
def test_get_available_agents_empty_response(mock_get, client):
    """Test handling of empty agents list from server"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {}  # No "agents" key
    mock_get.return_value.raise_for_status.return_value = None

    agents = client.get_available_agents()

    # Should return empty list (from response.get("agents", []))
    assert agents == []


# --- get_agent_type_choice with empty agents list ---


@patch.object(TicTacToeClient, "get_available_agents", return_value=[])
@patch("builtins.print")
def test_get_agent_type_choice_empty_list(mock_print, mock_get_agents, client):
    """Test get_agent_type_choice when agents list is empty"""
    result = client.get_agent_type_choice("X")

    # Should return "Human" as fallback
    assert result == "Human"

    # Should print error message
    mock_print.assert_called_with("Error: No agents available.")
