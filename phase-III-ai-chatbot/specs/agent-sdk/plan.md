# Phase III AI Chatbot - Agent SDK Implementation Plan

## Overview

This plan details the technical architecture and implementation strategy for upgrading the Phase III AI Chatbot backend from basic OpenAI Chat Completions API to the production-ready OpenAI Agents SDK.

## Architecture Decisions

### 1. Agent Design Pattern

**Decision**: Use single main agent with tools (not multi-agent handoffs initially)

**Rationale**:
- Simpler implementation for initial version
- All MCP tools are related to task management (single domain)
- Multi-agent handoffs add complexity without clear benefit for this use case
- Can add handoffs later if needed

**Implementation**:
- Create one `Task Management Agent` with all 5 MCP tools
- Use clear instructions for natural language understanding
- Configure with gpt-4o-mini model

### 2. Session Management Strategy

**Decision**: Use SQLiteSession with file-based persistence

**Rationale**:
- Built-in session management from SDK
- Automatic conversation history handling
- File-based persistence for durability
- Simple migration from current database approach
- Can upgrade to SQLAlchemy sessions later if needed

**Implementation**:
- Map conversation_id to session_id
- Store sessions in `data/sessions.db`
- Let SDK handle message history automatically
- Remove custom conversation history logic

### 3. Tool Integration Approach

**Decision**: Wrap existing MCP tools with @function_tool decorator

**Rationale**:
- Minimal changes to existing MCP tool code
- SDK handles tool schema generation automatically
- Maintains separation between agent layer and business logic
- Easy to test and maintain

**Implementation**:
- Create tool adapter module
- Wrap each MCP tool function
- Use context injection for user_id
- Preserve existing tool signatures

### 4. Guardrails Strategy

**Decision**: Implement lightweight input/output guardrails with parallel execution

**Rationale**:
- Input guardrails run in parallel for best latency
- Simple validation rules (length, content appropriateness)
- Output guardrails ensure quality without blocking
- Can enhance with LLM-based validation later

**Implementation**:
- Input guardrail: message length and content validation
- Output guardrail: response quality checks
- Use parallel mode for input guardrails
- Return clear error messages on tripwire

### 5. Streaming Implementation

**Decision**: Add new streaming endpoint alongside existing endpoint

**Rationale**:
- Maintains backward compatibility
- Allows gradual frontend migration
- Streaming provides better UX for long responses
- SSE is simple and widely supported

**Implementation**:
- Keep existing POST /api/chat unchanged
- Add new POST /api/chat/stream endpoint
- Use Runner.run_streamed() for streaming
- Return Server-Sent Events (SSE)

### 6. Error Handling Strategy

**Decision**: Comprehensive error handling with user-friendly messages

**Rationale**:
- SDK can raise MaxTurnsExceeded
- Guardrails can trigger and block execution
- Tool calls can fail
- Need clear error messages for users

**Implementation**:
- Catch MaxTurnsExceeded and return helpful message
- Handle guardrail failures with specific feedback
- Wrap tool errors with context
- Log all errors for debugging

## Component Design

### 1. Agent Service (`src/agent_sdk/agent_service.py`)

**Purpose**: Create and configure the main task management agent

**Key Functions**:
- `create_task_agent(tools: list) -> Agent`: Create configured agent
- `get_agent_config() -> dict`: Get agent configuration from settings

**Design**:
```python
from agents import Agent, ModelSettings
from src.config.settings import settings

def create_task_agent(tools: list) -> Agent:
    """Create the main task management agent"""
    return Agent(
        name="Task Management Agent",
        instructions=TASK_AGENT_INSTRUCTIONS,
        model=settings.openai_model,
        tools=tools,
        model_settings=ModelSettings(
            temperature=0.7,
            include_usage=True
        ),
        input_guardrails=[input_validation_guardrail],
        output_guardrails=[output_quality_guardrail],
        max_iterations=10
    )
```

### 2. Session Service (`src/agent_sdk/session_service.py`)

**Purpose**: Manage SDK sessions for conversation persistence

**Key Functions**:
- `get_or_create_session(conversation_id: Optional[UUID]) -> tuple[SQLiteSession, UUID]`
- `close_session(session: SQLiteSession) -> None`

