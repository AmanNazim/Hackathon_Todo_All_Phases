"""
Task workflow service for managing task status transitions.
"""

from typing import Dict, List, Optional
from fastapi import HTTPException, status


# Define allowed status transitions
STATUS_TRANSITIONS: Dict[str, List[str]] = {
    "todo": ["in_progress", "blocked"],
    "in_progress": ["review", "done", "blocked", "todo"],
    "review": ["done", "in_progress", "blocked"],
    "done": ["todo"],  # Allow reopening completed tasks
    "blocked": ["todo", "in_progress"]
}


def validate_status_transition(current_status: str, new_status: str) -> bool:
    """
    Validate if a status transition is allowed.

    Args:
        current_status: Current task status
        new_status: Desired new status

    Returns:
        True if transition is valid, False otherwise
    """
    if current_status == new_status:
        return True

    allowed_transitions = STATUS_TRANSITIONS.get(current_status, [])
    return new_status in allowed_transitions


def get_allowed_transitions(current_status: str) -> List[str]:
    """
    Get list of allowed status transitions from current status.

    Args:
        current_status: Current task status

    Returns:
        List of allowed status values
    """
    return STATUS_TRANSITIONS.get(current_status, [])


def enforce_status_transition(current_status: str, new_status: str) -> None:
    """
    Enforce status transition rules, raising exception if invalid.

    Args:
        current_status: Current task status
        new_status: Desired new status

    Raises:
        HTTPException: If transition is not allowed
    """
    if not validate_status_transition(current_status, new_status):
        allowed = get_allowed_transitions(current_status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status}' to '{new_status}'. "
                   f"Allowed transitions: {', '.join(allowed)}"
        )


def get_status_workflow_info() -> Dict[str, List[str]]:
    """
    Get complete status workflow information.

    Returns:
        Dictionary mapping each status to its allowed transitions
    """
    return STATUS_TRANSITIONS.copy()
