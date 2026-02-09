"""Unit tests for database models"""

import pytest
from uuid import uuid4
from datetime import datetime
from src.models.conversation import Conversation, ConversationStatus
from src.models.message import Message, MessageRole


class TestConversationModel:
    """Test cases for Conversation model"""

    def test_conversation_creation(self):
        """Test creating a conversation with default values"""
        conv = Conversation(user_id="user123")

        assert conv.id is not None
        assert conv.user_id == "user123"
        assert conv.status == ConversationStatus.ACTIVE
        assert isinstance(conv.created_at, datetime)
        assert isinstance(conv.updated_at, datetime)

    def test_conversation_status_enum(self):
        """Test conversation status enum values"""
        assert ConversationStatus.ACTIVE == "active"
        assert ConversationStatus.ARCHIVED == "archived"

    def test_conversation_with_custom_status(self):
        """Test creating conversation with archived status"""
        conv = Conversation(user_id="user123", status=ConversationStatus.ARCHIVED)
        assert conv.status == ConversationStatus.ARCHIVED

    def test_conversation_with_custom_id(self):
        """Test creating conversation with custom UUID"""
        custom_id = uuid4()
        conv = Conversation(id=custom_id, user_id="user123")
        assert conv.id == custom_id

    def test_conversation_timestamps(self):
        """Test that timestamps are set correctly"""
        conv = Conversation(user_id="user123")
        assert conv.created_at <= datetime.utcnow()
        assert conv.updated_at <= datetime.utcnow()
        assert conv.created_at <= conv.updated_at


class TestMessageModel:
    """Test cases for Message model"""

    def test_message_creation(self):
        """Test creating a message with required fields"""
        msg = Message(
            conversation_id=uuid4(),
            user_id="user123",
            role=MessageRole.USER,
            content="Hello"
        )

        assert msg.id is not None
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
        assert msg.metadata is None
        assert isinstance(msg.created_at, datetime)

    def test_message_role_enum(self):
        """Test message role enum values"""
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"

    def test_message_with_metadata(self):
        """Test creating message with metadata"""
        metadata = {"tool": "add_task", "result": "success"}
        msg = Message(
            conversation_id=uuid4(),
            user_id="user123",
            role=MessageRole.ASSISTANT,
            content="Task added",
            metadata=metadata
        )
        assert msg.metadata == metadata
        assert msg.metadata["tool"] == "add_task"

    def test_message_assistant_role(self):
        """Test creating assistant message"""
        msg = Message(
            conversation_id=uuid4(),
            user_id="user123",
            role=MessageRole.ASSISTANT,
            content="How can I help you?"
        )
        assert msg.role == MessageRole.ASSISTANT

    def test_message_with_custom_id(self):
        """Test creating message with custom UUID"""
        custom_id = uuid4()
        msg = Message(
            id=custom_id,
            conversation_id=uuid4(),
            user_id="user123",
            role=MessageRole.USER,
            content="Test"
        )
        assert msg.id == custom_id

    def test_message_timestamp(self):
        """Test that message timestamp is set correctly"""
        msg = Message(
            conversation_id=uuid4(),
            user_id="user123",
            role=MessageRole.USER,
            content="Test"
        )
        assert msg.created_at <= datetime.utcnow()

    def test_message_with_empty_metadata(self):
        """Test message with explicitly empty metadata"""
        msg = Message(
            conversation_id=uuid4(),
            user_id="user123",
            role=MessageRole.USER,
            content="Test",
            metadata={}
        )
        assert msg.metadata == {}

    def test_message_with_complex_metadata(self):
        """Test message with complex nested metadata"""
        metadata = {
            "tool_calls": [
                {"tool": "add_task", "params": {"title": "Buy milk"}},
                {"tool": "list_tasks", "params": {"status": "pending"}}
            ],
            "timestamp": "2026-02-09T10:00:00Z"
        }
        msg = Message(
            conversation_id=uuid4(),
            user_id="user123",
            role=MessageRole.ASSISTANT,
            content="I've added the task",
            metadata=metadata
        )
        assert msg.metadata == metadata
        assert len(msg.metadata["tool_calls"]) == 2
