import pytest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from server.game_manager import GameManager
from game_logic import TicTacToe # Not mocked in all tests for direct interaction
from server.schemas import StartGameRequest, BoardState, MoveRequest
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.perfect_agent import PerfectAgent
from agents.q_learning_agent import QLearningAgent
from agents.database_agent import DatabaseAgent
from server.game_manager import PLAYER_X, PLAYER_O, PERFECT_MOVES_FILE, Q_TABLE_PATH


@pytest.fixture
def game_manager_instance():
    """Provides a GameManager instance for tests."""
    gm = GameManager()
    # Mock AGENT_CLASSES to control agent creation during tests
    gm.AGENT_CLASSES = {
        "Human": None,
        "ランダム": RandomAgent,
        "Minimax": MinimaxAgent,
        "Database": DatabaseAgent,
        "Perfect": PerfectAgent,
        "QLearning": QLearningAgent,
    }
    return gm

@pytest.fixture
def mock_game():
    """Provides a mocked TicTacToe game instance."""
    mock = MagicMock(spec=TicTacToe)
    mock.board = [[" " for _ in range(3)] for _ in range(3)]
    mock.current_player = PLAYER_X
    mock.game_over = False
    mock.check_winner.return_value = None
    mock.winner_line = None
    return mock

# --- _create_agent tests ---

@pytest.mark.parametrize("agent_type, expected_class", [
    ("Human", None),
    ("ランダム", RandomAgent),
    ("Minimax", MinimaxAgent),
    ("Database", DatabaseAgent),
    ("Perfect", PerfectAgent),
    ("QLearning", QLearningAgent),
])
def test_create_agent_returns_correct_instance(game_manager_instance, agent_type, expected_class):
    player_symbol = PLAYER_X
    agent = game_manager_instance._create_agent(agent_type, player_symbol)

    if expected_class is None:
        assert agent is None
    else:
        assert isinstance(agent, expected_class)
        assert agent.player == player_symbol
        if agent_type == "Perfect":
            assert agent.perfect_moves_file == PERFECT_MOVES_FILE
        elif agent_type == "QLearning":
            # Check if q_table_file was passed correctly.
            # QLearningAgent's __init__ might load/save, so we check the init call args
            # This requires inspecting the mock if QLearningAgent were mocked itself.
            # For now, rely on actual instantiation.
            pass

@patch('agents.q_learning_agent.QLearningAgent')
def test_create_agent_qlearning_file_not_found(mock_q_agent_class, game_manager_instance):
    # Ensure that GameManager uses our mocked QLearningAgent
    game_manager_instance.AGENT_CLASSES["QLearning"] = mock_q_agent_class
    
    mock_q_agent_class.side_effect = FileNotFoundError("Q-table not found")
    player_symbol = PLAYER_X

    with pytest.raises(HTTPException) as exc_info:
        game_manager_instance._create_agent("QLearning", player_symbol)
    assert exc_info.value.status_code == 500
    assert "Q-learning table not found" in exc_info.value.detail


# --- _make_agent_move_if_needed tests ---

