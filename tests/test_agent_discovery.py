import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import importlib

from server.game_manager import GameManager
from agent_discovery import get_agent_details, AGENT_ALIASES, BaseAgent
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.database_agent import DatabaseAgent
from agents.perfect_agent import PerfectAgent
from agents.q_learning_agent import QLearningAgent


# --- get_agent_details tests ---


def test_get_agent_details_returns_correct_list_and_map():
    """Test that get_agent_details returns the correct list of agents and map"""
    display_names, agent_map = get_agent_details()

    assert "Human" not in display_names  # Human is added by GameManager
    assert "ランダム" in display_names
    assert "Minimax" in display_names
    assert "Database" in display_names
    assert "Perfect" in display_names
    assert "QLearning" in display_names

    assert "ランダム" == display_names[0]  # "ランダム" should be first in display_names

    assert agent_map["ランダム"] == RandomAgent
    assert agent_map["Minimax"] == MinimaxAgent
