"""Integration tests for database operations"""

import pytest
import asyncio
from uuid import uuid4
from src.repositories.conversation_repository import ConversationRepository
from src.repositories.message_repository import MessageRepository
from src.models.conversation import ConversationStatus
from src.models.message import MessageRole


@pytest.mark.asyncio
class TestDatabaseIntegration:
    """Integration tests for database operations"""

    async def test_create_conversation(self):
        """Test creating a conversation in the database"""
        conv = await ConversationRepository.create("user123")

        assert conv.id is not None
        assert conv.user_id == "user123"
        assert conv.status == ConversationStatus.ACTIVE

    async def test_get_conversation_by_id(self):
        """Test retrieving conversation by ID"""
        # Create conversation
        conv = await ConversationRepository.create("user123")

        # Retrieve it
        fetched = await ConversationRepository.get_by_id(conv.id)

        assert fetched is not None
        assert fetched.id == conv.id
        assert fetched.user_id == "user123"

    async def test_create_and_retrieve_messages(self):
        """Test creating and retrieving messages for a conversation"""
        # Create conversation
        conv = await ConversationRepository.create("user123")

        # Add messages
        msg1 = await MessageRepository.create(
            conv.id, "user123", MessageRole.USER, "Hello"
        )
        msg2 = await MessageRepository.create(
            conv.id, "user123", MessageRole.ASSISTANT, "Hi there!"
        )

        # Retrieve messages
        messages = await MessageRepository.get_conversation_messages(conv.id)

        assert len(messages) == 2
        assert messages[0].content == "Hello"
        assert messages[0].role == MessageRole.USER
        assert messages[1].content == "Hi there!"
        assert messages[1].role == MessageRole.ASSISTANT

    async def test_conversation_timestamp_update(self):
        """Test updating conversation timestamp"""
        conv = await ConversationRepository.create("user123")
        original_time = conv.updated_at

        # Wait a bit and update
        await asyncio.sleep(0.1)
        await ConversationRepository.update_timestamp(conv.id)

        # Verify timestamp changed
        updated_conv = await ConversationRepository.get_by_id(conv.id)
        assert updated_conv.updated_at > original_time

    async def test_archive_conversation(self):
        """Test archiving a conversation"""
        conv = await ConversationRepository.create("user123")
        assert conv.status == ConversationStatus.ACTIVE

        # Archive it
        await ConversationRepository.archive(conv.id)

        # Verify status changed
        archived_conv = await ConversationRepository.get_by_id(conv.id)
        assert archived_conv.status == ConversationStatus.ARCHIVED

    async def test_get_user_conversations(self):
        """Test retrieving all conversations for a user"""
        # Create multiple conversations
        conv1 = await ConversationRepository.create("user123")
        conv2 = await ConversationRepository.create("user123")
        conv3 = await ConversationRepository.create("user456")  # Different user

        # Get user123's conversations
        conversations = await ConversationRepository.get_user_conversations("user123")

        assert len(conversations) >= 2
        user_ids = [c.user_id for c in conversations]
        assert all(uid == "user123" for uid in user_ids)

    async def test_get_user_conversations_with_status_filter(self):
        """Test filtering conversations by status"""
        # Create conversations with different statuses
        conv1 = await ConversationRepository.create("user123")
        conv2 = await ConversationRepository.create("user123")
        await ConversationRepository.archive(conv2.id)

        # Get only active conversations
        active_convs = await ConversationRepository.get_user_conversations(
            "user123", status=ConversationStatus.ACTIVE
        )

        assert len(active_convs) >= 1
        assert all(c.status == ConversationStatus.ACTIVE for c in active_convs)

        # Get only archived conversations
        archived_convs = await ConversationRepository.get_user_conversations(
            "user123", status=ConversationStatus.ARCHIVED
        )

        assert len(archived_convs) >= 1
        assert all(c.status == ConversationStatus.ARCHIVED for c in archived_convs)

    async def test_message_with_metadata(self):
        """Test creating message with metadata"""
        conv = await ConversationRepository.create("user123")

        metadata = {
            "tool": "add_task",
            "params": {"title": "Buy groceries"},
            "result": "success"
        }

        msg = await MessageRepository.create(
            conv.id,
            "user123",
            MessageRole.ASSISTANT,
            "I've added the task",
            metadata=metadata
        )

        # Retrieve and verify
        messages = await MessageRepository.get_conversation_messages(conv.id)
        assert len(messages) == 1
        assert messages[0].metadata == metadata
        assert messages[0].metadata["tool"] == "add_task"

    async def test_conversation_messages_limit(self):
        """Test limiting number of messages retrieved"""
        conv = await ConversationRepository.create("user123")

        # Create 10 messages
        for i in range(10):
            await MessageRepository.create(
                conv.id,
                "user123",
                MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                f"Message {i}"
            )

        # Retrieve only 5 messages
        messages = await MessageRepository.get_conversation_messages(conv.id, limit=5)

        assert len(messages) == 5
        # Should get the 5 most recent messages in chronological order
        assert messages[0].content == "Message 5"
        assert messages[4].content == "Message 9"

    async def test_messages_chronological_order(self):
        """Test that messages are returned in chronological order"""
        conv = await ConversationRepository.create("user123")

        # Create messages in sequence
        msg1 = await MessageRepository.create(
            conv.id, "user123", MessageRole.USER, "First"
        )
        await asyncio.sleep(0.01)
        msg2 = await MessageRepository.create(
            conv.id, "user123", MessageRole.ASSISTANT, "Second"
        )
        await asyncio.sleep(0.01)
        msg3 = await MessageRepository.create(
            conv.id, "user123", MessageRole.USER, "Third"
        )

        # Retrieve messages
        messages = await MessageRepository.get_conversation_messages(conv.id)

        assert len(messages) == 3
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[2].content == "Third"
        assert messages[0].created_at < messages[1].created_at < messages[2].created_at

    async def test_multiple_conversations_isolation(self):
        """Test that messages are isolated between conversations"""
        # Create two conversations
        conv1 = await ConversationRepository.create("user123")
        conv2 = await ConversationRepository.create("user123")

        # Add messages to each
        await MessageRepository.create(
            conv1.id, "user123", MessageRole.USER, "Conv1 Message"
        )
        await MessageRepository.create(
            conv2.id, "user123", MessageRole.USER, "Conv2 Message"
        )

        # Verify isolation
        conv1_messages = await MessageRepository.get_conversation_messages(conv1.id)
        conv2_messages = await MessageRepository.get_conversation_messages(conv2.id)

        assert len(conv1_messages) == 1
        assert len(conv2_messages) == 1
        assert conv1_messages[0].content == "Conv1 Message"
        assert conv2_messages[0].content == "Conv2 Message"

    async def test_conversation_ordering_by_updated_at(self):
        """Test that conversations are ordered by most recent update"""
        # Create conversations
        conv1 = await ConversationRepository.create("user123")
        await asyncio.sleep(0.01)
        conv2 = await ConversationRepository.create("user123")
        await asyncio.sleep(0.01)

        # Update conv1 timestamp (making it most recent)
        await ConversationRepository.update_timestamp(conv1.id)

        # Get conversations
        conversations = await ConversationRepository.get_user_conversations("user123")

        # conv1 should be first (most recent)
        assert conversations[0].id == conv1.id

    async def test_empty_conversation_messages(self):
        """Test retrieving messages from conversation with no messages"""
        conv = await ConversationRepository.create("user123")

        messages = await MessageRepository.get_conversation_messages(conv.id)

        assert len(messages) == 0
        assert messages == []

    async def test_nonexistent_conversation(self):
        """Test retrieving nonexistent conversation returns None"""
        fake_id = uuid4()
        conv = await ConversationRepository.get_by_id(fake_id)

        assert conv is None