@patch('server.game_manager.TicTacToe')
def test_make_agent_move_if_needed_no_game(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_game_instance.game_over = False # Ensure not game_over
    mock_game_instance.get_current_agent.return_value = None # No agent
    game_manager_instance.game = mock_game_instance

    game_manager_instance._make_agent_move_if_needed()
    mock_game_instance.check_winner.assert_not_called() # Should not call check_winner if game is None or no agent

@patch('server.game_manager.TicTacToe')
def test_make_agent_move_if_needed_game_over_initially(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_game_instance.game_over = True
    game_manager_instance.game = mock_game_instance

    game_manager_instance._make_agent_move_if_needed()
    mock_game_instance.get_current_agent.assert_not_called()

@patch('server.game_manager.TicTacToe')
def test_make_agent_move_if_needed_human_turn_initially(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_game_instance.game_over = False
    mock_game_instance.get_current_agent.return_value = None # Human turn
    game_manager_instance.game = mock_game_instance

    game_manager_instance._make_agent_move_if_needed()
    mock_game_instance.get_current_agent.assert_called_once()
    assert not mock_game_instance.make_move.called # No agent move should be made

@patch('server.game_manager.TicTacToe')
def test_make_agent_move_if_needed_agent_makes_move(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_agent = MagicMock()
    mock_agent.player = PLAYER_X
    mock_agent.get_move.return_value = (0, 0) # Agent proposes move (0,0)

    mock_game_instance.game_over = False
    mock_game_instance.current_player = PLAYER_X

    # Configure check_winner to update game_over and current_agent on the mock game instance
    def mock_check_winner_effect():
        # Simulate a game where there is no winner after the first agent move,
        # but the game is still not over, and player switches to human.
        # This will cause the _make_agent_move_if_needed loop to terminate.
        mock_game_instance.game_over = False # Game is not over
        mock_game_instance.current_player = PLAYER_O # Simulate switch_player's effect
        mock_game_instance.get_current_agent.return_value = None # Now it's human's turn
        return None # No winner yet

    mock_game_instance.check_winner.side_effect = mock_check_winner_effect
    mock_game_instance.get_current_agent.return_value = mock_agent # Initially agent's turn

    game_manager_instance.game = mock_game_instance

    game_manager_instance._make_agent_move_if_needed()

    mock_agent.get_move.assert_called_once()
    mock_game_instance.make_move.assert_called_once_with(0, 0)
    mock_game_instance.check_winner.assert_called_once()
    mock_game_instance.switch_player.assert_called_once() # Should be called because game is not over
    assert mock_game_instance.game_over == False # Game not over yet
    assert mock_game_instance.get_current_agent.call_count == 3 # Called three times

@patch('server.game_manager.TicTacToe')
def test_make_agent_move_if_needed_agent_move_leads_to_win(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_agent = MagicMock()
    mock_agent.player = PLAYER_X
    mock_agent.get_move.return_value = (0, 0)

    mock_game_instance.game_over = False
    mock_game_instance.current_player = PLAYER_X
    mock_game_instance.get_current_agent.return_value = mock_agent
    mock_game_instance.make_move.return_value = True

    def mock_check_winner_effect():
        mock_game_instance.game_over = True # Game is over
        return PLAYER_X # Agent wins

    mock_game_instance.check_winner.side_effect = mock_check_winner_effect

    game_manager_instance.game = mock_game_instance

    game_manager_instance._make_agent_move_if_needed()
    mock_game_instance.make_move.assert_called_once_with(0, 0)
    mock_game_instance.check_winner.assert_called_once()
    mock_game_instance.switch_player.assert_not_called() # Game over, no switch
    assert mock_game_instance.game_over == True # Game should be marked over

@patch('server.game_manager.TicTacToe')
def test_make_agent_move_if_needed_agent_raises_keyerror(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_agent = MagicMock()
    mock_agent.player = PLAYER_X
    mock_agent.get_move.side_effect = KeyError("Game is over") # Agent says game is over

    mock_game_instance.game_over = False
    mock_game_instance.current_player = PLAYER_X
    mock_game_instance.get_current_agent.return_value = mock_agent

    # Configure check_winner to update game_over when called
    def mock_check_winner_effect():
        mock_game_instance.game_over = True # Game is over
        return None # No explicit winner reported by this check
    mock_game_instance.check_winner.side_effect = mock_check_winner_effect

    game_manager_instance.game = mock_game_instance

    game_manager_instance._make_agent_move_if_needed()
    mock_agent.get_move.assert_called_once()
    mock_game_instance.check_winner.assert_called_once() # Should update game_over
    assert mock_game_instance.game_over == True # Game should be marked over

@patch('server.game_manager.TicTacToe')
def test_make_agent_move_if_needed_agent_returns_none_move(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_agent = MagicMock()
    mock_agent.player = PLAYER_X
    mock_agent.get_move.return_value = None # Agent indicates no valid move

    mock_game_instance.game_over = False
    mock_game_instance.current_player = PLAYER_X
    mock_game_instance.get_current_agent.return_value = mock_agent

    # Configure check_winner to update game_over when called
    def mock_check_winner_effect():
        mock_game_instance.game_over = True # Game is over
        return "draw" # Simulate a draw
    mock_game_instance.check_winner.side_effect = mock_check_winner_effect

    game_manager_instance.game = mock_game_instance

    game_manager_instance._make_agent_move_if_needed()
    mock_agent.get_move.assert_called_once()
    mock_game_instance.check_winner.assert_called_once() # Should update game_over
    assert mock_game_instance.game_over == True # Game should be marked over


# --- start_new_game tests ---

@patch('server.game_manager.TicTacToe')
def test_start_new_game(mock_tictactoe_class, game_manager_instance):
    player_x_type = "Human"
    player_o_type = "ランダム"
    human_player_symbol = PLAYER_X

    # Configure the mock TicTacToe instance (which is mock_tictactoe_class.return_value)
    # This is what game_manager_instance.game will be set to.
    mock_tictactoe_class.return_value.human_player = human_player_symbol
    mock_tictactoe_class.return_value.agent_x = None  # Human player
    mock_tictactoe_class.return_value.agent_o = MagicMock(spec=RandomAgent, player=PLAYER_O) # Mock the agent instance


    game_instance = game_manager_instance.start_new_game(player_x_type, player_o_type, human_player_symbol)

    mock_tictactoe_class.assert_called_once()
    # Check if TicTacToe was called with correct arguments
    call_args, call_kwargs = mock_tictactoe_class.call_args
    assert call_kwargs['agent_x'] is None
    assert isinstance(call_kwargs['agent_o'], RandomAgent) # Expect a real RandomAgent instance
    assert call_kwargs['agent_o'].player == PLAYER_O
    assert call_kwargs['human_player'] == human_player_symbol

    assert game_manager_instance.game == game_instance
    assert game_instance.human_player == human_player_symbol
    assert game_instance.agent_x is None # Human
    assert isinstance(game_instance.agent_o, RandomAgent) # Expect a real RandomAgent instance
    assert game_instance.agent_o.player == PLAYER_O

# --- get_current_game_state tests ---

def test_get_current_game_state_no_game(game_manager_instance):
    game_manager_instance.game = None
    with pytest.raises(HTTPException) as exc_info:
        game_manager_instance.get_current_game_state()
    assert exc_info.value.status_code == 404
    assert "Game not started" in exc_info.value.detail

def test_get_current_game_state_returns_correct_state(game_manager_instance, mock_game):
    game_manager_instance.game = mock_game
    state = game_manager_instance.get_current_game_state()

    assert state["board"] == mock_game.board
    assert state["current_player"] == mock_game.current_player
    assert state["winner"] == mock_game.check_winner.return_value
    assert state["winner_line"] == mock_game.winner_line
    assert state["game_over"] == mock_game.game_over

# --- make_player_move tests ---

def test_make_player_move_no_game(game_manager_instance):
    game_manager_instance.game = None
    with pytest.raises(HTTPException) as exc_info:
        game_manager_instance.make_player_move(0, 0)
    assert exc_info.value.status_code == 404
    assert "Game not started" in exc_info.value.detail

@patch('server.game_manager.TicTacToe')
def test_make_player_move_invalid_move(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_game_instance.make_move.return_value = False # Invalid move
    mock_game_instance.get_current_agent.return_value = None # Human player
    game_manager_instance.game = mock_game_instance

    with pytest.raises(HTTPException) as exc_info:
        game_manager_instance.make_player_move(0, 0)
    assert exc_info.value.status_code == 400
    assert "Invalid move" in exc_info.value.detail

@patch('server.game_manager.TicTacToe')
def test_make_player_move_valid_move_no_winner(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_game_instance.make_move.return_value = True
    mock_game_instance.check_winner.return_value = None # No winner yet
    mock_game_instance.get_current_agent.return_value = None # Human player
    game_manager_instance.game = mock_game_instance

    game_instance = game_manager_instance.make_player_move(0, 0)
    mock_game_instance.make_move.assert_called_once_with(0, 0)
    mock_game_instance.switch_player.assert_called_once()
    assert game_instance == mock_game_instance

@patch('server.game_manager.TicTacToe')
def test_make_player_move_valid_move_with_winner(mock_tictactoe_class, game_manager_instance):
    mock_game_instance = mock_tictactoe_class.return_value
    mock_game_instance.make_move.return_value = True
    mock_game_instance.check_winner.return_value = PLAYER_X # Winner
    mock_game_instance.get_current_agent.return_value = None # Human player
    game_manager_instance.game = mock_game_instance

    game_instance = game_manager_instance.make_player_move(0, 0)
    mock_game_instance.make_move.assert_called_once_with(0, 0)
    mock_game_instance.switch_player.assert_not_called() # Game over, no switch
    assert game_instance == mock_game_instance