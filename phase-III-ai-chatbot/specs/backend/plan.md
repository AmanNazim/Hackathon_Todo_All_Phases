# Backend Implementation Plan: Phase III AI Chatbot API

**Date**: 2026-02-09
**Spec**: [spec.md](./spec.md)
**Component**: FastAPI Backend with Chat API and MCP Server

---

## Summary

Implement FastAPI backend with chat endpoint that uses OpenAI Agent and MCP tools to enable natural language task management. The system integrates with the existing database component and Phase II task system.

**Technical Approach**: Build FastAPI application with embedded MCP server, configure OpenAI Agent with 5 task management tools, implement single chat endpoint that handles conversation state and AI interactions.

---

## Technical Context

**Language**: Python 3.11+
**Framework**: FastAPI
**AI**: OpenAI Agents SDK (gpt-4o-mini)
**MCP**: Official MCP SDK (embedded in FastAPI)
**Database**: Existing database component (ConversationRepository, MessageRepository)
**Authentication**: Better Auth (Phase II integration)

**Performance Goals**:
- 95% of chat requests < 3 seconds
- MCP tool execution < 100ms
- Support 100+ concurrent users

**Constraints**:
- Stateless server architecture
- Must integrate with existing database component
- Must use Phase II task database
- User isolation enforced

---

## Project Structure

```
phase-III-ai-chatbot/backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py              # Chat endpoint
│   │   └── dependencies.py      # Auth dependencies
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py            # MCP server setup
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── delete_task.py
│   │       └── update_task.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── config.py            # Agent configuration
│   │   └── runner.py            # Agent execution
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py      # Chat business logic
│   │   └── task_service.py      # Task operations
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py              # Chat request/response models
│   │   └── task.py              # Task models
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Application settings
│   ├── models/                  # Database models (already exists)
│   ├── database/                # Database connection (already exists)
│   └── repositories/            # Repositories (already exists)
├── tests/
│   ├── test_mcp_tools.py
│   ├── test_chat_endpoint.py
│   └── test_agent.py
├── main.py                      # FastAPI application
└── requirements.txt             # Updated dependencies
```

---

## Implementation Tasks

### Task 1: Setup FastAPI Application
**Files**: `main.py`, `src/config/settings.py`
**Description**: Create FastAPI app with CORS, error handling, and configuration

### Task 2: Implement MCP Tools
**Files**: `src/mcp/tools/*.py`, `src/mcp/server.py`
**Description**: Implement 5 MCP tools for task operations

### Task 3: Configure OpenAI Agent
**Files**: `src/agent/config.py`, `src/agent/runner.py`
**Description**: Setup OpenAI Agent with MCP tools and system prompt

### Task 4: Implement Chat Service
**Files**: `src/services/chat_service.py`
**Description**: Business logic for handling chat requests

### Task 5: Implement Chat Endpoint
**Files**: `src/api/chat.py`, `src/schemas/chat.py`
**Description**: FastAPI endpoint for chat with authentication

### Task 6: Add Authentication
**Files**: `src/api/dependencies.py`
**Description**: Integrate Better Auth for user authentication

### Task 7: Write Tests
**Files**: `tests/*.py`
**Description**: Unit and integration tests for all components

### Task 8: Create Documentation
**Files**: `README.md`, `API.md`
**Description**: API documentation and usage guide

---

## MCP Tools Design

### Tool Structure

Each tool follows this pattern:

```python
async def tool_function(user_id: str, **params) -> dict:
    """
    Tool description for AI

    Args:
        user_id: User identifier
        **params: Tool-specific parameters

    Returns:
        Structured response dict
    """
    # 1. Validate parameters
    # 2. Execute database operation
    # 3. Return structured response
```

### Tool Schemas

Tools are registered with MCP server using JSON schema:

```python
{
    "name": "add_task",
    "description": "Create a new task for the user",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["user_id", "title"]
    }
}
```

---

## OpenAI Agent Configuration

### System Prompt

