# Database Implementation Plan: Phase III AI Chatbot Storage

**Date**: 2026-02-09
**Spec**: [spec.md](./spec.md)
**Component**: Database Schema and Migrations

---

## Summary

Implement PostgreSQL database schema for storing AI chatbot conversations and messages. Extend Phase II database with two new tables (conversations, messages) while maintaining full compatibility with existing schema. Use Alembic for migrations and SQLModel for ORM.

---

## Technical Context

**Database**: Neon Serverless PostgreSQL (existing from Phase II)
**ORM**: SQLModel (existing from Phase II)
**Migration Tool**: Alembic (existing from Phase II)
**Python Version**: 3.11+
**Connection Library**: asyncpg

**Performance Goals**:
- Query latency: <100ms p95 for history retrieval
- Write latency: <50ms p95 for message insert
- Support: 100+ concurrent connections

**Constraints**:
- Must not modify Phase II tables
- Must use existing database connection
- Must follow Phase II naming conventions

---

## Database Schema Design

### Table 1: conversations

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_conversations_user_status ON conversations(user_id, status);
```

**Purpose**: Store chat session metadata
**Key Design Decisions**:
- UUID for globally unique IDs
- Foreign key to users with CASCADE delete
- Status enum enforced at database level
- Indexes for user lookup and recent conversations

### Table 2: messages

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_user_message_length CHECK (role != 'user' OR length(content) <= 1000)
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
```

**Purpose**: Store individual chat messages
**Key Design Decisions**:
- Composite index on (conversation_id, created_at) for efficient history queries
- JSONB for flexible metadata storage
- Check constraint for user message length
- Cascade delete with conversation

---

## SQLModel Models

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

### Message Model

```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id")
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

---

## Migration Strategy

### Migration Files

**File 1**: `001_create_conversations_table.py`
- Create conversations table
- Create indexes
- Add constraints

**File 2**: `002_create_messages_table.py`
- Create messages table
- Create indexes
- Add constraints

### Migration Execution Order

1. Run Phase II migrations (if not already applied)
2. Run `001_create_conversations_table.py`
3. Run `002_create_messages_table.py`
4. Verify schema with test queries

### Rollback Strategy

Each migration includes downgrade function:
- Drop indexes first
- Drop tables in reverse order (messages, then conversations)
- No data loss for Phase II tables

---

## Implementation Tasks

### Task 1: Create SQLModel Models
**Files**: `backend/src/models/conversation.py`, `backend/src/models/message.py`
**Acceptance**: Models match schema, relationships defined, enums work

### Task 2: Create Alembic Migrations
**Files**: `backend/alembic/versions/001_*.py`, `backend/alembic/versions/002_*.py`
**Acceptance**: Migrations apply cleanly, rollback works, indexes created

### Task 3: Database Connection Setup
**Files**: `backend/src/database/connection.py`
**Acceptance**: Connection pool configured, async support, error handling

### Task 4: Repository Layer
**Files**: `backend/src/repositories/conversation_repository.py`, `backend/src/repositories/message_repository.py`
**Acceptance**: CRUD operations work, queries optimized, transactions handled

### Task 5: Integration Tests
**Files**: `backend/tests/integration/test_database.py`
**Acceptance**: All CRUD operations tested, foreign keys verified, performance acceptable

---

## Query Patterns

### Pattern 1: Get Recent Conversations
```python
async def get_user_conversations(user_id: str, limit: int = 50):
    query = select(Conversation).where(
        Conversation.user_id == user_id,
        Conversation.status == ConversationStatus.ACTIVE
    ).order_by(Conversation.updated_at.desc()).limit(limit)
    return await session.exec(query)
```

### Pattern 2: Get Conversation History
```python
async def get_conversation_messages(conversation_id: UUID, limit: int = 20):
    query = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(limit)
    messages = await session.exec(query)
    return list(reversed(messages))  # Return in chronological order
```

### Pattern 3: Create Message and Update Conversation
```python
async def add_message(conversation_id: UUID, user_id: str, role: MessageRole, content: str):
    async with session.begin():
        # Create message
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        session.add(message)

        # Update conversation timestamp
        conversation = await session.get(Conversation, conversation_id)
        conversation.updated_at = datetime.utcnow()

        await session.commit()
        return message
```

---

## Testing Strategy

### Unit Tests
- Model validation (field types, constraints)
- Enum values
- Default values
- Relationships

### Integration Tests
- Create conversation
- Add messages
- Retrieve history
- Update timestamps
- Archive conversations
- Cascade deletes
- Foreign key constraints
- Query performance

### Migration Tests
- Apply migrations
- Rollback migrations
- Data integrity after migration
- Index creation verification

---

## Performance Optimization

### Indexing Strategy
1. **User lookup**: `idx_conversations_user_id`
2. **Recent conversations**: `idx_conversations_updated_at`
3. **Filtered queries**: `idx_conversations_user_status`
4. **Message history**: `idx_messages_conversation_created` (composite)

### Connection Pooling
```python
# Database configuration
DATABASE_CONFIG = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600
}
```

### Query Optimization
- Always use LIMIT for message queries
- Use prepared statements (SQLModel default)
- Batch operations when possible
- Monitor slow query log

---

## Monitoring and Maintenance

### Metrics to Track
- Query latency (p50, p95, p99)
- Connection pool utilization
- Table sizes
- Index usage
- Slow queries

### Maintenance Tasks
- Daily: Monitor query performance
- Weekly: Review slow query log
- Monthly: Analyze table growth, optimize indexes
- Quarterly: Archive old conversations

---

## Risk Mitigation

### Risk 1: Migration Failure
**Mitigation**: Test migrations on staging, backup before production migration

### Risk 2: Performance Degradation
**Mitigation**: Proper indexing, connection pooling, query monitoring

### Risk 3: Data Loss
**Mitigation**: Foreign key constraints, transactions, regular backups

### Risk 4: Phase II Compatibility
**Mitigation**: Integration tests, no modifications to existing tables

---

## Deliverables

1. ✅ SQLModel models (conversation.py, message.py)
2. ✅ Alembic migrations (001, 002)
3. ✅ Repository layer (conversation_repository.py, message_repository.py)
4. ✅ Integration tests (test_database.py)
5. ✅ Documentation (this plan, README)

---

## Next Steps

1. Create tasks.md with detailed implementation tasks
2. Implement SQLModel models
3. Create and test migrations
4. Build repository layer
5. Write comprehensive tests
6. Deploy to staging and verify

---

**Plan Status**: Ready for task generation
**Estimated Effort**: 2-3 days for complete implementation and testing
