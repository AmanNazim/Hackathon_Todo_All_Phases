# Data Model: AI-Powered Conversational Task Management

**Date**: 2026-02-09
**Phase**: 1.1 (Data Model Design)
**Plan Reference**: [plan.md](./plan.md)

## Overview

This document defines the database schema for the conversational task management system. The schema extends Phase II's existing database with new tables for conversations and messages while maintaining compatibility with the existing tasks table.

---

## Database Schema

### New Tables

#### Conversations Table

**Purpose**: Store conversation metadata and status

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_conversations_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_conversation_status
        CHECK (status IN ('active', 'archived'))
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_conversations_user_status ON conversations(user_id, status);
```

**Fields**:
- `id` (UUID): Unique conversation identifier, auto-generated
- `user_id` (VARCHAR(255)): Reference to user from Phase II users table
- `status` (VARCHAR(20)): Conversation status (active, archived)
- `created_at` (TIMESTAMP): Conversation creation timestamp
- `updated_at` (TIMESTAMP): Last message timestamp

**Constraints**:
- Primary key on `id`
- Foreign key to `users.id` with CASCADE delete
- Check constraint on `status` enum values
- `created_at` <= `updated_at` (enforced at application level)

**Indexes**:
- `idx_conversations_user_id`: Fast lookup of user's conversations
- `idx_conversations_updated_at`: Recent conversations query
- `idx_conversations_user_status`: Filtered user conversations

#### Messages Table

**Purpose**: Store individual messages in conversations

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_messages_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_message_role
        CHECK (role IN ('user', 'assistant')),

    CONSTRAINT chk_user_message_length
        CHECK (role != 'user' OR length(content) <= 1000)
);

-- Indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
```

**Fields**:
- `id` (UUID): Unique message identifier, auto-generated
- `conversation_id` (UUID): Reference to parent conversation
- `user_id` (VARCHAR(255)): Reference to user (must match conversation.user_id)
- `role` (VARCHAR(20)): Message sender role (user, assistant)
- `content` (TEXT): Message text content
- `metadata` (JSONB): Optional metadata (tool calls, actions, etc.)
- `created_at` (TIMESTAMP): Message creation timestamp

**Constraints**:
- Primary key on `id`
- Foreign key to `conversations.id` with CASCADE delete
- Foreign key to `users.id` with CASCADE delete
- Check constraint on `role` enum values
- Check constraint on user message length (max 1000 characters)
- `user_id` must match `conversation.user_id` (enforced at application level)

**Indexes**:
- `idx_messages_conversation_id`: Fast lookup of conversation messages
- `idx_messages_created_at`: Recent messages query
- `idx_messages_conversation_created`: Composite index for ordered message retrieval (primary query pattern)

### Existing Tables (Phase II)

#### Tasks Table (Reference Only)

**Purpose**: Store user tasks (managed by Phase II, used by MCP tools)

```sql
-- Existing table from Phase II (reference only, not modified)
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_tasks_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_task_status
        CHECK (status IN ('pending', 'completed'))
);

-- Existing indexes from Phase II
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
```

**Note**: This table is not modified by Phase III. MCP tools interact with it through Phase II's task service layer.

---

## Entity Relationships

```
users (Phase II)
  │
  ├─── conversations (1:N)
  │      │
  │      └─── messages (1:N)
  │
  └─── tasks (1:N, Phase II)
```

**Relationships**:
1. **User → Conversations**: One user has many conversations
2. **Conversation → Messages**: One conversation has many messages
3. **User → Tasks**: One user has many tasks (Phase II relationship)

**No Direct Relationship**: Conversations and tasks are not directly linked. Tasks are referenced in message metadata when MCP tools are invoked.

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

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user123",
                "status": "active",
                "created_at": "2026-02-09T10:00:00Z",
                "updated_at": "2026-02-09T10:30:00Z"
            }
        }
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

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user123",
                "role": "user",
                "content": "Add a task to buy groceries",
                "metadata": None,
                "created_at": "2026-02-09T10:00:00Z"
            }
        }
```

### Task Model (Phase II Reference)

```python
# Existing model from Phase II (reference only)
class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
```

---

## Validation Rules

### Conversation Validation

1. **user_id**: Must reference existing user in users table
2. **status**: Must be 'active' or 'archived'
3. **created_at**: Must be <= updated_at
4. **State Transition**: active → archived (one-way, no reverse)

### Message Validation

1. **conversation_id**: Must reference existing conversation
2. **user_id**: Must match conversation.user_id
3. **role**: Must be 'user' or 'assistant'
4. **content**:
   - User messages: Max 1000 characters
   - Assistant messages: No length limit
   - Cannot be empty
5. **metadata**: Must be valid JSON if provided

### Task Validation (Phase II)

1. **user_id**: Must reference existing user
2. **title**: Required, non-empty
3. **status**: Must be 'pending' or 'completed'
4. **completed_at**: Must be set when status is 'completed'

---

## State Transitions

### Conversation States

```
┌────────┐
│ active │ ──────────────────────────────────┐
└────────┘                                    │
                                              │ archive
                                              ▼
                                        ┌──────────┐
                                        │ archived │
                                        └──────────┘
```

**Transitions**:
- **active → archived**: User archives conversation or automatic after 90 days
- **No reverse transition**: Archived conversations cannot be reactivated

### Message States

Messages are immutable once created. No state transitions.

### Task States (Phase II)

```
┌─────────┐
│ pending │ ──────────────────────────────────┐
└─────────┘                                    │
                                               │ complete
                                               ▼
                                         ┌───────────┐
                                         │ completed │
                                         └───────────┘
