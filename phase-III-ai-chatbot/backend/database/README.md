# Phase III AI Chatbot - Database Documentation

## Overview

This database component provides persistent storage for AI chatbot conversations and messages. It extends the Phase II database with two new tables while maintaining full compatibility with existing schemas.

### Key Features

- **Stateless Architecture**: All conversation state stored in PostgreSQL
- **Async Operations**: Full async/await support for high performance
- **Repository Pattern**: Clean separation between business logic and data access
- **Type Safety**: SQLModel with full type hints
- **Migration Support**: Alembic for schema versioning

### Database Tables

- **conversations**: Chat session metadata
- **messages**: Individual chat messages
- **tasks**: Existing Phase II table (referenced, not modified)

---

## Schema Diagram

```
┌─────────────────────┐
│      users          │
│  (Phase II)         │
└──────────┬──────────┘
           │
           ├─────────────────────────────────┐
           │                                 │
           ▼                                 ▼
┌─────────────────────┐           ┌─────────────────────┐
│   conversations     │           │       tasks         │
│                     │           │    (Phase II)       │
│  - id (UUID)        │           │                     │
│  - user_id (FK)     │           │  - id (UUID)        │
│  - status           │           │  - user_id (FK)     │
│  - created_at       │           │  - title            │
│  - updated_at       │           │  - description      │
└──────────┬──────────┘           │  - status           │
           │                      │  - created_at       │
           │                      │  - completed_at     │
           ▼                      └─────────────────────┘
┌─────────────────────┐
│      messages       │
│                     │
│  - id (UUID)        │
│  - conversation_id  │
│  - user_id (FK)     │
│  - role             │
│  - content          │
│  - metadata (JSON)  │
│  - created_at       │
└─────────────────────┘
```

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (Neon Serverless PostgreSQL recommended)
- pip or uv package manager

### Installation

1. **Install Dependencies**

```bash
cd phase-III-ai-chatbot/backend
pip install sqlmodel asyncpg alembic psycopg2-binary
```

2. **Configure Database Connection**

Create `.env` file:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

For Neon PostgreSQL:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

3. **Initialize Alembic** (if not already done)

```bash
alembic init alembic
```

Update `alembic.ini`:
```ini
sqlalchemy.url = postgresql+asyncpg://localhost/phase3_chatbot
```

Update `alembic/env.py` to import models:
```python
from src.models import Conversation, Message
target_metadata = SQLModel.metadata
```

---

## Running Migrations

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade 001_conversations

# Apply one migration at a time
alembic upgrade +1
```

### Rollback Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 001_conversations

# Rollback all migrations
alembic downgrade base
```

### Check Migration Status

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

---

## Repository Usage Examples

### Conversation Operations

```python
from src.repositories.conversation_repository import ConversationRepository
from src.models.conversation import ConversationStatus

# Create new conversation
conversation = await ConversationRepository.create(user_id="user123")
print(f"Created conversation: {conversation.id}")

# Get conversation by ID
conv = await ConversationRepository.get_by_id(conversation.id)

# Get user's active conversations
active_convs = await ConversationRepository.get_user_conversations(
    user_id="user123",
    status=ConversationStatus.ACTIVE,
    limit=50
)

# Update conversation timestamp
await ConversationRepository.update_timestamp(conversation.id)

# Archive conversation
await ConversationRepository.archive(conversation.id)
```

### Message Operations

```python
from src.repositories.message_repository import MessageRepository
from src.models.message import MessageRole

# Create user message
user_msg = await MessageRepository.create(
    conversation_id=conversation.id,
    user_id="user123",
    role=MessageRole.USER,
    content="Add a task to buy groceries"
)

# Create assistant message with metadata
assistant_msg = await MessageRepository.create(
    conversation_id=conversation.id,
    user_id="user123",
    role=MessageRole.ASSISTANT,
    content="I've added the task",
    metadata={
        "tool": "add_task",
        "params": {"title": "Buy groceries"},
        "result": "success"
    }
)

# Get conversation history (last 20 messages)
messages = await MessageRepository.get_conversation_messages(
    conversation_id=conversation.id,
    limit=20
)

# Messages are returned in chronological order (oldest first)
for msg in messages:
    print(f"{msg.role}: {msg.content}")
```

### Complete Conversation Flow

```python
async def handle_chat_message(user_id: str, conversation_id: UUID, user_message: str):
    """Complete flow for handling a chat message"""

    # 1. Store user message
    await MessageRepository.create(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content=user_message
    )

    # 2. Get conversation history for context
    history = await MessageRepository.get_conversation_messages(
        conversation_id=conversation_id,
        limit=20
    )

    # 3. Process with AI (not shown)
    ai_response = "..." # AI processing here

    # 4. Store assistant response
    await MessageRepository.create(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content=ai_response
    )

    # 5. Update conversation timestamp
    await ConversationRepository.update_timestamp(conversation_id)

    return ai_response
```

---

## Common Queries

### Get Recent Conversations

```python
# Get user's 10 most recent conversations
conversations = await ConversationRepository.get_user_conversations(
    user_id="user123",
    limit=10
)
```