```
You are a helpful task management assistant. You help users manage their todo tasks through natural conversation.

CAPABILITIES:
- Create new tasks from user descriptions
- List tasks (all, pending, or completed)
- Mark tasks as complete
- Update task details
- Delete tasks

GUIDELINES:
- Extract task titles from natural language
- Ask for clarification when intent is ambiguous
- Confirm actions after completing them
- Be friendly and conversational

EXAMPLES:
User: "Add a task to buy groceries"
Action: Call add_task with title="Buy groceries"

User: "What do I need to do?"
Action: Call list_tasks with status="pending"

User: "I finished the report"
Action: Search for task matching "report", then call complete_task

When unsure, always ask for clarification rather than guessing.
```

### Agent Configuration

```python
agent = Agent(
    name="TaskManagementAgent",
    instructions=SYSTEM_PROMPT,
    tools=[add_task, list_tasks, complete_task, delete_task, update_task],
    model="gpt-4o-mini"
)
```

---

## Chat Flow

### Request Processing

1. **Receive Request**: POST /api/chat with conversation_id and message
2. **Authenticate**: Verify user token, extract user_id
3. **Validate**: Check message length, format
4. **Load/Create Conversation**: Get existing or create new conversation
5. **Load History**: Get last 20 messages for context
6. **Save User Message**: Store in database
7. **Run Agent**: Execute with history + new message
8. **Save AI Response**: Store in database
9. **Update Conversation**: Update timestamp
10. **Return Response**: Send conversation_id and AI response

### Stateless Design

- No in-memory session state
- All state in database
- Each request is independent
- Any server can handle any request

---

## Authentication Integration

### Better Auth Dependency

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Verify authentication token and extract user_id

    Args:
        token: JWT token from Authorization header

    Returns:
        user_id: Authenticated user identifier

    Raises:
        HTTPException: 401 if token invalid
    """
    # Verify token with Better Auth
    # Extract user_id from token payload
    # Return user_id
```

### Endpoint Protection

```python
@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    # user_id automatically injected from token
    # Use for all database operations
```

---

## Error Handling

### Error Response Format

```python
{
    "error": "error_code",
    "message": "Human-readable error message",
    "details": {}  # Optional additional context
}
```

### Error Types

- **400 Bad Request**: Invalid input (message too long, invalid format)
- **401 Unauthorized**: Missing or invalid authentication
- **404 Not Found**: Conversation not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error (logged, generic message to user)

---

## Testing Strategy

### Unit Tests
- MCP tool functions
- Agent configuration
- Chat service logic
- Request/response schemas

### Integration Tests
- Chat endpoint with authentication
- Full conversation flow
- Tool execution with database
- Error handling

### Test Coverage Target
- 80%+ code coverage
- All critical paths tested
- Error scenarios covered

---

## Performance Optimization

### Async Operations
- All database calls async
- Agent execution async
- No blocking operations

### Connection Pooling
- Database: 10 base, 20 max (already configured)
- HTTP client: Reuse connections

### Caching
- Agent configuration cached
- Tool schemas cached
- No conversation caching (stateless)

---

## Deployment Considerations

### Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Database (already configured)
DATABASE_URL=postgresql+asyncpg://...

# Application
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://frontend.com"]

# Authentication
AUTH_SECRET=...
AUTH_ISSUER=...
```

### Health Check

```python
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## Risk Mitigation

### Risk 1: OpenAI API Latency
**Mitigation**: Use gpt-4o-mini for speed, set timeout, show loading indicator

### Risk 2: Tool Execution Failures
**Mitigation**: Comprehensive error handling, graceful degradation, user-friendly messages

### Risk 3: Rate Limiting
**Mitigation**: Implement basic rate limiting, monitor usage, handle 429 errors

### Risk 4: Authentication Issues
**Mitigation**: Clear error messages, token refresh handling, fallback to login

---

## Next Steps

1. Create tasks.md with detailed implementation tasks
2. Implement FastAPI application and MCP tools
3. Configure OpenAI Agent
4. Implement chat endpoint
5. Add authentication
6. Write tests
7. Create documentation

---

**Plan Status**: Ready for task generation
**Estimated Effort**: 3-4 days for complete implementation and testing
