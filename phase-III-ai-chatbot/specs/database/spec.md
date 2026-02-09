# Database Specification: Phase III AI Chatbot Conversation Storage

**Version**: 1.0
**Status**: Draft
**Created**: 2026-02-09
**Component**: Database Schema for Conversations and Messages

---

## Overview

### Purpose
Provide persistent storage for AI chatbot conversations and messages, enabling stateless server architecture with conversation history retrieval.

### Business Value
- **Conversation Persistence**: Users can resume conversations after closing the app
- **Stateless Architecture**: Any server instance can handle any request
- **Audit Trail**: Complete history of user interactions with AI
- **Scalability**: Database-backed state enables horizontal scaling

### Scope
This specification covers database schema for:
- Conversations (chat sessions)
- Messages (individual chat messages)
- Integration with existing Phase II tasks table

---

## Requirements

### Functional Requirements

#### FR1: Store Conversations
- System must create new conversation when user starts chat
- System must associate conversation with authenticated user
- System must track conversation creation and last update time
- System must support conversation status (active, archived)

**Acceptance Criteria**:
- Conversation has unique identifier
- Conversation linked to user account
- Timestamps automatically set on creation and update
- Status can be active or archived

#### FR2: Store Messages
- System must store all user and assistant messages
- System must link messages to parent conversation
- System must record message role (user or assistant)
- System must store message content and timestamp
- System must optionally store metadata (tool calls, actions)

**Acceptance Criteria**:
- Message has unique identifier
- Message linked to conversation and user
- Role clearly identifies sender
- Content stored as text
- Metadata stored as JSON when present

#### FR3: Retrieve Conversation History
- System must retrieve messages for a conversation in chronological order
- System must support limiting number of messages retrieved
- System must efficiently query recent conversations for a user

**Acceptance Criteria**:
- Messages returned in creation order
- Query supports LIMIT clause
- User's conversations retrievable by user_id
- Query performance acceptable (<100ms p95)

#### FR4: Update Conversation Timestamp
- System must update conversation's updated_at when new message added
- System must maintain accurate last activity time

**Acceptance Criteria**:
- updated_at reflects latest message time
- Timestamp updates automatically

#### FR5: Archive Old Conversations
- System must support archiving conversations older than 90 days
- System must preserve archived conversation data
- System must allow manual archiving by user

**Acceptance Criteria**:
- Conversations can transition from active to archived
- Archived conversations retained in database
- Archive operation is reversible (if needed)

#### FR6: Integrate with Phase II Tasks
- System must reference existing tasks table
- System must not modify Phase II task schema
- System must support task operations through existing table

**Acceptance Criteria**:
- No changes to tasks table structure
- Foreign key references to users table work correctly
- Task queries unaffected by new tables

---

## Data Entities

### Conversation
**Purpose**: Represents a chat session between user and AI

**Attributes**:
- Unique identifier (UUID)
- User identifier (links to Phase II users)
- Status (active or archived)
- Creation timestamp
- Last update timestamp

**Relationships**:
- Belongs to one User
- Has many Messages

### Message
**Purpose**: Represents a single message in a conversation

**Attributes**:
- Unique identifier (UUID)
- Conversation identifier (links to parent conversation)
- User identifier (links to Phase II users)
- Role (user or assistant)
- Content (message text)
- Metadata (optional JSON for tool calls)
- Creation timestamp

**Relationships**:
- Belongs to one Conversation
- Belongs to one User

### Task (Existing - Phase II)
**Purpose**: Represents a todo task (not modified)

**Attributes**:
- Unique identifier (UUID)
- User identifier
- Title
- Description (optional)
- Status (pending or completed)
- Timestamps

**Relationships**:
- Belongs to one User
- Referenced by MCP tools (no direct FK from messages)

---

## Success Criteria

### Performance Metrics
1. **Query Latency**: 95% of conversation history queries complete in <100ms
2. **Write Latency**: 95% of message inserts complete in <50ms
3. **Concurrent Users**: Support 100+ concurrent database connections
4. **Data Volume**: Handle 1M+ messages without performance degradation