**Design**:
```python
from agents import SQLiteSession
from uuid import UUID, uuid4
from pathlib import Path

SESSION_DB_PATH = "data/sessions.db"

def get_or_create_session(conversation_id: Optional[UUID]) -> tuple[SQLiteSession, UUID]:
    """Get existing session or create new one"""
    if conversation_id is None:
        conversation_id = uuid4()

    session = SQLiteSession(
        session_id=str(conversation_id),
        db_path=SESSION_DB_PATH
    )
    return session, conversation_id
```

### 3. Tool Adapter (`src/agent_sdk/tool_adapter.py`)

**Purpose**: Convert MCP tools to SDK function tools with context injection

**Key Functions**:
- `create_function_tools(user_id: str) -> list`: Create all function tools with user_id bound
- `wrap_mcp_tool(tool_func, user_id: str) -> callable`: Wrap single MCP tool

**Design**:
```python
from agents.decorators import function_tool
from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task

def create_function_tools(user_id: str) -> list:
    """Create function tools with user_id context"""

    @function_tool
    async def add_task_tool(title: str, description: str = None) -> dict:
        """Create a new task for the user"""
        return await add_task.add_task(user_id, title, description)

    @function_tool
    async def list_tasks_tool(status: str = "all") -> list:
        """List user's tasks"""
        return await list_tasks.list_tasks(user_id, status)

    # ... similar for other tools

    return [add_task_tool, list_tasks_tool, complete_task_tool,
            delete_task_tool, update_task_tool]
```

### 4. Guardrails (`src/agent_sdk/guardrails.py`)

**Purpose**: Validate inputs and outputs for safety and quality

**Key Functions**:
- `input_validation_guardrail(ctx, agent, input) -> GuardrailFunctionOutput`
- `output_quality_guardrail(ctx, agent, input, output) -> GuardrailFunctionOutput`

**Design**:
```python
from agents.decorators import input_guardrail, output_guardrail
from agents.types import GuardrailFunctionOutput

@input_guardrail
async def input_validation_guardrail(ctx, agent, input) -> GuardrailFunctionOutput:
    """Validate user input"""
    message = input if isinstance(input, str) else str(input)

    # Check length
    if len(message) < 1 or len(message) > 1000:
        return GuardrailFunctionOutput(
            output_info={"error": "Message must be 1-1000 characters"},
            tripwire_triggered=True
        )

    return GuardrailFunctionOutput(
        output_info={"valid": True},
        tripwire_triggered=False
    )

@output_guardrail
async def output_quality_guardrail(ctx, agent, input, output) -> GuardrailFunctionOutput:
    """Validate agent output quality"""
    # Check if output is empty or too short
    if not output or len(output) < 5:
        return GuardrailFunctionOutput(
            output_info={"error": "Response too short"},
            tripwire_triggered=True
        )

    return GuardrailFunctionOutput(
        output_info={"quality": "good"},
        tripwire_triggered=False
    )
```

### 5. Runner Service (`src/agent_sdk/runner_service.py`)

**Purpose**: Execute agents using SDK Runner

**Key Functions**:
- `run_agent(agent: Agent, message: str, session: SQLiteSession, user_id: str) -> str`
- `run_agent_streamed(agent: Agent, message: str, session: SQLiteSession, user_id: str) -> AsyncIterator`

**Design**:
```python
from agents import Runner
from agents.exceptions import MaxTurnsExceeded

async def run_agent(agent: Agent, message: str, session: SQLiteSession, user_id: str) -> str:
    """Run agent and return final output"""
    try:
        result = await Runner.run(
            agent,
            message,
            session=session,
            context_variables={"user_id": user_id}
        )
        return result.final_output
    except MaxTurnsExceeded:
        return "I apologize, but I've reached the maximum number of steps. Please try rephrasing your request."
    except Exception as e:
        raise RuntimeError(f"Agent execution failed: {str(e)}")

async def run_agent_streamed(agent: Agent, message: str, session: SQLiteSession, user_id: str):
    """Run agent with streaming"""
    try:
        async for event in Runner.run_streamed(agent, message, session=session,
                                               context_variables={"user_id": user_id}):
            yield event
    except MaxTurnsExceeded:
        yield {"error": "Maximum turns exceeded"}
    except Exception as e:
        yield {"error": str(e)}
```

### 6. Chat Service Update (`src/services/chat_service.py`)

**Purpose**: Update to use Agent SDK instead of direct OpenAI calls

