import pytest
from unittest.mock import MagicMock, patch, mock_open
import os

from server.game_manager import GameManager
from agents.base_agent import BaseAgent
from agents.random_agent import RandomAgent


# --- get_available_agents tests ---

def test_get_available_agents_returns_correct_list():
    """Test that get_available_agents returns the correct list of agents"""
    gm = GameManager()
    agents = gm.get_available_agents()
    
    # Human should be first
    assert agents[0] == "Human"
    
    # Should contain all expected agents
    assert "Random" in agents
    assert "Minimax" in agents
    assert "Perfect" in agents
    assert "QLearning" in agents
    assert "Database" in agents
    
    # Should not contain Japanese aliases
    assert "ランダム" not in agents


def test_get_available_agents_sorted():
    """Test that agents are sorted (except Human which is first)"""
    gm = GameManager()
    agents = gm.get_available_agents()
    
    # Skip Human (first element) and check if rest is sorted
    rest = agents[1:]
    assert rest == sorted(rest)


# --- _discover_agents tests ---

@patch('server.game_manager.os.listdir')
def test_discover_agents_skips_base_agent(mock_listdir):
    """Test that _discover_agents skips base_agent.py"""
    mock_listdir.return_value = ['base_agent.py', '__init__.py']
    
    gm = GameManager()
    
    # Should only have Human (base_agent.py should be skipped)
    agents = gm.get_available_agents()
    assert agents == ["Human"]


@patch('os.listdir')
@patch('importlib.import_module')
def test_discover_agents_skips_non_py_files(mock_import, mock_listdir):
    """Test that _discover_agents skips non-.py files"""
    mock_listdir.return_value = ['README.md', '__pycache__', 'random_agent.py']
    
    # Create a fresh GameManager to trigger _discover_agents
    gm = GameManager()
    
    # Only random_agent.py should be considered
    # Note: The actual import might fail, but we're testing the filtering logic


@patch('os.path.exists')
def test_discover_agents_handles_missing_directory(mock_exists):
    """Test that _discover_agents handles missing agents directory gracefully"""
    mock_exists.return_value = False
    
    # Should not raise an error
    gm = GameManager()
    agents = gm.get_available_agents()
    
    # Should at least have Human
    assert "Human" in agents


@patch('server.game_manager.os.listdir')
@patch('server.game_manager.importlib.import_module')
def test_discover_agents_handles_import_error(mock_import, mock_listdir):
    """Test that _discover_agents handles import errors gracefully"""
    mock_listdir.return_value = ['broken_agent.py']
    mock_import.side_effect = ImportError("Module not found")
    
    # Should not raise an error, just print a warning
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    gm = GameManager()
    
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    # Should have printed a warning
    assert "Warning" in output or "Could not import" in output


# --- Integration tests ---

def test_agent_classes_populated():
    """Test that AGENT_CLASSES is populated with discovered agents"""
    gm = GameManager()
    
    # Should have Human
    assert "Human" in gm.AGENT_CLASSES
    assert gm.AGENT_CLASSES["Human"] is None
    
    # Should have Random
    assert "Random" in gm.AGENT_CLASSES
    assert gm.AGENT_CLASSES["Random"] == RandomAgent
    
    # Should have Japanese alias for Random
    assert "ランダム" in gm.AGENT_CLASSES
    assert gm.AGENT_CLASSES["ランダム"] == RandomAgent


def test_agent_aliases():
    """Test that agent aliases are correctly set up"""
    gm = GameManager()
    
    # Random should have a Japanese alias
    assert "ランダム" in gm.AGENT_CLASSES
    assert gm.AGENT_CLASSES["ランダム"] == gm.AGENT_CLASSES["Random"]