# Note: The following tests require actual database constraints to be enforced
# They are included for completeness but may need database setup to run

@pytest.mark.asyncio
class TestDatabaseConstraints:
    """Tests for database constraints (requires actual database)"""

    @pytest.mark.skip(reason="Requires database with constraints")
    async def test_user_message_length_constraint(self):
        """Test that user messages exceeding 1000 chars are rejected"""
        conv = await ConversationRepository.create("user123")

        # Try to create message exceeding 1000 chars
        long_content = "x" * 1001

        with pytest.raises(Exception):  # Should raise constraint violation
            await MessageRepository.create(
                conv.id, "user123", MessageRole.USER, long_content
            )

    @pytest.mark.skip(reason="Requires database with constraints")
    async def test_invalid_message_role_constraint(self):
        """Test that invalid message roles are rejected"""
        conv = await ConversationRepository.create("user123")

        # This would require bypassing the enum, which SQLModel prevents
        # But at database level, invalid roles should be rejected
        pass

    @pytest.mark.skip(reason="Requires database with foreign keys")
    async def test_cascade_delete(self):
        """Test that deleting conversation cascades to messages"""
        # Create conversation with messages
        conv = await ConversationRepository.create("user123")
        await MessageRepository.create(
            conv.id, "user123", MessageRole.USER, "Test"
        )

        # Delete conversation (would need delete method in repository)
        # Messages should be automatically deleted due to CASCADE

        # Verify messages are gone
        messages = await MessageRepository.get_conversation_messages(conv.id)
        assert len(messages) == 0
