# Backend Specification: Phase III AI Chatbot API

**Version**: 1.0
**Status**: Draft
**Created**: 2026-02-09
**Component**: FastAPI Backend with Chat API and MCP Server

---

## Overview

### Purpose
Provide a FastAPI backend that enables users to manage tasks through natural language conversations with an AI assistant.

### Business Value
- **Natural Interaction**: Users manage tasks by chatting instead of clicking buttons
- **AI-Powered**: Intelligent understanding of user intent
- **Stateless Design**: Scalable architecture with database-persisted state
- **Tool-Based**: Standardized MCP tools for task operations

### Scope
This specification covers:
- Chat API endpoint for conversation handling
- MCP server with 5 task management tools
- OpenAI Agent integration for natural language understanding
- Authentication and authorization
- Integration with database component (already implemented)

---

## Requirements

### Functional Requirements

#### FR1: Chat Endpoint
- System must provide POST /api/chat endpoint
- System must accept conversation_id (optional) and message (required)
- System must create new conversation if conversation_id not provided
- System must authenticate user before processing request
- System must return AI response with conversation_id

**Acceptance Criteria**:
- Endpoint accepts JSON with conversation_id and message
- New conversation created when conversation_id is null
- User authentication verified
- Response includes conversation_id and AI response text

#### FR2: Natural Language Task Creation
- System must understand user intent to create tasks
- System must extract task title from natural language
- System must call add_task MCP tool
- System must confirm task creation to user

**Acceptance Criteria**:
- User can say "Add task to buy groceries" and task is created
- Task title extracted correctly
- Confirmation message returned

#### FR3: Natural Language Task Listing
- System must understand requests to view tasks
- System must call list_tasks MCP tool with appropriate filter
- System must format task list in readable response

**Acceptance Criteria**:
- User can say "Show my tasks" and see task list
- Filters work for "pending" and "completed"
- Response is user-friendly

#### FR4: Natural Language Task Completion
- System must identify task to mark complete
- System must call complete_task MCP tool
- System must confirm completion

**Acceptance Criteria**:
- User can say "I finished the groceries task" and task marked complete
- Task identified correctly
- Confirmation returned

#### FR5: Natural Language Task Deletion
- System must identify task to delete
- System must call delete_task MCP tool
- System must confirm deletion

**Acceptance Criteria**:
- User can say "Delete the meeting task" and task deleted
- Confirmation returned

#### FR6: Natural Language Task Updates
- System must identify task to update
- System must extract new title or description
- System must call update_task MCP tool
- System must confirm update

**Acceptance Criteria**:
- User can say "Change meeting task to team meeting" and task updated
- New values extracted correctly
- Confirmation returned

#### FR7: Conversation History Management
- System must load conversation history from database
- System must include history in AI context
- System must save new messages to database
- System must update conversation timestamp

**Acceptance Criteria**:
- Previous messages loaded when conversation continues
- AI has context from history
- New messages persisted
- Conversation updated_at reflects latest message

#### FR8: MCP Tools Implementation
- System must implement 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- Each tool must have proper schema definition
- Tools must interact with Phase II task database
- Tools must return structured responses

**Acceptance Criteria**:
- All 5 tools implemented
- Tool schemas match MCP specification
- Tools work with existing task database
- Responses follow defined format

---

## API Specification

### Chat Endpoint

**POST /api/chat**

**Request**:
```json
{
  "conversation_id": "uuid | null",
  "message": "string (max 1000 chars)"
}
```

**Response**:
```json
{
  "conversation_id": "uuid",
  "response": "string",
  "created_at": "timestamp"
}
```

**Error Responses**:
- 400: Invalid request (message too long, invalid format)
- 401: Unauthorized (missing or invalid authentication)
- 429: Rate limit exceeded
- 500: Internal server error

---

## MCP Tools Specification

### Tool 1: add_task

**Purpose**: Create a new task

**Parameters**:
- user_id (string, required)
- title (string, required)
- description (string, optional)

**Returns**:
```json
{
  "task_id": "string",
  "status": "created",
  "title": "string"
}
```

### Tool 2: list_tasks

**Purpose**: Retrieve user's tasks

**Parameters**:
- user_id (string, required)
- status (string, optional: "all", "pending", "completed")

**Returns**:
```json
[
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "status": "string",
    "created_at": "string"
  }
]
```

### Tool 3: complete_task

**Purpose**: Mark task as completed

**Parameters**:
- user_id (string, required)
- task_id (string, required)

**Returns**:
```json
{
  "task_id": "string",
  "status": "completed",
  "title": "string"
}
```

### Tool 4: delete_task

**Purpose**: Delete a task

**Parameters**:
- user_id (string, required)
- task_id (string, required)

**Returns**:
```json
{
  "task_id": "string",
  "status": "deleted",
  "title": "string"
}
```

### Tool 5: update_task

**Purpose**: Update task title or description

**Parameters**:
- user_id (string, required)
- task_id (string, required)
- title (string, optional)
- description (string, optional)

