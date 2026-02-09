"""Conversation repository for database operations"""

from sqlmodel import select
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from ..models.conversation import Conversation, ConversationStatus
from ..database.connection import get_session


class ConversationRepository:
    """Repository for conversation CRUD operations"""

    @staticmethod
    async def create(user_id: str) -> Conversation:
        """
        Create new conversation for a user.

        Args:
            user_id: User identifier

        Returns:
            Created conversation instance
        """
        async with get_session() as session:
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation

    @staticmethod
    async def get_by_id(conversation_id: UUID) -> Optional[Conversation]:
        """
        Get conversation by ID.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Conversation instance or None if not found
        """
        async with get_session() as session:
            return await session.get(Conversation, conversation_id)

    @staticmethod
    async def get_user_conversations(
        user_id: str,
        status: Optional[ConversationStatus] = None,
        limit: int = 50
    ) -> List[Conversation]:
        """
        Get user's conversations with optional status filter.

        Args:
            user_id: User identifier
            status: Optional status filter (active or archived)
            limit: Maximum number of conversations to return

        Returns:
            List of conversations ordered by most recent first
        """
        async with get_session() as session:
            query = select(Conversation).where(Conversation.user_id == user_id)

            if status:
                query = query.where(Conversation.status == status)

            query = query.order_by(Conversation.updated_at.desc()).limit(limit)
            result = await session.exec(query)
            return list(result.all())

    @staticmethod
    async def update_timestamp(conversation_id: UUID) -> None:
        """
        Update conversation's updated_at timestamp to current time.

        Args:
            conversation_id: Conversation UUID
        """
        async with get_session() as session:
            conversation = await session.get(Conversation, conversation_id)
            if conversation:
                conversation.updated_at = datetime.utcnow()
                await session.commit()

    @staticmethod
    async def archive(conversation_id: UUID) -> None:
        """
        Archive a conversation by changing its status.

        Args:
            conversation_id: Conversation UUID
        """
        async with get_session() as session:
            conversation = await session.get(Conversation, conversation_id)
            if conversation:
                conversation.status = ConversationStatus.ARCHIVED
                await session.commit()