### Data Integrity Metrics
1. **Referential Integrity**: 100% of foreign key constraints enforced
2. **Data Consistency**: Zero orphaned messages or conversations
3. **Constraint Violations**: All check constraints enforced at database level

### Operational Metrics
1. **Backup Success**: Daily backups complete successfully
2. **Migration Success**: Schema migrations apply without data loss
3. **Index Efficiency**: All queries use appropriate indexes

---

## Constraints

### Technical Constraints
1. **Database**: Must use Neon Serverless PostgreSQL (from Phase II)
2. **User Messages**: Maximum 1000 characters
3. **Assistant Messages**: No length limit
4. **Conversation Limit**: 50 active conversations per user
5. **Retention**: 90 days for active conversations

### Integration Constraints
1. **Phase II Compatibility**: Must not break existing Phase II functionality
2. **User Table**: Must reference existing users table
3. **Task Table**: Must not modify existing tasks table
4. **Schema Naming**: Follow Phase II naming conventions

---

## Out of Scope

The following are explicitly excluded:
1. **Full-Text Search**: Advanced search across message content
2. **Message Editing**: Modifying messages after creation
3. **Message Deletion**: Individual message deletion (cascade only)
4. **Conversation Sharing**: Multi-user conversations
5. **Message Reactions**: Likes, reactions, or annotations
6. **Read Receipts**: Message read status tracking
7. **Typing Indicators**: Real-time typing status (handled at application level)
8. **Message Attachments**: File or image storage

---

## Edge Cases

### Edge Case 1: Orphaned Messages
**Scenario**: Conversation deleted while messages exist
**Expected Behavior**: CASCADE delete removes all messages

### Edge Case 2: User Deletion
**Scenario**: User account deleted
**Expected Behavior**: CASCADE delete removes conversations and messages

### Edge Case 3: Concurrent Message Creation
**Scenario**: Multiple messages created simultaneously for same conversation
**Expected Behavior**: All messages saved, updated_at reflects latest

### Edge Case 4: Very Long Conversations
**Scenario**: Conversation with 1000+ messages
**Expected Behavior**: Queries remain performant with proper indexing

### Edge Case 5: Message Length Violation
**Scenario**: User message exceeds 1000 characters
**Expected Behavior**: Database constraint rejects insert, application handles error

---

## Security Considerations

### Data Access
1. **User Isolation**: Users can only access their own conversations
2. **Authentication Required**: All database access through authenticated API
3. **SQL Injection Prevention**: Parameterized queries only

### Data Privacy
1. **Data Encryption**: Database encryption at rest (Neon default)
2. **Connection Security**: TLS for all database connections
3. **Audit Logging**: Log all schema changes and admin access

---

## Acceptance Testing Scenarios

### Test Scenario 1: Create Conversation
**Given**: Authenticated user
**When**: New conversation created
**Then**: Conversation record exists with user_id, active status, and timestamps

### Test Scenario 2: Add Messages
**Given**: Existing conversation
**When**: User and assistant messages added
**Then**: Messages stored with correct role, content, and timestamps

### Test Scenario 3: Retrieve History
**Given**: Conversation with 50 messages
**When**: Request last 20 messages
**Then**: 20 most recent messages returned in chronological order

### Test Scenario 4: Archive Conversation
**Given**: Active conversation older than 90 days
**When**: Archive operation executed
**Then**: Conversation status changed to archived

### Test Scenario 5: Cascade Delete
**Given**: Conversation with 10 messages
**When**: Conversation deleted
**Then**: All 10 messages also deleted

### Test Scenario 6: Foreign Key Enforcement
**Given**: Attempt to create message with invalid conversation_id
**When**: Insert executed
**Then**: Database rejects insert with foreign key error

---

## Notes

- Schema designed for stateless server architecture
- Indexes optimized for common query patterns
- Compatible with Phase II database structure
- Supports future enhancements (search, analytics)

---

**Document Status**: Ready for planning phase
