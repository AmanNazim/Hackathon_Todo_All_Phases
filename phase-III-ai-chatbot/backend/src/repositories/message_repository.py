"""Message repository for database operations"""

from sqlmodel import select
from uuid import UUID
from typing import List, Optional, Dict, Any
from ..models.message import Message, MessageRole
from ..database.connection import get_session


class MessageRepository:
    """Repository for message CRUD operations"""

    @staticmethod
    async def create(
        conversation_id: UUID,
        user_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Create new message in a conversation.

        Args:
            conversation_id: Conversation UUID
            user_id: User identifier
            role: Message role (user or assistant)
            content: Message text content
            metadata: Optional metadata (tool calls, actions, etc.)

        Returns:
            Created message instance
        """
        async with get_session() as session:
            message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role,
                content=content,
                metadata=metadata
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    @staticmethod
    async def get_conversation_messages(
        conversation_id: UUID,
        limit: int = 20
    ) -> List[Message]:
        """
        Get messages for a conversation in chronological order.

        Retrieves the most recent N messages and returns them in chronological
        order (oldest first). This is useful for building conversation context.

        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of messages to return (default: 20)

        Returns:
            List of messages in chronological order (oldest to newest)
        """
        async with get_session() as session:
            # Query most recent messages in descending order
            query = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(limit)

            result = await session.exec(query)
            messages = list(result.all())

            # Reverse to get chronological order (oldest to newest)
            return list(reversed(messages))
