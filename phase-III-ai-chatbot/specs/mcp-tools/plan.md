# MCP Tools Implementation Plan

## Overview

Implement 5 MCP tools for task management using Python MCP SDK (FastMCP). The tools will integrate with existing task storage and expose task operations to AI agents through the Model Context Protocol.

## Technical Approach

### 1. MCP Server Implementation

**Choice**: Use FastMCP (simplified Python MCP SDK)

**Rationale**:
- Simpler decorator-based API for rapid development
- Automatic schema generation from function signatures
- Built-in STDIO transport support
- Less boilerplate than standard MCP SDK

**Alternative Considered**: Standard MCP SDK
- More verbose, requires manual schema definition
- Better for complex scenarios with custom transport
- Not needed for this straightforward use case

### 2. Tool Implementation Strategy

**Approach**: Implement each tool as a decorated Python function

**Pattern**:
```python
from fastmcp import FastMCP

mcp = FastMCP("Task Management Server")

@mcp.tool()
def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task"""
    # Implementation
    return {"task_id": id, "status": "created", "title": title}
```

**Benefits**:
- Type hints provide automatic schema generation
- Docstrings become tool descriptions
- Return types are automatically serialized
- Input validation handled by FastMCP

### 3. Integration with Existing Storage

**Approach**: Import and use existing task database functions

**Assumptions**:
- Task storage functions exist in `phase-III-ai-chatbot/backend/database/` or similar
- Functions like `create_task()`, `get_tasks()`, `update_task()`, `delete_task()` are available
- Tasks have fields: id, user_id, title, description, completed

**Integration Pattern**:
```python
from backend.database.tasks import (
    create_task,
    get_user_tasks,
    update_task_status,
    delete_task_by_id,
    update_task_fields
)

@mcp.tool()
def add_task(user_id: str, title: str, description: str = "") -> dict:
    task = create_task(user_id, title, description)
    return {"task_id": task.id, "status": "created", "title": task.title}
```

### 4. Tool Schema Definitions

Each tool will have JSON Schema automatically generated from Python type hints:

**add_task**:
- user_id: string (required)
- title: string (required)
- description: string (optional, default: "")

**list_tasks**:
- user_id: string (required)
- status: string (optional, enum: ["all", "pending", "completed"], default: "all")

**complete_task**:
- user_id: string (required)
- task_id: integer (required)

**delete_task**:
- user_id: string (required)
- task_id: integer (required)

**update_task**:
- user_id: string (required)
- task_id: integer (required)
- title: string (optional)
- description: string (optional)

### 5. Error Handling Strategy

**Approach**: Use try-except blocks with clear error messages

**Pattern**:
```python
@mcp.tool()
def complete_task(user_id: str, task_id: int) -> dict:
    try:
        task = get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        if task.user_id != user_id:
            raise ValueError(f"Task {task_id} does not belong to user {user_id}")

        updated_task = mark_task_complete(task_id)
        return {"task_id": task_id, "status": "completed", "title": updated_task.title}
    except Exception as e:
        logger.error(f"Error completing task: {e}", file=sys.stderr)
        raise
```

**Error Types**:
- ValueError: Task not found, invalid parameters, permission errors
- TypeError: Invalid parameter types (handled by FastMCP)
- Database errors: Connection issues, constraint violations

### 6. Logging Configuration

**Critical Constraint**: STDIO servers must log to stderr only

**Configuration**:
```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)
```

**What to Log**:
- Tool invocations (user_id, tool name, parameters)
- Errors and exceptions
- Database operations
- Validation failures

### 7. File Structure

```
phase-III-ai-chatbot/backend/
├── mcp/
│   ├── __init__.py
│   ├── server.py          # Main MCP server with FastMCP
│   ├── tools.py           # Tool implementations
│   └── config.py          # Configuration and logging
└── database/
    └── tasks.py           # Existing task storage functions
```

**Rationale**:
- Separate MCP concerns from database logic
- `server.py` initializes FastMCP and registers tools
- `tools.py` contains tool implementations
- `config.py` handles logging and configuration

### 8. Transport Configuration

**Transport**: STDIO (Standard Input/Output)

**Rationale**:
- Required for Claude Desktop integration
- Simpler than HTTP/SSE for local agent communication
- No network configuration needed

**Implementation**:
```python
if __name__ == "__main__":
    mcp.run()  # FastMCP handles STDIO transport automatically
```

### 9. Testing Strategy

**Unit Tests**:
- Test each tool function independently
- Mock database calls
- Verify correct return formats
- Test error conditions

**Integration Tests**:
- Test with actual database
- Verify user isolation (tasks scoped by user_id)
- Test concurrent operations

**Manual Testing**:
- Use MCP Inspector: `npx @modelcontextprotocol/inspector python backend/mcp/server.py`
- Test with Agent SDK integration
- Verify natural language command handling

### 10. Agent Integration

**Approach**: Agent SDK will use MCP client to connect to tools

**Flow**:
1. Agent receives user message
2. Agent determines intent (add/list/complete/delete/update)
3. Agent calls appropriate MCP tool via client
4. Agent receives structured response
5. Agent formats response for user

**No Changes Needed**: Agent SDK already supports MCP tools through existing integration

## Implementation Steps

1. **Setup MCP Server Structure**
   - Create `backend/mcp/` directory
   - Create `__init__.py`, `server.py`, `tools.py`, `config.py`
   - Configure logging to stderr

2. **Implement Tool Functions**
   - Implement `add_task` tool
   - Implement `list_tasks` tool
   - Implement `complete_task` tool
   - Implement `delete_task` tool
   - Implement `update_task` tool

3. **Integrate with Database**
   - Import existing task storage functions
   - Add error handling for database operations
   - Ensure user isolation (user_id scoping)

4. **Configure MCP Server**
   - Initialize FastMCP instance
   - Register all tools
   - Configure STDIO transport
   - Add startup logging

5. **Testing**
   - Test each tool independently
   - Test with MCP Inspector
   - Test with Agent SDK integration
   - Verify error handling

6. **Documentation**
   - Document tool usage
   - Document error codes
   - Document integration with Agent SDK

## Risk Mitigation

**Risk**: Existing task storage functions may not match expected interface
**Mitigation**: Create adapter functions if needed to match tool signatures

**Risk**: User isolation may not be enforced in database
**Mitigation**: Add user_id validation in tool functions before database calls

**Risk**: STDIO transport may have buffering issues
**Mitigation**: Ensure no stdout writes, use stderr for all logging

**Risk**: Concurrent access to task database
**Mitigation**: Use database transactions, handle lock errors gracefully

## Success Criteria

- All 5 tools implemented and functional
- Tools integrate with existing task storage
- STDIO transport working correctly
- Logging to stderr only
- Agent can invoke tools successfully
- Error handling provides clear messages
- User isolation enforced (tasks scoped by user_id)
- All tests passing
