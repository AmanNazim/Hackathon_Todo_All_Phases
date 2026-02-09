# Phase III AI Chatbot - API Documentation

## Overview

The Phase III AI Chatbot API provides a conversational interface for managing todo tasks through natural language. The API uses OpenAI's GPT-4o-mini model with MCP (Model Context Protocol) tools to understand user intent and perform task operations.

## Base URL

```
http://localhost:8000
```

## Authentication

All API endpoints (except `/health` and `/`) require authentication via Bearer token.

### Authentication Header

```
Authorization: Bearer <your-token>
```

### Example

```bash
curl -H "Authorization: Bearer your-token-here" \
     http://localhost:8000/api/chat
```

---

## Endpoints

### Health Check

Check if the API is running.

**Endpoint**: `GET /health`

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "service": "phase-iii-chatbot"
}
```

---

### Root

Get API information.

**Endpoint**: `GET /`

**Authentication**: Not required

**Response**:
```json
{
  "message": "Phase III AI Chatbot API",
  "version": "1.0",
  "docs": "/docs"
}
```

---

### Chat

Send a message to the AI chatbot for task management.

**Endpoint**: `POST /api/chat`

**Authentication**: Required

**Request Body**:
```json
{
  "conversation_id": "uuid | null",
  "message": "string (1-1000 characters)"
}
```

**Parameters**:
- `conversation_id` (optional): UUID of existing conversation. If not provided, a new conversation is created.
- `message` (required): User's message text. Must be 1-1000 characters.

**Response**:
```json
{
  "conversation_id": "string (uuid)",
  "response": "string",
  "created_at": "string (ISO 8601 timestamp)"
}
```

**Status Codes**:
- `200 OK`: Success
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Conversation not found or access denied
- `422 Unprocessable Entity`: Invalid request (message too long, invalid format)
- `500 Internal Server Error`: Server error

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

**Example Response**:
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "response": "I've added 'Buy groceries' to your tasks.",
  "created_at": "2026-02-09T10:30:00.000Z"
}
```

---

### Streaming Endpoint

**POST /api/chat/stream**

Stream chat responses in real-time using Server-Sent Events (SSE).

**Endpoint**: `POST /api/chat/stream`

**Authentication**: Required

**Request Body**: Same as `/api/chat`
```json
{
  "conversation_id": "uuid | null",
  "message": "string (1-1000 characters)"
}
```

**Response**: Server-Sent Events (SSE) stream

**Event Types**:

1. **text** - Partial response text
```
event: text
data: {"text": "I've added"}
```

2. **tool_call** - Tool execution notification
```
event: tool_call
data: {"tool": "add_task_tool", "status": "running"}
```

3. **complete** - Stream completion
```
event: complete
data: {"conversation_id": "uuid", "created_at": "timestamp"}
```

4. **error** - Error during streaming
```
event: error
data: {"error": "error message"}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}' \
  --no-buffer
```

**Example Response Stream**:
```
event: text
data: {"text": "I've"}

event: text
data: {"text": " added"}

event: tool_call
data: {"tool": "add_task_tool", "status": "running"}

event: text
data: {"text": " 'Buy groceries' to your tasks."}

event: complete
data: {"conversation_id": "123e4567-e89b-12d3-a456-426614174000", "created_at": "2026-02-09T10:30:00.000Z"}
```

**Status Codes**:
- `200 OK`: Stream started successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Access denied
- `422 Unprocessable Entity`: Invalid request (message validation failed)

**Notes**:
- Connection stays open until stream completes
- Client should handle reconnection if connection drops
- Use `Cache-Control: no-cache` header to prevent caching
- Ideal for real-time UI updates

---

## Natural Language Commands

The chatbot understands various natural language commands for task management:

### Create Task

**Examples**:
- "Add a task to buy milk"
- "Create a task for the meeting"
- "Remind me to call mom"
- "I need to finish the report"

**AI Action**: Calls `add_task` MCP tool

---

### List Tasks

**Examples**:
- "Show my tasks"
- "What do I need to do?"
- "List all tasks"
- "Show pending tasks"
- "What have I completed?"

**AI Action**: Calls `list_tasks` MCP tool with appropriate filter

---

### Complete Task

**Examples**:
- "I finished the groceries"
- "Mark the report task as done"
- "Completed the meeting"

**AI Action**: Calls `complete_task` MCP tool

---

### Update Task

**Examples**:
- "Change the meeting task to team meeting"
- "Update task 1 to include agenda"
- "Rename the report task"

**AI Action**: Calls `update_task` MCP tool

---

### Delete Task

**Examples**:
- "Delete the old task"
- "Remove the meeting task"
- "Cancel the report task"

**AI Action**: Calls `delete_task` MCP tool

---

## MCP Tools

The AI agent uses the following MCP tools to perform task operations:

### add_task

Create a new task.

**Parameters**:
- `user_id` (string, required): User identifier
- `title` (string, required): Task title
- `description` (string, optional): Task description

**Returns**:
```json
{
  "task_id": "string",
  "status": "created",
  "title": "string"
}
```

---

### list_tasks

List user's tasks.

**Parameters**:
- `user_id` (string, required): User identifier
- `status` (string, optional): Filter by status ("all", "pending", "completed")

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

---

### complete_task

Mark task as completed.

**Parameters**:
- `user_id` (string, required): User identifier
- `task_id` (string, required): Task identifier

**Returns**:
```json
{
  "task_id": "string",
  "status": "completed",
  "title": "string"
}
```

---

### delete_task

Delete a task.

**Parameters**:
- `user_id` (string, required): User identifier
- `task_id` (string, required): Task identifier

