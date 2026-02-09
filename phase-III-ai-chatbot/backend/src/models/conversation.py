"""Conversation model for AI chatbot"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .message import Message


class ConversationStatus(str, Enum):
    """Conversation status enum"""
    ACTIVE = "active"
    ARCHIVED = "archived"


class Conversation(SQLModel, table=True):
    """Conversation model representing a chat session"""
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
