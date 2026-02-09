"""
ChatKit Event Adapters

Functions to convert Agent SDK events to ChatKit event format.
"""

from typing import Any, Dict


def convert_to_chatkit_event(agent_event: Any) -> Dict[str, Any]:
    """
    Convert Agent SDK event to ChatKit event format.

    Args:
        agent_event: Event from Agent SDK streaming

    Returns:
        ChatKit-compatible event dictionary
    """
    # Handle text delta events
    if hasattr(agent_event, 'text') and agent_event.text:
        return {
            "type": "text_delta",
            "text": agent_event.text
        }

    # Handle tool call events
    if hasattr(agent_event, 'tool_name'):
        return {
            "type": "tool_call",
            "tool": agent_event.tool_name,
            "status": "running"
        }

    # Handle completion events
    if hasattr(agent_event, 'type') and agent_event.type == 'complete':
        return {
            "type": "complete"
        }

    # Handle error events
    if hasattr(agent_event, 'type') and agent_event.type == 'error':
        return {
            "type": "error",
            "error": getattr(agent_event, 'error', 'Unknown error'),
            "message": getattr(agent_event, 'message', 'An error occurred')
        }

    # Pass through unknown events
    return agent_event if isinstance(agent_event, dict) else {"type": "unknown", "data": str(agent_event)}


def convert_text_event(text: str) -> Dict[str, Any]:
    """
    Create a ChatKit text delta event.

    Args:
        text: Text content to send

    Returns:
        ChatKit text delta event
    """
    return {
        "type": "text_delta",
        "text": text
    }


def convert_tool_event(tool_name: str, status: str = "running") -> Dict[str, Any]:
    """
    Create a ChatKit tool call event.

    Args:
        tool_name: Name of the tool being called
        status: Status of the tool call (running, complete, error)

    Returns:
        ChatKit tool call event
    """
    return {
        "type": "tool_call",
        "tool": tool_name,
        "status": status
    }


def convert_complete_event() -> Dict[str, Any]:
    """
    Create a ChatKit completion event.

    Returns:
        ChatKit complete event
    """
    return {
        "type": "complete"
    }


def convert_error_event(error: str, message: str = None) -> Dict[str, Any]:
    """
    Create a ChatKit error event.

    Args:
        error: Error identifier
        message: User-friendly error message

    Returns:
        ChatKit error event
    """
    return {
        "type": "error",
        "error": error,
        "message": message or "An error occurred during processing"
    }
