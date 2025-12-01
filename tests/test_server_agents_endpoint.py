import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from server.server import app
from server.game_manager import game_manager


@pytest.fixture
def test_client():
    return TestClient(app)


# --- /agents endpoint tests ---

def test_get_agents_endpoint_success(test_client):
    """Test /agents endpoint returns list of agents"""
    response = test_client.get("/agents")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "agents" in data
    assert isinstance(data["agents"], list)
    assert "Human" in data["agents"]


def test_get_agents_endpoint_returns_all_agents(test_client):
    """Test /agents endpoint returns all expected agents"""
    response = test_client.get("/agents")
    
    assert response.status_code == 200
    agents = response.json()["agents"]
    
    # Should contain all expected agents
    expected_agents = ["Human", "Random", "Minimax", "Perfect", "QLearning", "Database"]
    for agent in expected_agents:
        assert agent in agents


@patch.object(game_manager, 'get_available_agents')
def test_get_agents_endpoint_calls_game_manager(mock_get_agents, test_client):
    """Test /agents endpoint calls game_manager.get_available_agents()"""
    mock_get_agents.return_value = ["Human", "TestAgent"]
    
    response = test_client.get("/agents")
    
    assert response.status_code == 200
    mock_get_agents.assert_called_once()
    assert response.json()["agents"] == ["Human", "TestAgent"]
