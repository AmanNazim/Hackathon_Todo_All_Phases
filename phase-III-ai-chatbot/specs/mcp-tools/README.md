# MCP Tools Documentation

## Overview

The MCP (Model Context Protocol) tools provide task management capabilities to AI agents through a standardized interface. The tools are implemented using **FastMCP** (Python MCP SDK) and expose 5 core operations through STDIO transport.

## Implementation

### FastMCP Server

The MCP server is implemented in `backend/mcp_server.py` using FastMCP:

```python
from fastmcp import FastMCP

mcp = FastMCP("Task Management Server")

@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user."""
    # Implementation

if __name__ == "__main__":
    mcp.run()  # Runs with STDIO transport
```

### Key Features

- **FastMCP Decorators**: Tools use `@mcp.tool()` decorator for automatic registration
- **Type Hints**: Automatic schema generation from Python type hints
- **STDIO Transport**: Communication via standard input/output
- **Logging to stderr**: All logs go to stderr (STDIO constraint)
- **Error Handling**: Comprehensive error handling with clear messages

## Running the Server

```bash
# From backend directory
cd phase-III-ai-chatbot/backend

# Run the MCP server
python mcp_server.py
```

## Testing

### With MCP Inspector

```bash
npx @modelcontextprotocol/inspector python mcp_server.py
```

See [TESTING.md](TESTING.md) for complete testing guide.

## Available Tools

### 1. add_task

**Purpose**: Create a new task for a user

**Parameters**:
- `user_id` (string, required) - User identifier
- `title` (string, required) - Task title
- `description` (string, optional) - Task description

**Returns**:
```json
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries"
}
```

**Example Usage**:
```python
result = await add_task(
    user_id="ziakhan",
    title="Buy groceries",
    description="Milk, eggs, bread"
)
```

**Natural Language Triggers**:
- "Add a task to buy groceries"
- "I need to remember to pay bills"
- "Create a task for calling mom"

---

### 2. list_tasks

**Purpose**: Retrieve tasks from the user's list

**Parameters**:
- `user_id` (string, required) - User identifier
- `status` (string, optional) - Filter: "all", "pending", "completed" (default: "all")

**Returns**:
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "completed": false
  }
]
```

**Example Usage**:
```python
# List all tasks
tasks = await list_tasks(user_id="ziakhan", status="all")

# List only pending tasks
pending = await list_tasks(user_id="ziakhan", status="pending")
```

**Natural Language Triggers**:
- "Show me all my tasks"
- "What's pending?"
- "List my completed tasks"

---

### 3. complete_task

**Purpose**: Mark a task as complete

**Parameters**:
- `user_id` (string, required) - User identifier
- `task_id` (integer, required) - Task ID to complete

**Returns**:
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

**Example Usage**:
```python
result = await complete_task(user_id="ziakhan", task_id=3)
```

**Natural Language Triggers**:
- "Mark task 3 as complete"
- "I finished the groceries task"
- "Task 5 is done"

---

### 4. delete_task

**Purpose**: Remove a task from the list

**Parameters**:
- `user_id` (string, required) - User identifier
- `task_id` (integer, required) - Task ID to delete

**Returns**:
```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

**Example Usage**:
```python
result = await delete_task(user_id="ziakhan", task_id=2)
```

**Natural Language Triggers**:
- "Delete the meeting task"
- "Remove task 2"
- "Cancel that task"

---

### 5. update_task

**Purpose**: Modify task title or description

**Parameters**:
- `user_id` (string, required) - User identifier
- `task_id` (integer, required) - Task ID to update
- `title` (string, optional) - New task title
- `description` (string, optional) - New task description

**Returns**:
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

**Example Usage**:
```python
result = await update_task(
    user_id="ziakhan",
    task_id=1,
    title="Buy groceries and fruits"
)
```

**Natural Language Triggers**:
- "Change task 1 to 'Call mom tonight'"
- "Update the description of task 3"
- "Rename task 5"

---

## Agent Integration

The MCP tools are automatically available to the AI agent through the Agent SDK integration. The agent understands natural language commands and maps them to appropriate tool calls.

### Conversation Flow

1. User sends message to agent
2. Agent analyzes intent and extracts parameters
3. Agent calls appropriate MCP tool
4. Tool executes and returns structured response
5. Agent formats response for user
6. Agent provides friendly confirmation

### Example Conversation

**User**: "Add a task to buy groceries"

**Agent Process**:
1. Identifies intent: create task
2. Extracts parameters: title="Buy groceries"
3. Calls: `add_task(user_id="current_user", title="Buy groceries")`
4. Receives: `{"task_id": 5, "status": "created", "title": "Buy groceries"}`
5. Responds: "I've added 'Buy groceries' to your task list (Task #5)"

---

## Error Handling

All tools handle errors gracefully and return clear messages:

### Task Not Found
```python
# Raises ValueError
ValueError: "Task 123 not found"
```

### Permission Error
```python
# Raises ValueError
ValueError: "Task 123 does not belong to user ziakhan"
```

### Missing Parameters
```python
# Handled by MCP schema validation
# Returns error before tool execution
```

---

## Testing

### Manual Testing with MCP Inspector

```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector

# Test the MCP server
npx @modelcontextprotocol/inspector python backend/src/mcp/server.py
```

### Testing Individual Tools

```python
import asyncio
from src.mcp.tools.add_task import add_task

async def test_add_task():
    result = await add_task(
        user_id="test_user",
        title="Test Task",
        description="This is a test"
    )
    print(result)

asyncio.run(test_add_task())
```

---

## Implementation Details

### File Structure

```
backend/src/mcp/
├── __init__.py
├── server.py              # MCP tools registry
└── tools/
    ├── __init__.py
    ├── add_task.py        # Create task tool
    ├── list_tasks.py      # List tasks tool
    ├── complete_task.py   # Complete task tool
    ├── delete_task.py     # Delete task tool
    └── update_task.py     # Update task tool
```

### Tool Schema Format

Each tool includes a JSON schema for parameter validation:

```python
tool_schema = {
    "name": "tool_name",
    "description": "Tool description",
    "parameters": {
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param_name"]
    }
}
```

### Integration with TaskService

All tools delegate to `TaskService` for data operations:

```python
from src.services.task_service import TaskService

async def add_task(user_id: str, title: str, description: str = None):
    return await TaskService.create_task(user_id, title, description)
```

---

## Future Enhancements

- Integration with Phase II task database (currently using mock data)
- Real-time task synchronization
- Task priority and due dates
- Task categories and tags
- Task sharing between users
- Advanced filtering and search
- Task history and audit logs

---

## Troubleshooting

### Tool Not Found

**Issue**: Agent cannot find MCP tool

**Solution**: Verify tool is registered in `server.py` MCP_TOOLS list

### Type Errors

**Issue**: task_id type mismatch

**Solution**: Ensure task_id is passed as integer, not string

### Permission Errors

**Issue**: User cannot access task

**Solution**: Verify user_id matches task owner in database

---

## Support

For issues or questions about MCP tools:
1. Check this documentation
2. Review tool implementation in `backend/src/mcp/tools/`
3. Test with MCP Inspector
4. Check Agent SDK integration logs
