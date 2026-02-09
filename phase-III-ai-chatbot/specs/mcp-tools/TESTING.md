# MCP Server Testing Guide

## Running the MCP Server

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### Start the Server

```bash
# From the backend directory
cd phase-III-ai-chatbot/backend

# Run the MCP server
python mcp_server.py
```

The server will start with STDIO transport and wait for MCP client connections.

## Testing with MCP Inspector

The MCP Inspector is the official tool for testing MCP servers.

### Install MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

### Test the Server

```bash
# From the backend directory
npx @modelcontextprotocol/inspector python mcp_server.py
```

This will open a web interface where you can:
1. See all available tools
2. View tool schemas
3. Test tool execution with sample inputs
4. View responses and errors

## Manual Testing Examples

### Test add_task

```json
{
  "user_id": "ziakhan",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

Expected response:
```json
{
  "task_id": 12345,
  "status": "created",
  "title": "Buy groceries"
}
```

### Test list_tasks

```json
{
  "user_id": "ziakhan",
  "status": "all"
}
```

Expected response:
```json
[
  {
    "id": 12345,
    "title": "Buy groceries",
    "completed": false
  }
]
```

### Test complete_task

```json
{
  "user_id": "ziakhan",
  "task_id": 12345
}
```

Expected response:
```json
{
  "task_id": 12345,
  "status": "completed",
  "title": "Buy groceries"
}
```

### Test delete_task

```json
{
  "user_id": "ziakhan",
  "task_id": 12345
}
```

Expected response:
```json
{
  "task_id": 12345,
  "status": "deleted",
  "title": "Buy groceries"
}
```

### Test update_task

```json
{
  "user_id": "ziakhan",
  "task_id": 12345,
  "title": "Buy groceries and fruits"
}
```

Expected response:
```json
{
  "task_id": 12345,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

## Integration with Claude Desktop

### Configuration

Add to Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "task-management": {
      "command": "python",
      "args": ["/absolute/path/to/phase-III-ai-chatbot/backend/mcp_server.py"],
      "env": {}
    }
  }
}
```

**Important**: Use absolute paths for the command and args.

### Restart Claude Desktop

After updating the config, completely restart Claude Desktop to load the MCP server.

### Test in Claude

Try these commands in Claude:
- "Add a task to buy groceries"
- "Show me all my tasks"
- "Mark task 1 as complete"
- "Delete task 2"
- "Change task 3 to 'Call mom tonight'"

## Troubleshooting

### Server Not Starting

**Issue**: Import errors or module not found

**Solution**:
```bash
# Ensure you're in the backend directory
cd phase-III-ai-chatbot/backend

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run server
python mcp_server.py
```

### Tools Not Appearing in Claude

**Issue**: MCP server not loaded

**Solution**:
1. Check config file syntax (valid JSON)
2. Verify absolute paths
3. Check server logs in stderr
4. Restart Claude Desktop completely

### Type Errors

**Issue**: task_id type mismatch

**Solution**: Ensure task_id is passed as integer (not string)

### Logging Issues

**Issue**: No logs appearing

**Solution**: Logs go to stderr. Check terminal output or redirect stderr:
```bash
python mcp_server.py 2> mcp_server.log
```

## Verification Checklist

- [ ] Server starts without errors
- [ ] All 5 tools are registered
- [ ] MCP Inspector shows all tools
- [ ] add_task creates tasks successfully
- [ ] list_tasks returns task arrays
- [ ] complete_task marks tasks complete
- [ ] delete_task removes tasks
- [ ] update_task modifies tasks
- [ ] Error messages are clear
- [ ] Logging goes to stderr only
- [ ] Claude Desktop integration works

## Next Steps

1. Integrate with actual Phase II task database
2. Add comprehensive unit tests
3. Add integration tests with Agent SDK
4. Deploy to production environment
