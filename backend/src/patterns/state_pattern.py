from abc import ABC, abstractmethod
from typing import Optional

class WorkItemState(ABC):
    """State Pattern for Work Item Lifecycle"""
    
    @abstractmethod
    def get_state_name(self) -> str:
        pass
    
    @abstractmethod
    def can_transition_to(self, next_state: str) -> bool:
        pass
    
    @abstractmethod
    def validate_transition(self, work_item: dict) -> tuple[bool, Optional[str]]:
        """Returns (is_valid, error_message)"""
        pass

class OpenState(WorkItemState):
    def get_state_name(self) -> str:
        return "OPEN"
    
    def can_transition_to(self, next_state: str) -> bool:
        return next_state == "INVESTIGATING"
    
    def validate_transition(self, work_item: dict) -> tuple[bool, Optional[str]]:
        return True, None

class InvestigatingState(WorkItemState):
    def get_state_name(self) -> str:
        return "INVESTIGATING"
    
    def can_transition_to(self, next_state: str) -> bool:
        return next_state in ["RESOLVED", "OPEN"]
    
    def validate_transition(self, work_item: dict) -> tuple[bool, Optional[str]]:
        return True, None

class ResolvedState(WorkItemState):
    def get_state_name(self) -> str:
        return "RESOLVED"
    
    def can_transition_to(self, next_state: str) -> bool:
        return next_state in ["CLOSED", "INVESTIGATING"]
    
    def validate_transition(self, work_item: dict) -> tuple[bool, Optional[str]]:
        # Can go back to INVESTIGATING or forward to CLOSED
        return True, None

class ClosedState(WorkItemState):
    def get_state_name(self) -> str:
        return "CLOSED"
    
    def can_transition_to(self, next_state: str) -> bool:
        return False  # Terminal state
    
    def validate_transition(self, work_item: dict) -> tuple[bool, Optional[str]]:
        # Must have RCA to close
        if not work_item.get("has_rca"):
            return False, "Cannot close work item without RCA"
        return True, None

class StateManager:
    """Manages state transitions"""
    
    STATES = {
        "OPEN": OpenState(),
        "INVESTIGATING": InvestigatingState(),
        "RESOLVED": ResolvedState(),
        "CLOSED": ClosedState()
    }
    
    @classmethod
    def get_state(cls, state_name: str) -> WorkItemState:
        return cls.STATES.get(state_name, OpenState())
    
    @classmethod
    def validate_transition(cls, current_state: str, next_state: str, work_item: dict) -> tuple[bool, Optional[str]]:
        """Validate if transition is allowed"""
        state_obj = cls.get_state(current_state)
        
        # Check if transition is allowed
        if not state_obj.can_transition_to(next_state):
            return False, f"Cannot transition from {current_state} to {next_state}"
        
        # Validate transition requirements
        next_state_obj = cls.get_state(next_state)
        return next_state_obj.validate_transition(work_item)
