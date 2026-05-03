import pytest
from src.patterns.state_pattern import StateManager

def test_cannot_close_without_rca():
    """Test that work item cannot be closed without RCA"""
    work_item = {
        "id": 1,
        "state": "RESOLVED",
        "has_rca": False
    }
    
    is_valid, error = StateManager.validate_transition("RESOLVED", "CLOSED", work_item)
    
    assert not is_valid
    assert "Cannot close work item without RCA" in error

def test_can_close_with_rca():
    """Test that work item can be closed with RCA"""
    work_item = {
        "id": 1,
        "state": "RESOLVED",
        "has_rca": True
    }
    
    is_valid, error = StateManager.validate_transition("RESOLVED", "CLOSED", work_item)
    
    assert is_valid
    assert error is None

def test_state_transitions():
    """Test valid state transitions"""
    # OPEN -> INVESTIGATING
    assert StateManager.get_state("OPEN").can_transition_to("INVESTIGATING")
    
    # INVESTIGATING -> RESOLVED
    assert StateManager.get_state("INVESTIGATING").can_transition_to("RESOLVED")
    
    # RESOLVED -> CLOSED
    assert StateManager.get_state("RESOLVED").can_transition_to("CLOSED")
    
    # Cannot go from CLOSED anywhere
    assert not StateManager.get_state("CLOSED").can_transition_to("RESOLVED")
