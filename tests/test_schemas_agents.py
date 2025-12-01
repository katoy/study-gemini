import pytest
from pydantic import ValidationError

from server.schemas import AvailableAgentsResponse


def test_available_agents_response_valid():
    """Test valid AvailableAgentsResponse"""
    response = AvailableAgentsResponse(agents=["Human", "Random", "Minimax"])
    assert response.agents == ["Human", "Random", "Minimax"]


def test_available_agents_response_empty_list():
    """Test AvailableAgentsResponse with empty list"""
    response = AvailableAgentsResponse(agents=[])
    assert response.agents == []


def test_available_agents_response_invalid_type():
    """Test AvailableAgentsResponse with invalid type"""
    with pytest.raises(ValidationError):
        AvailableAgentsResponse(agents="not a list")
