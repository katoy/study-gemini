import pytest
from server.game_manager import GameManager

def test_create_agent_with_alias():
    """
    Test that GameManager can create an agent using its alias (e.g., "Random").
    """
    game_manager = GameManager()

    # "Random" should be mapped to "ランダム" and create a RandomAgent
    agent = game_manager._create_agent("Random", "O")

    assert agent is not None
    # Verify it's a RandomAgent (checking class name or type)
    # Since we don't import RandomAgent directly here, we can check the class name
    assert agent.__class__.__name__ == "RandomAgent"

def test_create_agent_with_japanese_name():
    """
    Test that GameManager can still create an agent using its Japanese name.
    """
    game_manager = GameManager()

    # "ランダム" should work directly
    agent = game_manager._create_agent("ランダム", "O")

    assert agent is not None
    assert agent.__class__.__name__ == "RandomAgent"

def test_start_game_with_alias():
    """
    Test starting a game with an alias.
    """
    game_manager = GameManager()

    # Start game with Human vs Random (using alias)
    game = game_manager.start_new_game(
        player_x_type="Human",
        player_o_type="Random",
        human_player_symbol="X"
    )

    assert game is not None
    assert game.agent_o is not None
    assert game.agent_o.__class__.__name__ == "RandomAgent"