**Returns**:
```json
{
  "task_id": "string",
  "status": "updated",
  "title": "string"
}
```

---

## Success Criteria

### Performance Metrics
1. **Response Time**: 95% of chat requests complete in <3 seconds
2. **Tool Execution**: MCP tools execute in <100ms
3. **Concurrent Users**: Support 100+ concurrent chat sessions
4. **Error Rate**: <1% of requests result in 500 errors

### Quality Metrics
1. **Intent Accuracy**: AI correctly interprets 90% of task management commands
2. **Tool Success Rate**: 99% of tool calls succeed
3. **Data Consistency**: 100% of messages persisted correctly

---

## Constraints

### Technical Constraints
1. **Framework**: Must use FastAPI
2. **AI**: Must use OpenAI Agents SDK
3. **MCP**: Must use Official MCP SDK
4. **Database**: Must use existing database component
5. **Authentication**: Must integrate with Phase II Better Auth

### Business Constraints
1. **Stateless**: Server must be stateless (no in-memory session state)
2. **User Isolation**: Users can only access their own tasks and conversations
3. **Message Length**: User messages limited to 1000 characters

---

## Out of Scope

The following are explicitly excluded:
1. **Streaming Responses**: Real-time streaming of AI responses
2. **Voice Input**: Speech-to-text processing
3. **Multi-Language**: Languages other than English
4. **Advanced Task Features**: Subtasks, dependencies, recurring tasks
5. **File Uploads**: Attachment handling
6. **Custom Commands**: User-defined shortcuts
7. **Analytics**: Usage tracking and metrics dashboard
8. **Rate Limiting**: Advanced rate limiting (basic only)

---

## Edge Cases

### Edge Case 1: Empty Message
**Scenario**: User sends empty message
**Expected Behavior**: Return 400 error with helpful message

### Edge Case 2: Very Long Message
**Scenario**: User message exceeds 1000 characters
**Expected Behavior**: Return 400 error indicating limit

### Edge Case 3: Invalid Conversation ID
**Scenario**: User provides non-existent conversation_id
**Expected Behavior**: Return 404 error

### Edge Case 4: Ambiguous Task Reference
**Scenario**: User says "delete the task" but has multiple tasks
**Expected Behavior**: AI asks for clarification

### Edge Case 5: No Tasks Found
**Scenario**: User asks to list tasks but has none
**Expected Behavior**: AI responds with friendly "no tasks" message

### Edge Case 6: Tool Execution Failure
**Scenario**: MCP tool fails (e.g., database error)
**Expected Behavior**: AI responds with error message, conversation continues

### Edge Case 7: Concurrent Requests
**Scenario**: User sends multiple messages rapidly
**Expected Behavior**: Requests processed in order, no data loss

---

## Security Considerations

### Authentication
1. **Required**: All requests must include valid authentication token
2. **User Context**: Extract user_id from authentication token
3. **Token Validation**: Verify token with Better Auth

### Authorization
1. **Conversation Access**: Users can only access their own conversations
2. **Task Access**: Users can only manage their own tasks
3. **Data Isolation**: Enforce user_id filtering in all queries

### Input Validation
1. **Message Length**: Validate max 1000 characters
2. **Conversation ID**: Validate UUID format
3. **SQL Injection**: Use parameterized queries (handled by ORM)
4. **XSS Prevention**: Sanitize user input

---

## Integration Points

### Database Component (Completed)
- Use ConversationRepository for conversation operations
- Use MessageRepository for message operations
- Use existing database connection

### Phase II Task System
- Access tasks table through existing models
- Maintain compatibility with Phase II task operations
- No modifications to Phase II schema

### Authentication System
- Integrate with Better Auth middleware
- Extract user_id from JWT token
- Validate authentication on all endpoints

---

## Acceptance Testing Scenarios

### Test Scenario 1: Create Task via Chat
**Given**: Authenticated user with no tasks
**When**: User sends "Add task to buy milk"
**Then**: Task created, confirmation returned, message saved

### Test Scenario 2: List Tasks via Chat
**Given**: User has 3 pending tasks
**When**: User sends "Show my tasks"
**Then**: AI lists 3 tasks in readable format

### Test Scenario 3: Complete Task via Chat
**Given**: User has task "Buy milk"
**When**: User sends "I bought the milk"
**Then**: Task marked complete, confirmation returned

### Test Scenario 4: Continue Conversation
**Given**: Existing conversation with 5 messages
**When**: User sends new message with conversation_id
**Then**: History loaded, AI has context, new message added

### Test Scenario 5: Unauthorized Access
**Given**: Request without authentication token
**When**: POST to /api/chat
**Then**: 401 error returned

### Test Scenario 6: Invalid Message
**Given**: Authenticated user
**When**: User sends message with 1500 characters
**Then**: 400 error with length limit message

---

## Notes

- Focus on core chat and task management functionality
- Keep AI prompts simple and effective
- Ensure proper error handling throughout
- Maintain stateless architecture
- All operations must be async

---

**Document Status**: Ready for planning phase