### Get Conversation with Messages

```python
# Get conversation and its messages
conv = await ConversationRepository.get_by_id(conversation_id)
messages = await MessageRepository.get_conversation_messages(conversation_id)

print(f"Conversation: {conv.id}")
print(f"Messages: {len(messages)}")
```

### Filter by Status

```python
# Get only archived conversations
archived = await ConversationRepository.get_user_conversations(
    user_id="user123",
    status=ConversationStatus.ARCHIVED
)
```

### Count Messages in Conversation

```python
messages = await MessageRepository.get_conversation_messages(conversation_id)
message_count = len(messages)
```

---

## Database Indexes

The following indexes are created for optimal query performance:

### Conversations Table
- `idx_conversations_user_id`: Fast user lookup
- `idx_conversations_updated_at`: Recent conversations query
- `idx_conversations_user_status`: Filtered user conversations

### Messages Table
- `idx_messages_conversation_id`: Fast conversation lookup
- `idx_messages_created_at`: Recent messages query
- `idx_messages_conversation_created`: Composite index for history retrieval (primary query pattern)

---

## Performance Considerations

### Connection Pooling

The database connection is configured with:
- Pool size: 10 connections
- Max overflow: 20 connections
- Pool timeout: 30 seconds
- Pool recycle: 3600 seconds (1 hour)

### Query Optimization

1. **Always use LIMIT**: Message queries default to 20 messages
2. **Use indexes**: All common queries use appropriate indexes
3. **Batch operations**: Use transactions for multiple operations
4. **Async operations**: All database calls are async

### Monitoring

Monitor these metrics:
- Query latency (target: <100ms p95)
- Connection pool utilization
- Slow query log
- Table sizes

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to database

**Solutions**:
1. Check DATABASE_URL environment variable
2. Verify database credentials
3. Check network connectivity
4. Ensure SSL mode is correct for Neon (`?sslmode=require`)

```bash
# Test connection
python -c "from src.database.connection import engine; import asyncio; asyncio.run(engine.connect())"
```

### Migration Issues

**Problem**: Migration fails with "relation already exists"

**Solution**: Check current migration state and reset if needed

```bash
# Check current state
alembic current

# If needed, stamp to specific revision
alembic stamp head
```

**Problem**: Alembic can't find models

**Solution**: Ensure models are imported in `alembic/env.py`

```python
from src.models.conversation import Conversation
from src.models.message import Message
target_metadata = SQLModel.metadata
```

### Query Performance Issues

**Problem**: Slow query performance

**Solutions**:
1. Check if indexes are being used:
```sql
EXPLAIN ANALYZE SELECT * FROM messages WHERE conversation_id = '...';
```

2. Verify indexes exist:
```sql
\di messages*
```

3. Check connection pool:
```python
print(engine.pool.status())
```

### Foreign Key Violations

**Problem**: Cannot create message with invalid conversation_id

**Solution**: This is expected behavior. Ensure conversation exists before creating messages.

```python
# Verify conversation exists
conv = await ConversationRepository.get_by_id(conversation_id)
if conv is None:
    raise ValueError("Conversation not found")
```

### Message Length Constraint

**Problem**: User message exceeds 1000 characters

**Solution**: Validate message length before database insert

```python
if role == MessageRole.USER and len(content) > 1000:
    raise ValueError("User message exceeds 1000 character limit")
```

---

## Testing

### Run Unit Tests

```bash
pytest tests/unit/test_models.py -v
```

### Run Integration Tests

```bash
# Requires test database
export DATABASE_URL=postgresql+asyncpg://localhost/test_db
pytest tests/integration/test_database.py -v
```

### Test Coverage

```bash
pytest --cov=src --cov-report=html
```

---

## Maintenance

### Daily Tasks
- Monitor query performance
- Check error logs
- Verify backup completion

### Weekly Tasks
- Review slow query log
- Check table growth
- Analyze index usage

### Monthly Tasks
- Archive old conversations (90+ days)
- Optimize indexes if needed
- Review and update documentation

### Archival Script

```python
from datetime import datetime, timedelta

async def archive_old_conversations():
    """Archive conversations older than 90 days"""
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    # Implementation would query and update conversations
    # This is a placeholder for the actual implementation
    pass
```

---

## Security

### Best Practices

1. **Never commit credentials**: Use environment variables
2. **Use SSL**: Always use `sslmode=require` for production
3. **Parameterized queries**: SQLModel handles this automatically
4. **Input validation**: Validate all user input before database operations
5. **Access control**: Ensure users can only access their own data

### Data Privacy

- User conversations are isolated by user_id
- Foreign key constraints enforce data integrity
- Cascade deletes ensure no orphaned data

---

## Additional Resources

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Neon Documentation](https://neon.tech/docs/)

---

## Support

For issues or questions:
1. Check this documentation
2. Review error logs
3. Check database connection
4. Verify migrations are applied
5. Test with simple queries

---

**Last Updated**: 2026-02-09
**Version**: 1.0
**Status**: Production Ready
