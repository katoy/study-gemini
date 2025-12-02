import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from server.server import app, get_game_manager  # get_game_managerをインポート
from server.game_manager import GameManager  # GameManagerクラスをインポート


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
    expected_agents = [
        "Human",
        "ランダム",
        "Minimax",
        "Perfect",
        "QLearning",
        "Database",
    ]
    for agent in expected_agents:
        assert agent in agents


def test_get_agents_endpoint_calls_game_manager(test_client):
    """Test /agents endpoint calls game_manager.get_available_agents()"""
    mock_game_manager = MagicMock(spec=GameManager)
    mock_game_manager.get_available_agents.return_value = ["Human", "TestAgent"]

    # 依存性注入をオーバーライド
    app.dependency_overrides[get_game_manager] = lambda: mock_game_manager

    response = test_client.get("/agents")

    assert response.status_code == 200
    mock_game_manager.get_available_agents.assert_called_once()
    assert response.json()["agents"] == ["Human", "TestAgent"]

    # オーバーライドをクリア
    app.dependency_overrides = {}
