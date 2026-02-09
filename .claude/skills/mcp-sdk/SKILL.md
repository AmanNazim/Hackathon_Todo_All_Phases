---
name: mcp-sdk
description: Complete Model Context Protocol (MCP) SDK for building servers and clients that connect LLMs to external tools and data sources. Supports Python, TypeScript, Java, Kotlin, C#, and Rust. Use when building MCP servers to expose Resources/Tools/Prompts, building MCP clients to connect to servers, integrating with Claude for Desktop, or troubleshooting MCP connections and tool execution.
---

# MCP SDK Complete Skill

Complete Model Context Protocol (MCP) framework for building servers and clients across multiple languages.

## Core Concepts

**MCP Servers**: Expose capabilities (Resources, Tools, Prompts) to clients via STDIO or SSE transport.

**MCP Clients**: Connect to servers and use their capabilities.

**Resources**: File-like data readable by clients (files, database records, API responses).

**Tools**: LLM-callable functions requiring user approval before execution.

**Prompts**: Pre-written templates for specific tasks.

**Transports**: STDIO (standard I/O) or SSE (Server-Sent Events over HTTP).

## Installation

### Python
```bash
pip install mcp
pip install fastmcp  # Simplified server creation
```

### TypeScript
```bash
npm install @modelcontextprotocol/sdk
```

### Other Languages
- Java: `implementation 'io.modelcontextprotocol:sdk:0.1.0'`
- Kotlin: `implementation 'io.modelcontextprotocol:kotlin-sdk:0.1.0'`
- C#: `dotnet add package ModelContextProtocol`
- Rust: `mcp-sdk = "0.1.0"`

## Building MCP Servers

### Python Server (FastMCP - Recommended)

```python
from fastmcp import FastMCP

mcp = FastMCP("Demo Server")

@mcp.resource("file://logs/app.log")
def get_logs() -> str:
    """Returns application logs"""
    with open("/var/logs/app.log") as f:
        return f.read()

@mcp.tool()
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.prompt()
def review_code(code: str) -> str:
    """Generate code review prompt"""
    return f"Please review this code:\n{code}"

if __name__ == "__main__":
    mcp.run()
```

### Python Server (Standard SDK)

```python
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
import mcp.server.stdio

server = Server("demo-server")

@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="file://logs/app.log",
            name="Application Logs",
            mimeType="text/plain"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "file://logs/app.log":
        with open("/var/logs/app.log") as f:
            return f.read()
    raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="calculate_sum",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "calculate_sum":
        result = arguments["a"] + arguments["b"]
        return [TextContent(type="text", text=str(result))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### TypeScript Server

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "demo-server", version: "1.0.0" },
  { capabilities: { resources: {}, tools: {} } }
);

server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "file://logs/app.log",
      name: "Application Logs",
      mimeType: "text/plain",
    },
  ],
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  if (request.params.uri === "file://logs/app.log") {
    const logs = await fs.readFile("/var/logs/app.log", "utf-8");
    return { contents: [{ uri: request.params.uri, mimeType: "text/plain", text: logs }] };
  }
  throw new Error(`Unknown resource: ${request.params.uri}`);
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "calculate_sum",
      description: "Add two numbers",
      inputSchema: {
        type: "object",
        properties: {
          a: { type: "number" },
          b: { type: "number" },
        },
        required: ["a", "b"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "calculate_sum") {
    const { a, b } = request.params.arguments as { a: number; b: number };
    return { content: [{ type: "text", text: String(a + b) }] };
  }
  throw new Error(`Unknown tool: ${request.params.name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## Building MCP Clients

### Python Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

            # Call a tool
            result = await session.call_tool("calculate_sum", {"a": 5, "b": 3})
            print(f"Result: {result}")

            # List resources
            resources = await session.list_resources()
            print(f"Available resources: {resources}")

            # Read a resource
            content = await session.read_resource("file://logs/app.log")
            print(f"Resource content: {content}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### TypeScript Client

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: "python",
  args: ["server.py"],
});

const client = new Client(
  { name: "demo-client", version: "1.0.0" },
  { capabilities: {} }
);

await client.connect(transport);

// List tools
const tools = await client.listTools();
console.log("Available tools:", tools);

// Call tool
const result = await client.callTool({
  name: "calculate_sum",
  arguments: { a: 5, b: 3 },
});
console.log("Result:", result);

// List resources
const resources = await client.listResources();
console.log("Available resources:", resources);

// Read resource
const content = await client.readResource({
  uri: "file://logs/app.log",
});
console.log("Resource content:", content);
```

## Claude for Desktop Integration

Add server configuration to Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "demo-server": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

**Critical**: Use absolute paths for command and args.

## Logging Best Practices

### STDIO Servers - CRITICAL CONSTRAINT

**NEVER write to stdout in STDIO servers** - it breaks the protocol.

```python
import logging
import sys

