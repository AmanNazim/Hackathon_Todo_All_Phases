# Phase III AI Chatbot - Agent SDK Specification

## Overview

Implement a production-ready agent framework using OpenAI Agents SDK to replace the basic OpenAI integration in the Phase III AI Chatbot backend. The Agent SDK provides robust multi-agent workflows, session management, guardrails, and streaming capabilities.

## Goals

- Replace basic OpenAI Chat Completions API with OpenAI Agents SDK
- Implement proper session management using SDK's built-in sessions
- Add input/output guardrails for safety and quality
- Enable streaming responses for better UX
- Support multi-agent handoffs for specialized tasks
- Maintain compatibility with existing MCP tools

## Non-Goals

- Changing the existing API contract (POST /api/chat)
- Modifying the MCP tools implementation
- Adding new features beyond agent framework upgrade
- Implementing voice or advanced features

## Requirements

### 1. Agent Configuration

**FR-1.1**: Create a main task management agent using `Agent` class with:
- Name: "Task Management Agent"
- Instructions: System prompt for natural language task management
- Model: gpt-4o-mini (configurable via settings)
- Tools: All 5 existing MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)

**FR-1.2**: Configure agent with proper model settings:
- Temperature: 0.7 for natural conversation
- Include usage tracking for monitoring

### 2. Session Management

**FR-2.1**: Replace custom conversation storage with SDK's `SQLiteSession`:
- Use session_id based on conversation_id
- Store conversation history automatically
- Support conversation resumption

**FR-2.2**: Implement session lifecycle:
- Create new session for new conversations
- Load existing session for conversation continuation
- Automatic message history management

### 3. Tool Integration

**FR-3.1**: Convert existing MCP tools to SDK function tools:
- Wrap each MCP tool function with `@function_tool` decorator
- Maintain existing function signatures
- Preserve tool descriptions and parameters

**FR-3.2**: Inject user_id context into tool calls:
- Use context variables to pass user_id
- Ensure all tools receive correct user_id automatically

### 4. Guardrails

**FR-4.1**: Implement input guardrail:
- Validate message length (1-1000 characters)
- Check for appropriate content
- Run in parallel mode for best latency

**FR-4.2**: Implement output guardrail:
- Validate response quality
- Check for safe content
- Ensure responses are helpful and on-topic

### 5. Runner Integration

**FR-5.1**: Use `Runner.run()` for agent execution:
- Pass agent, user message, and session
- Handle context variables (user_id)
- Return final output

**FR-5.2**: Implement error handling:
- Catch `MaxTurnsExceeded` exception
- Handle guardrail failures gracefully
- Provide user-friendly error messages

### 6. Streaming Support

**FR-6.1**: Implement streaming endpoint using `Runner.run_streamed()`:
- Stream response events as they're generated
- Support both raw response events and run item events
- Enable real-time progress updates

**FR-6.2**: Create streaming response format:
- Server-Sent Events (SSE) format
- Include event types (text, tool_call, handoff)
- Proper connection handling

### 7. Multi-Agent Handoffs (Optional)

**FR-7.1**: Create specialized agents for different task types:
- Task Creation Agent: Specialized in creating tasks
- Task Query Agent: Specialized in listing and searching tasks
- Task Management Agent: Specialized in updating/deleting tasks

**FR-7.2**: Implement triage agent with handoffs:
- Analyze user intent
- Hand off to appropriate specialized agent
- Maintain conversation context across handoffs

## API Contract

### Existing Endpoint (Maintained)

**POST /api/chat**

Request:
```json
{
  "conversation_id": "uuid | null",
  "message": "string (1-1000 characters)"
}
```

Response:
```json
{
  "conversation_id": "string (uuid)",
  "response": "string",
  "created_at": "string (ISO 8601)"
}
```

### New Streaming Endpoint

**POST /api/chat/stream**

Request: Same as /api/chat

Response: Server-Sent Events (SSE)
```
event: text
data: {"text": "partial response"}

event: tool_call
data: {"tool": "add_task", "status": "running"}

event: complete
data: {"conversation_id": "uuid", "created_at": "timestamp"}
```

## Technical Architecture

### Components

1. **Agent Service** (`src/agent_sdk/agent_service.py`)
   - Create and configure agents
   - Manage agent lifecycle
   - Handle context injection

2. **Session Service** (`src/agent_sdk/session_service.py`)
   - Create and retrieve sessions
   - Manage session lifecycle
   - Handle session persistence

3. **Tool Adapter** (`src/agent_sdk/tool_adapter.py`)
   - Convert MCP tools to SDK function tools
   - Handle context injection for user_id
   - Maintain tool registry

4. **Guardrail Functions** (`src/agent_sdk/guardrails.py`)
   - Input validation guardrail
   - Output quality guardrail
   - Safety checks

5. **Runner Service** (`src/agent_sdk/runner_service.py`)
   - Execute agents with Runner.run()
   - Handle streaming with Runner.run_streamed()
   - Error handling and retries

6. **API Integration** (`src/api/chat.py` - updated)
   - Update existing endpoint to use Agent SDK
   - Add new streaming endpoint
   - Maintain backward compatibility

### Data Flow

```
User Request → API Endpoint → Input Guardrail → Agent Service
                                                      ↓
                                                 Runner.run()
                                                      ↓
                                    Agent → Tools → MCP Functions
                                      ↓
                                Output Guardrail → Response
```

## Dependencies

```
openai-agents>=0.1.0
```

## Success Criteria

1. All existing chat functionality works with Agent SDK
2. Conversation history persists using SDK sessions
3. Input/output guardrails validate all interactions
4. Streaming endpoint provides real-time responses
5. All MCP tools work as SDK function tools
6. Error handling provides clear user feedback
7. Performance is equal or better than current implementation

## Testing Requirements

1. Unit tests for agent configuration
2. Unit tests for tool adapter
3. Unit tests for guardrails
4. Integration tests for Runner service
5. Integration tests for streaming endpoint
6. End-to-end tests for complete chat flow

## Migration Path

1. Implement Agent SDK components alongside existing code
2. Add feature flag to switch between implementations
3. Test Agent SDK implementation thoroughly
4. Switch to Agent SDK as default
5. Remove old implementation after validation

## Future Enhancements

- Multi-agent handoffs for specialized tasks
- Advanced guardrails with LLM-based validation
- Redis sessions for distributed deployments
- Voice support for audio interactions
- Custom model providers via LiteLLM
