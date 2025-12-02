import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from server.server import app, get_game_manager
from server.game_manager import GameManager, PLAYER_X, PLAYER_O


@pytest.fixture(scope="function")
def client_with_mocked_game_manager():
    """Test client with a mocked GameManager instance shared across requests within a test function."""
    mock_game_manager_instance = GameManager()

    # 依存性注入をオーバーライド
    app.dependency_overrides[get_game_manager] = lambda: mock_game_manager_instance

    with TestClient(app) as client:
        yield client

    # テスト終了後にオーバーライドをクリア
    app.dependency_overrides = {}


# --- /game/start endpoint tests ---


def test_start_game_endpoint(client_with_mocked_game_manager):
    """Test the /game/start endpoint."""
    response = client_with_mocked_game_manager.post(
        "/game/start",
        json={
            "player_x_type": "Human",
            "player_o_type": "ランダム",
            "human_player_symbol": "X",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "board" in data
    assert data["current_player"] == "X"


def test_start_game_endpoint_no_human_symbol(client_with_mocked_game_manager):
    """Test /game/start with human_player_symbol omitted."""
    response = client_with_mocked_game_manager.post(
        "/game/start",
        json={
            "player_x_type": "Human",
            "player_o_type": "ランダム",
            # human_player_symbol is omitted
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "board" in data


# --- /game/status endpoint tests ---


def test_get_game_status_endpoint(client_with_mocked_game_manager):
    """Test the /game/status endpoint."""
    # Start a game first so get_current_game_state returns a valid state
    client_with_mocked_game_manager.post(
        "/game/start",
        json={
            "player_x_type": "Human",
            "player_o_type": "ランダム",
            "human_player_symbol": "X",
        },
    )

    response = client_with_mocked_game_manager.get("/game/status")
    assert response.status_code == 200
    data = response.json()
    assert "board" in data


# --- /game/move endpoint tests ---


def test_make_move_endpoint(client_with_mocked_game_manager):
    """Test the /game/move endpoint and agent's subsequent move."""
    # Start a game where it's human's turn (X) vs agent (O)
    client_with_mocked_game_manager.post(
        "/game/start",
        json={
            "player_x_type": "Human",
            "player_o_type": "ランダム",
            "human_player_symbol": "X",
        },
    )

    # Get the mocked GameManager instance from the overrides
    mock_game_manager = app.dependency_overrides[get_game_manager]()

    # Mock the agent's move to be predictable
    with patch.object(mock_game_manager.game.agent_o, "get_move", return_value=(1, 1)):
        # Human makes a move
        response = client_with_mocked_game_manager.post(
            "/game/move", json={"row": 0, "col": 0}
        )
        assert response.status_code == 200
        data = response.json()

        # After human moves (X at 0,0), agent should have moved (O at 1,1)
        # and the current player should be back to X.
        assert data["board"][0][0] == "X"
        assert data["board"][1][1] == "O"
        assert data["current_player"] == "X"