```

---

## Query Patterns

### Common Queries

#### Q1: Get User's Active Conversations
```sql
SELECT * FROM conversations
WHERE user_id = $1 AND status = 'active'
ORDER BY updated_at DESC
LIMIT 50;
```
**Index Used**: `idx_conversations_user_status`

#### Q2: Get Recent Messages for Conversation
```sql
SELECT * FROM messages
WHERE conversation_id = $1
ORDER BY created_at DESC
LIMIT 20;
```
**Index Used**: `idx_messages_conversation_created`

#### Q3: Get User's Pending Tasks
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND status = 'pending'
ORDER BY created_at DESC;
```
**Index Used**: `idx_tasks_user_status` (Phase II)

#### Q4: Update Conversation Timestamp
```sql
UPDATE conversations
SET updated_at = NOW()
WHERE id = $1;
```
**Index Used**: Primary key

#### Q5: Archive Old Conversations
```sql
UPDATE conversations
SET status = 'archived'
WHERE updated_at < NOW() - INTERVAL '90 days'
  AND status = 'active';
```
**Index Used**: `idx_conversations_updated_at`

---

## Data Retention

### Retention Policies

1. **Conversations**: 90 days from last update
   - After 90 days: Status changed to 'archived'
   - Archived conversations retained indefinitely (or per policy)
   - User can manually archive at any time

2. **Messages**: Cascade delete with conversation
   - When conversation deleted, all messages deleted
   - No independent message retention policy

3. **Tasks**: Managed by Phase II retention policy
   - Not affected by conversation retention

### Cleanup Strategy

**Background Job** (runs daily):
```python
async def archive_old_conversations():
    """Archive conversations older than 90 days"""
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    async with get_session() as session:
        result = await session.exec(
            update(Conversation)
            .where(Conversation.updated_at < cutoff_date)
            .where(Conversation.status == ConversationStatus.ACTIVE)
            .values(status=ConversationStatus.ARCHIVED)
        )
        return result.rowcount
```

---

## Migration Scripts

### Migration 001: Create Conversations Table

```python
"""create conversations table

Revision ID: 001_conversations
Revises: phase_ii_final
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('active', 'archived')", name='chk_conversation_status')
    )

    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_updated_at', 'conversations', ['updated_at'], postgresql_using='btree', postgresql_ops={'updated_at': 'DESC'})
    op.create_index('idx_conversations_user_status', 'conversations', ['user_id', 'status'])

def downgrade():
    op.drop_index('idx_conversations_user_status')
    op.drop_index('idx_conversations_updated_at')
    op.drop_index('idx_conversations_user_id')
    op.drop_table('conversations')
```

### Migration 002: Create Messages Table

```python
"""create messages table

Revision ID: 002_messages
Revises: 001_conversations
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='chk_message_role'),
        sa.CheckConstraint("role != 'user' OR length(content) <= 1000", name='chk_user_message_length')
    )

    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})

def downgrade():
    op.drop_index('idx_messages_conversation_created')
    op.drop_index('idx_messages_created_at')
    op.drop_index('idx_messages_conversation_id')
    op.drop_table('messages')
```

---

## Performance Considerations

### Index Strategy

1. **Composite Indexes**: Used for common query patterns (user_id + status, conversation_id + created_at)
2. **Descending Indexes**: Used for timestamp columns to optimize ORDER BY DESC queries
3. **Covering Indexes**: Consider adding covering indexes if specific queries become bottlenecks

### Query Optimization

1. **Limit Clauses**: Always use LIMIT for message history queries (default: 20)
2. **Connection Pooling**: Configure appropriate pool size (min: 5, max: 20)
3. **Prepared Statements**: Use parameterized queries for all database operations
4. **Batch Operations**: Batch insert messages when possible

### Scaling Considerations

1. **Read Replicas**: Consider read replicas for high read load
2. **Partitioning**: Partition messages table by created_at if volume exceeds 10M rows
3. **Archival**: Move archived conversations to separate table or cold storage
4. **Caching**: Consider Redis cache for active conversation metadata

---

## Testing Strategy

### Unit Tests

1. **Model Validation**: Test all validation rules
2. **State Transitions**: Test conversation status transitions
3. **Constraints**: Test database constraints (foreign keys, check constraints)
4. **Relationships**: Test SQLModel relationships

### Integration Tests

1. **CRUD Operations**: Test create, read, update, delete for all entities
2. **Query Performance**: Test query performance with realistic data volumes
3. **Concurrent Access**: Test concurrent message creation
4. **Transaction Rollback**: Test error handling and rollback

### Data Migration Tests

1. **Migration Up**: Test migration applies successfully
2. **Migration Down**: Test migration rollback
3. **Data Integrity**: Test existing Phase II data unaffected

---

## Summary

**New Tables**: 2 (conversations, messages)
**Modified Tables**: 0 (Phase II tables unchanged)
**New Indexes**: 6 (3 per new table)
**Foreign Keys**: 4 (2 per new table)
**Enums**: 2 (ConversationStatus, MessageRole)

**Ready for**: API contract generation and implementation

**Next Steps**:
1. Generate API contracts (chat-api.yaml, mcp-tools.json)
2. Implement SQLModel models
3. Create Alembic migrations
4. Write model tests
