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


def test_create_agent_with_alias(gm_instance):
    """
    Test that GameManager can create an agent using its alias (e.g., "Random").
    """
    # "Random" should be mapped to "ランダム" and create a RandomAgent
    agent = gm_instance._create_agent("Random", "O")

    assert agent is not None
    assert agent.__class__.__name__ == "RandomAgent"


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


def test_execute_move_invalid_raises_value_error(gm_instance):
    """Test that execute_move raises ValueError for an invalid move."""
    game = gm_instance.create_game_instance("Human", "Human", "X")
    game = gm_instance.execute_move(game, 0, 0)  # Valid move
    with pytest.raises(ValueError, match="Invalid move"):
        gm_instance.execute_move(game, 0, 0)  # Invalid move


def test_run_ai_move_handles_agent_exception(gm_instance):
    """Test that run_ai_move handles exceptions from agent.get_move."""
    mock_agent = MagicMock()
    # Test with both KeyError and IndexError
    for error in [KeyError, IndexError]:
        mock_agent.get_move.side_effect = error
        game = TicTacToe(agent_x=mock_agent, agent_o=None, human_player="O")
        game.current_player = "X"

        # Patch check_winner to see if it's called
        with patch.object(game, "check_winner", wraps=game.check_winner) as mock_check_winner:
            returned_game = gm_instance.run_ai_move(game)
            assert returned_game is game
            mock_check_winner.assert_called_once()


def test_run_ai_move_no_move_returned(gm_instance):
    """Test run_ai_move when the agent returns no move."""
    mock_agent = MagicMock()
    mock_agent.get_move.return_value = None
    game = TicTacToe(agent_x=mock_agent, agent_o=None, human_player="O")
    game.current_player = "X"

    with patch.object(game, "check_winner", wraps=game.check_winner) as mock_check_winner:
        returned_game = gm_instance.run_ai_move(game)
        assert returned_game is game
        mock_check_winner.assert_called_once()


def test_make_player_move_on_ai_turn_valid_move(gm_instance):
    """Test making a valid player move even when it is the AI's turn."""
    # O is human, X is agent. Agent X moves first.
    game = gm_instance.start_new_game("Minimax", "Human", "O")

    # Pre-condition: It should be O's (human) turn. Let's force it to be X's turn.
    # The first move by Minimax is (0, 0).
    assert game.board[0][0] == "X"
    game.current_player = "X"

    # Human 'O' makes a valid move at (1, 1), even though it's X's turn.
    # The server logic allows this. The move is made by the current_player, which is 'X'.
    moved_game = gm_instance.make_player_move(1, 1)

    # The move should be accepted. The board at (1,1) is now 'X'.
    assert moved_game.board[1][1] == "X"
    assert gm_instance.game is not None
