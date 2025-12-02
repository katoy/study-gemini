import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from game_logic import TicTacToe
from server.game_manager import GameManager
from agents.random_agent import RandomAgent
from agents.perfect_agent import PerfectAgent
from agents.minimax_agent import MinimaxAgent
import os


# Use a single GameManager instance for tests to avoid re-discovering agents
@pytest.fixture(scope="function")
def gm_instance():
    return GameManager()


# --- GameManager tests ---


def test_game_manager_initialization(gm_instance):
    """Test GameManager initialization and agent discovery"""
    assert "ランダム" in gm_instance.AGENT_CLASSES
    assert "Human" in gm_instance.AGENT_CLASSES
    assert "Minimax" in gm_instance.AGENT_CLASSES


def test_start_new_game(gm_instance):
    """Test starting a new game"""
    game = gm_instance.start_new_game("Human", "ランダム", "X")
    assert isinstance(game, TicTacToe)
    assert gm_instance.game is not None


def test_get_current_game_state_not_started():
    """Test getting game state before game starts"""
    gm = GameManager()  # Fresh instance without a game
    with pytest.raises(HTTPException) as excinfo:
        gm.get_current_game_state()
    assert excinfo.value.status_code == 404


def test_get_current_game_state_success(gm_instance):
    """Test getting game state after game starts"""
    gm_instance.start_new_game("Human", "ランダム", "X")
    state = gm_instance.get_current_game_state()
    assert "board" in state
    assert "current_player" in state


def test_make_player_move_not_started():
    """Test making a move before game starts"""
    gm = GameManager()  # Fresh instance without a game
    with pytest.raises(HTTPException) as excinfo:
        gm.make_player_move(0, 0)
    assert excinfo.value.status_code == 404


def test_make_player_move_invalid(gm_instance):
    """Test making an invalid move"""
    gm_instance.start_new_game("Human", "Human", "X")
    gm_instance.make_player_move(0, 0)  # Valid move
    with pytest.raises(HTTPException) as excinfo:
        gm_instance.make_player_move(0, 0)  # Invalid move (already taken)
    assert excinfo.value.status_code == 400


# --- New tests for 100% coverage ---


def test_create_agent_human(gm_instance):
    """Test creating a Human agent (should return None)."""
    agent = gm_instance._create_agent("Human", "X")
    assert agent is None


def test_create_agent_minimax(gm_instance):
    """Test creating a Minimax agent."""
    agent = gm_instance._create_agent("Minimax", "X")
    assert isinstance(agent, MinimaxAgent)


def test_create_agent_regular(gm_instance):
    """Test creating a regular agent like Random."""
    agent = gm_instance._create_agent("ランダム", "O")
    assert isinstance(agent, RandomAgent)


def test_create_agent_perfect(gm_instance):
    """Test creating a Perfect agent with a file path."""
    agent = gm_instance._create_agent("Perfect", "X")
    assert isinstance(agent, PerfectAgent)


def test_create_agent_qlearning_file_not_found(gm_instance):
    """Test QLearning agent creation fails if q_table.json is not found"""
    original_q_learning_class = gm_instance.AGENT_CLASSES.get("QLearning")
    if not original_q_learning_class:
        pytest.skip("QLearningAgent not found")

    q_learning_class_mock = MagicMock(side_effect=FileNotFoundError)

    # Directly manipulate the dictionary for this test
    gm_instance.AGENT_CLASSES["QLearning"] = q_learning_class_mock

    with pytest.raises(HTTPException) as excinfo:
        gm_instance._create_agent("QLearning", "X")

    assert excinfo.value.status_code == 500
    assert "Q-learning table not found" in excinfo.value.detail

    # Restore the original class to not affect other tests
    gm_instance.AGENT_CLASSES["QLearning"] = original_q_learning_class


def test_make_player_move_on_agent_turn_raises_exception(gm_instance):
    """Test that make_player_move raises HTTPException on agent's turn if the move is invalid."""
    # Start a game where an agent moves first
    gm_instance.start_new_game("Minimax", "Human", "O")

    # It is now Human's turn (O), but we force it to be agent's turn (X)
    gm_instance.game.current_player = "X"

    with pytest.raises(HTTPException) as excinfo:
        # Minimax (X) has likely moved to (0,0). Attempting the same move will be invalid.
        gm_instance.make_player_move(0, 0)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Invalid move"


@patch("agent_discovery.os.path.exists", return_value=False)
def test_discover_agents_no_directory(mock_exists):
    """Test that _discover_agents handles missing agents directory gracefully."""
    # GameManagerの__init__内でget_agent_details()が呼ばれる
    # get_agent_details()内のos.path.existsがモックされる
    gm = GameManager()
    # Humanエージェントは常に存在するため、AGENT_CLASSESにはHumanのみが含まれる
    assert "Human" in gm.AGENT_CLASSES
    assert len(gm.AGENT_CLASSES) == 1
    assert gm.agent_display_names == ["Human"]


def test_make_agent_move_if_needed_no_game(gm_instance):
    """Test _make_agent_move_if_needed when no game is active."""
    # gm_instance.game is None by default for a fresh GameManager instance
    assert gm_instance.game is None
    gm_instance._make_agent_move_if_needed()  # Should simply return, no error.
    # Assert that no exceptions were raised and no game methods were called
    assert gm_instance.game is None  # Still None