**Changes**:
- Replace OpenAI client calls with Agent SDK Runner
- Use SDK sessions instead of custom conversation storage
- Remove manual message history management
- Simplify error handling

**Design**:
```python
from src.agent_sdk.agent_service import create_task_agent
from src.agent_sdk.session_service import get_or_create_session
from src.agent_sdk.tool_adapter import create_function_tools
from src.agent_sdk.runner_service import run_agent

class ChatService:
    @staticmethod
    async def handle_chat(user_id: str, message: str, conversation_id: Optional[UUID] = None) -> Dict:
        # Get or create session
        session, conv_id = get_or_create_session(conversation_id)

        # Create tools with user_id context
        tools = create_function_tools(user_id)

        # Create agent
        agent = create_task_agent(tools)

        # Run agent
        response = await run_agent(agent, message, session, user_id)

        return {
            "conversation_id": str(conv_id),
            "response": response,
            "created_at": datetime.utcnow().isoformat()
        }
```

### 7. Streaming Endpoint (`src/api/chat.py`)

**Purpose**: Add streaming endpoint for real-time responses

**Design**:
```python
from fastapi.responses import StreamingResponse
from src.agent_sdk.runner_service import run_agent_streamed

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, user_id: str = Depends(get_current_user)):
    """Stream chat responses in real-time"""

    async def event_generator():
        session, conv_id = get_or_create_session(request.conversation_id)
        tools = create_function_tools(user_id)
        agent = create_task_agent(tools)

        async for event in run_agent_streamed(agent, request.message, session, user_id):
            if hasattr(event, 'text'):
                yield f"event: text\ndata: {json.dumps({'text': event.text})}\n\n"
            # Handle other event types

        yield f"event: complete\ndata: {json.dumps({'conversation_id': str(conv_id)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

## Project Structure

```
phase-III-ai-chatbot/backend/
├── src/
│   ├── agent_sdk/              # New: Agent SDK integration
│   │   ├── __init__.py
│   │   ├── agent_service.py    # Agent creation and configuration
│   │   ├── session_service.py  # Session management
│   │   ├── tool_adapter.py     # MCP tool to SDK tool adapter
│   │   ├── guardrails.py       # Input/output guardrails
│   │   └── runner_service.py   # Agent execution
│   ├── services/
│   │   └── chat_service.py     # Updated: Use Agent SDK
│   └── api/
│       └── chat.py             # Updated: Add streaming endpoint
├── data/
│   └── sessions.db             # New: SDK session storage
└── tests/
    ├── test_agent_sdk.py       # New: Agent SDK tests
    └── test_streaming.py       # New: Streaming tests
```

## Migration Strategy

### Phase 1: Implement Agent SDK Components
1. Create agent_sdk module structure
2. Implement agent service
3. Implement session service
4. Implement tool adapter
5. Implement guardrails
6. Implement runner service

### Phase 2: Update Existing Services
1. Update chat_service.py to use Agent SDK
2. Add streaming endpoint to chat.py
3. Update error handling

### Phase 3: Testing
1. Unit tests for all new components
2. Integration tests for chat flow
3. Streaming endpoint tests
4. End-to-end tests

### Phase 4: Deployment
1. Update requirements.txt
2. Update environment variables
3. Create data directory for sessions
4. Deploy and monitor

## Testing Strategy

### Unit Tests
- Agent configuration
- Tool adapter wrapping
- Guardrail validation logic
- Session creation and retrieval

### Integration Tests
- Complete chat flow with Agent SDK
- Streaming endpoint functionality
- Error handling scenarios
- Session persistence

### Performance Tests
- Response time comparison
- Streaming latency
- Session lookup performance

## Rollback Plan

If issues arise:
1. Keep old implementation code commented
2. Add feature flag to switch implementations
3. Monitor error rates and performance
4. Rollback to old implementation if needed

## Success Metrics

1. All existing tests pass
2. Response time <= current implementation
3. Streaming provides sub-second first token
4. Zero data loss in session migration
5. Error rate <= current implementation

## Dependencies

```
openai-agents>=0.1.0
```

## Timeline Estimate

- Agent SDK components: 2-3 hours
- Service updates: 1-2 hours
- Testing: 1-2 hours
- Documentation: 1 hour

Total: 5-8 hours of development time