# Configure logging to stderr ONLY
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)
logger.info("Server started")  # Safe - goes to stderr
```

### HTTP/SSE Servers

Can write to stdout freely since communication uses HTTP.

## Troubleshooting

### Server Not Appearing in Claude

1. Validate JSON syntax in config file
2. Use absolute paths for command and args
3. Check server logs in stderr
4. Restart Claude Desktop completely
5. Test server independently: `python server.py`

### Tool Execution Failures

1. Validate input schema matches tool definition
2. Check error messages in server logs (stderr)
3. Verify user approved tool execution
4. Test tool independently outside MCP

### Resource Access Issues

1. Verify URI format (e.g., `file://path/to/resource`)
2. Check file permissions
3. Ensure resource exists before listing
4. Validate MIME type is appropriate

### Connection Problems

1. **STDIO**: Verify command and args are correct
2. **SSE**: Verify server is running and accessible
3. Check environment variables are set correctly
4. Review transport initialization code
5. Check for stdout pollution in STDIO servers

## Multi-Language Server Examples

### Java Server

```java
import io.modelcontextprotocol.server.Server;
import io.modelcontextprotocol.server.Tool;
import io.modelcontextprotocol.server.Resource;

public class DemoServer {
    public static void main(String[] args) {
        Server server = new Server("demo-server");

        server.registerTool(new Tool(
            "calculate_sum",
            "Add two numbers",
            (params) -> {
                int a = params.getInt("a");
                int b = params.getInt("b");
                return String.valueOf(a + b);
            }
        ));

        server.registerResource(new Resource(
            "file://logs/app.log",
            "Application Logs",
            () -> Files.readString(Path.of("/var/logs/app.log"))
        ));

        server.start();
    }
}
```

### Kotlin Server

```kotlin
import io.modelcontextprotocol.server.*

fun main() {
    val server = Server("demo-server")

    server.registerTool(
        Tool(
            name = "calculate_sum",
            description = "Add two numbers"
        ) { params ->
            val a = params["a"] as Int
            val b = params["b"] as Int
            (a + b).toString()
        }
    )

    server.registerResource(
        Resource(
            uri = "file://logs/app.log",
            name = "Application Logs"
        ) {
            File("/var/logs/app.log").readText()
        }
    )

    server.start()
}
```

## Best Practices

### Server Design

- Use FastMCP for rapid prototyping (Python)
- Use standard SDK for production systems
- Implement proper error handling
- Validate all inputs
- Use descriptive names and documentation

### Tool Implementation

- Keep tools focused and single-purpose
- Provide clear input schemas with JSON Schema
- Return structured, parseable output
- Handle errors gracefully with meaningful messages
- Log tool executions for debugging (to stderr)

### Resource Management

- Use appropriate URI schemes (file://, http://, custom://)
- Set correct MIME types
- Implement efficient caching for frequently accessed resources
- Handle large resources with streaming
- Validate resource access permissions

### Client Integration

- Initialize session properly before operations
- Handle connection failures with retry logic
- Implement exponential backoff for retries
- Cache tool/resource lists to reduce calls
- Clean up connections on exit

### Security

- Validate all user inputs before processing
- Sanitize file paths to prevent directory traversal
- Use environment variables for secrets (never hardcode)
- Implement rate limiting for tool calls
- Audit tool executions with logging

### Performance

- Use async/await for I/O operations
- Implement connection pooling for clients
- Cache frequently accessed resources
- Optimize tool execution time
- Monitor resource usage and memory

## Testing

### Test Server Independently

```bash
# Python
python server.py

# TypeScript
node server.js

# Java
java -jar server.jar
```

### Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python server.py
```

### Integration Testing

```python
import pytest
from mcp.client.stdio import stdio_client

@pytest.mark.asyncio
async def test_tool_execution():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("calculate_sum", {"a": 5, "b": 3})
            assert result.content[0].text == "8"
```

## Common Patterns

### Database Query Tool

```python
@mcp.tool()
def query_database(sql: str) -> list[dict]:
    """Execute SQL query and return results"""
    # Validate SQL to prevent injection
    if not is_safe_query(sql):
        raise ValueError("Unsafe query detected")

    conn = get_db_connection()
    cursor = conn.execute(sql)
    return [dict(row) for row in cursor.fetchall()]
```

### File System Resource

```python
@mcp.resource("file://workspace/{path}")
def read_file(path: str) -> str:
    """Read file from workspace"""
    # Sanitize path to prevent directory traversal
    safe_path = sanitize_path(path)
    full_path = os.path.join(WORKSPACE_DIR, safe_path)

    with open(full_path, 'r') as f:
        return f.read()
```

### API Integration Tool

```python
@mcp.tool()
async def fetch_weather(city: str) -> dict:
    """Fetch weather data for a city"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.weather.com/{city}") as resp:
            return await resp.json()
```

## Documentation References

- Core Documentation: https://modelcontextprotocol.io/
- Quickstart: https://modelcontextprotocol.io/quickstart
- Building Servers: https://modelcontextprotocol.io/docs/building-servers
- Building Clients: https://modelcontextprotocol.io/docs/building-clients
- Integration: https://modelcontextprotocol.io/docs/integration