**Returns**:
```json
{
  "task_id": "string",
  "status": "deleted",
  "title": "string"
}
```

---

### update_task

Update task title or description.

**Parameters**:
- `user_id` (string, required): User identifier
- `task_id` (string, required): Task identifier
- `title` (string, optional): New task title
- `description` (string, optional): New task description

**Returns**:
```json
{
  "task_id": "string",
  "status": "updated",
  "title": "string"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message"
}
```

### Common Errors

**401 Unauthorized**:
```json
{
  "detail": "Invalid authentication credentials"
}
```

**404 Not Found**:
```json
{
  "detail": "Conversation not found or access denied"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "ensure this value has at most 1000 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error. Please try again."
}
```

---

## Rate Limiting

Currently, no rate limiting is enforced. In production, implement rate limiting to prevent abuse.

**Recommended Limits**:
- 10 requests per minute per user
- 100 requests per hour per user

---

## Agent SDK Architecture

### Components

The API uses OpenAI Agents SDK with the following components:

1. **Agent Service** (`src/agent_sdk/agent_service.py`)
   - Creates and configures the Task Management Agent
   - Sets model parameters (gpt-4o-mini, temperature=0.7)
   - Configures guardrails and max iterations

2. **Session Service** (`src/agent_sdk/session_service.py`)
   - Manages SQLite sessions for conversation persistence
   - Automatic conversation history tracking
   - Session stored in `data/sessions.db`

3. **Tool Adapter** (`src/agent_sdk/tool_adapter.py`)
   - Converts MCP tools to SDK function tools
   - Injects user_id context automatically
   - Maintains tool registry

4. **Guardrails** (`src/agent_sdk/guardrails.py`)
   - Input validation (message length, content safety)
   - Output quality checks
   - Runs in parallel for best latency

5. **Runner Service** (`src/agent_sdk/runner_service.py`)
   - Executes agents using `Runner.run()` and `Runner.run_streamed()`
   - Handles errors and max turns exceeded
   - Provides retry logic

### Data Flow

```
User Request → API Endpoint → Input Guardrail → Agent Service
                                                      ↓
                                                 Runner.run()
                                                      ↓
                                    Agent → Tools → MCP Functions
                                      ↓
                                Output Guardrail → Response
                                      ↓
                                Session Storage (SQLite)
```

### Session Management

Sessions are automatically managed by the SDK:
- **New Conversation**: Creates new UUID and SQLite session
- **Existing Conversation**: Loads session by conversation_id
- **History**: Last 20 messages automatically included in context
- **Persistence**: All messages stored in `data/sessions.db`

### Guardrails

**Input Guardrails** (run in parallel):
- Message length validation (1-1000 characters)
- Empty message check
- Content safety check (basic)

**Output Guardrails**:
- Response quality validation
- Minimum length check (5+ characters)
- Empty response prevention

## Development

### Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Create data directory for sessions
mkdir -p data

# Run server
uvicorn main:app --reload
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Examples

### Complete Conversation Flow

```bash
# 1. Create new conversation and add task
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task to buy milk"}'

# Response:
# {
#   "conversation_id": "abc-123",
#   "response": "I've added 'Buy milk' to your tasks.",
#   "created_at": "2026-02-09T10:00:00Z"
# }

# 2. Continue conversation - list tasks
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "abc-123",
    "message": "Show my tasks"
  }'

# Response:
# {
#   "conversation_id": "abc-123",
#   "response": "Here are your tasks:\n1. Buy milk (pending)",
#   "created_at": "2026-02-09T10:01:00Z"
# }

# 3. Complete task
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "abc-123",
    "message": "I bought the milk"
  }'

# Response:
# {
#   "conversation_id": "abc-123",
#   "response": "Great! I've marked 'Buy milk' as complete.",
#   "created_at": "2026-02-09T10:02:00Z"
# }
```

---

## Security Considerations

1. **Authentication**: Always use HTTPS in production
2. **Token Storage**: Store tokens securely, never in client-side code
3. **Input Validation**: All inputs are validated server-side
4. **Rate Limiting**: Implement rate limiting in production
5. **CORS**: Configure CORS origins appropriately for your frontend

---

## Troubleshooting

### Common Issues

**Issue**: "Failed to create/retrieve session"
- **Solution**: Ensure `data/` directory exists and is writable
- **Command**: `mkdir -p data && chmod 755 data`

**Issue**: "Maximum turns exceeded"
- **Solution**: Request is too complex, break into smaller parts
- **Note**: Agent has max_iterations=10 to prevent infinite loops

**Issue**: Streaming connection drops
- **Solution**: Implement reconnection logic in client
- **Note**: Use last conversation_id to resume

**Issue**: Guardrail validation fails
- **Solution**: Check message length (1-1000 chars) and content
- **Response**: Error message indicates specific validation failure

### Performance Tips

1. **Use Streaming**: For better UX, use `/api/chat/stream` endpoint
2. **Session Reuse**: Always pass conversation_id to maintain context
3. **Message Length**: Keep messages concise for faster processing
4. **Concurrent Requests**: API supports multiple concurrent conversations

### Monitoring

The Agent SDK includes usage tracking:
- Token usage automatically tracked with `include_usage=True`
- Check logs for agent execution metrics
- Monitor session database size in `data/sessions.db`

## Support

For issues or questions:
- Check the interactive docs at `/docs`
- Review the backend README
- Check the specification documents
- Review Agent SDK documentation: https://openai.github.io/openai-agents-python/

---

**Version**: 2.0 (Agent SDK)
**Last Updated**: 2026-02-09
**Agent SDK Version**: 0.1.0+
