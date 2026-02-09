"""
Session Service

Manages OpenAI Agents SDK sessions for conversation persistence.
"""

from agents import SQLiteSession
from uuid import UUID, uuid4
from typing import Optional, Tuple
from pathlib import Path


# Session database path
SESSION_DB_PATH = "data/sessions.db"


def get_or_create_session(conversation_id: Optional[UUID] = None) -> Tuple[SQLiteSession, UUID]:
    """
    Get existing session or create a new one.

    Args:
        conversation_id: Optional UUID of existing conversation

    Returns:
        Tuple of (SQLiteSession, conversation_id)
    """
    # Create new conversation ID if not provided
    if conversation_id is None:
        conversation_id = uuid4()

    # Ensure data directory exists
    data_dir = Path(SESSION_DB_PATH).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create or retrieve session
    try:
        session = SQLiteSession(
            session_id=str(conversation_id),
            db_path=SESSION_DB_PATH
        )
        return session, conversation_id
    except Exception as e:
        raise RuntimeError(f"Failed to create/retrieve session: {str(e)}")


def close_session(session: SQLiteSession) -> None:
    """
    Close a session (cleanup if needed).

    Args:
        session: SQLiteSession to close
    """
    # SQLiteSession doesn't require explicit closing in current SDK version
    # This function is here for future compatibility
    pass


def delete_session(conversation_id: UUID) -> None:
    """
    Delete a session and its history.

    Args:
        conversation_id: UUID of conversation to delete
    """
    # Note: Current SDK doesn't provide direct session deletion
    # This would require direct database access
    # Placeholder for future implementation
    pass
