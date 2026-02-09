# ChatKit Integration Guide

## Overview

This document provides guidance for integrating OpenAI's ChatKit framework with the Phase III AI Chatbot backend.

## Backend Architecture

The backend provides a ChatKit-compatible API that bridges the Agent SDK (with LiteLLM) to ChatKit's interface.

### Components

1. **ChatKitServer** (`src/chatkit/server.py`)
   - Handles message generation using Agent SDK
   - Processes widget actions
   - Manages streaming responses

2. **Widget Builders** (`src/chatkit/widgets.py`)
   - Creates task list widgets
   - Generates task forms
   - Builds starter prompts

3. **Event Adapters** (`src/chatkit/events.py`)
   - Converts Agent SDK events to ChatKit format
   - Handles text deltas, tool calls, and completions

4. **Action Handlers** (`src/chatkit/actions.py`)
   - Processes task operations (create, complete, delete, update)
   - Calls MCP tools for task management

## API Endpoints

### Generate Endpoint

**POST /api/chatkit/generate**

Generates AI responses with streaming.

Request:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": "uuid | null"
}
```

Response: Server-Sent Events (SSE)
```
data: {"type": "text_delta", "text": "I've"}
data: {"type": "text_delta", "text": " added"}
data: {"type": "tool_call", "tool": "add_task_tool", "status": "running"}
data: {"type": "complete"}
```

### Action Endpoint

**POST /api/chatkit/action**

Handles widget actions.

Request:
```json
{
  "type": "complete_task",
  "payload": {"task_id": "123"},
  "conversation_id": "uuid | null"
}
```

Response: Server-Sent Events (SSE)

### Tasks Widget Endpoint

**GET /api/chatkit/tasks?status=all**

Returns task list widget.

Response:
```json
{
  "widget": {
    "type": "Card",
    "children": [...]
  }
}
```

## Widget Types

### Task List Widget

Displays a list of tasks with action buttons:

```python
{
  "type": "Card",
  "children": [
    {"type": "Title", "value": "Your Tasks"},
    {
      "type": "ListView",
      "items": [
        {
          "type": "ListViewItem",
          "title": "Buy groceries",
          "description": "Milk, eggs, bread",
          "badge": {"label": "pending", "color": "primary"},
          "actions": [
            {
              "type": "Button",
              "label": "Complete",
              "onClickAction": {
                "type": "complete_task",
                "payload": {"task_id": "123"}
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Task Form Widget

Form for creating or editing tasks:

```python
{
  "type": "Form",
  "onSubmitAction": {
    "type": "create_task",
    "payload": {}
  },
  "children": [
    {"type": "Title", "value": "Create New Task"},
    {
      "type": "Text",
      "value": "",
      "editable": {
        "name": "title",
        "required": True,
        "placeholder": "Enter task title"
      }
    },
    {"type": "Button", "label": "Create", "submit": True}
  ]
}
```

## Action Types

### complete_task
Marks a task as complete.

Payload:
```json
{"task_id": "123"}
```

### delete_task
Deletes a task.

Payload:
```json
{"task_id": "123"}
```

### update_task
Updates task title or description.

Payload:
```json
{
  "task_id": "123",
  "title": "New title",
  "description": "New description"
}
```

### create_task
Creates a new task.

Payload:
```json
{
  "title": "Task title",
  "description": "Task description"
}
```

## Event Types

### text_delta
Partial text response.

```json
{"type": "text_delta", "text": "partial text"}
```

### tool_call
Tool execution indicator.

```json
{"type": "tool_call", "tool": "add_task_tool", "status": "running"}
```

### complete
Stream completion.

```json
{"type": "complete"}
```

### error
Error event.

```json
{
  "type": "error",
  "error": "error_code",
  "message": "User-friendly message"
}
```

## Integration with Agent SDK

The ChatKit backend integrates seamlessly with the existing Agent SDK:

1. **Session Management**: Uses Agent SDK's SQLite sessions
2. **Tool Execution**: Calls MCP tools through Agent SDK
3. **Streaming**: Converts Agent SDK events to ChatKit format
4. **LiteLLM**: Supports 100+ LLM providers through Agent SDK

## Testing

### Test Generate Endpoint

```bash
curl -X POST http://localhost:8000/api/chatkit/generate \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy milk"}' \
  --no-buffer
```

### Test Action Endpoint

```bash
curl -X POST http://localhost:8000/api/chatkit/action \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "complete_task",
    "payload": {"task_id": "123"}
  }' \
  --no-buffer
```

### Test Tasks Widget

```bash
curl http://localhost:8000/api/chatkit/tasks?status=all \
  -H "Authorization: Bearer test-token"
```

## Troubleshooting

### Streaming Not Working
- Ensure `--no-buffer` flag is used with curl
- Check that SSE headers are set correctly
- Verify no proxy is buffering responses

### Actions Not Executing
- Check authentication token is valid
- Verify action type is supported
- Check payload format matches expected schema

### Widgets Not Displaying
- Verify widget structure matches ChatKit schema
- Check for JSON serialization errors
- Ensure all required fields are present

## Best Practices

1. **Error Handling**: Always wrap operations in try-except blocks
2. **Validation**: Validate action payloads before processing
3. **Streaming**: Use async generators for streaming responses
4. **Authentication**: Always require authentication for endpoints
5. **Logging**: Log all actions for debugging and monitoring

## Future Enhancements

- Multi-agent handoffs for specialized tasks
- Rich media widgets (images, files)
- Advanced task filtering and search
- Task analytics and insights
- Collaborative task management
