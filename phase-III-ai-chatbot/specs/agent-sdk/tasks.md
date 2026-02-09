# Phase III AI Chatbot - Agent SDK Implementation Tasks

## Overview

Implementation tasks for upgrading the Phase III AI Chatbot backend to use OpenAI Agents SDK.

## Tasks

### Task 1: Project Setup and Structure
**Status**: [x]

**Description**: Create the agent_sdk module structure and update dependencies.

**Acceptance Criteria**:
- [x] Create `src/agent_sdk/` directory
- [x] Create `__init__.py` files for all modules
- [x] Add `openai-agents>=0.1.0` to requirements.txt
- [x] Create `data/` directory for session storage
- [x] Update .gitignore to exclude sessions.db

**Files**:
- `src/agent_sdk/__init__.py`
- `requirements.txt`
- `.gitignore`

---

### Task 2: Implement Agent Service
**Status**: [x]

**Description**: Create agent service to configure and create the main task management agent.

**Acceptance Criteria**:
- [x] Create `agent_service.py` with `create_task_agent()` function
- [x] Define comprehensive TASK_AGENT_INSTRUCTIONS
- [x] Configure agent with gpt-4o-mini model
- [x] Set model settings (temperature=0.7, include_usage=True)
- [x] Set max_iterations=10
- [x] Accept tools, input_guardrails, output_guardrails as parameters

**Files**:
- `src/agent_sdk/agent_service.py`

**Test Cases**:
- Agent is created with correct name and model
- Agent has proper instructions
- Agent accepts tools list
- Model settings are configured correctly

---

### Task 3: Implement Session Service
**Status**: [x]

**Description**: Create session service to manage SDK SQLiteSession instances.

**Acceptance Criteria**:
- [x] Create `session_service.py` with session management functions
- [x] Implement `get_or_create_session(conversation_id)` function
- [x] Return tuple of (SQLiteSession, UUID)
- [x] Create new UUID if conversation_id is None
- [x] Use file-based SQLite storage at `data/sessions.db`
- [x] Handle session creation errors gracefully

**Files**:
- `src/agent_sdk/session_service.py`

**Test Cases**:
- New session created when conversation_id is None
- Existing session retrieved when conversation_id provided
- Session persists to database file
- UUID is returned correctly

---

### Task 4: Implement Tool Adapter
**Status**: [x]

**Description**: Create tool adapter to convert MCP tools to SDK function tools with user_id context injection.

**Acceptance Criteria**:
- [x] Create `tool_adapter.py` with `create_function_tools(user_id)` function
- [x] Wrap all 5 MCP tools with @function_tool decorator
- [x] Inject user_id into each tool call automatically
- [x] Preserve original tool signatures (except user_id)
- [x] Maintain tool descriptions from MCP tools
- [x] Return list of function tools

**Files**:
- `src/agent_sdk/tool_adapter.py`

**Test Cases**:
- All 5 tools are created
- Tools have correct names and descriptions
- user_id is injected correctly
- Tools call underlying MCP functions
- Async functions work correctly

---

### Task 5: Implement Guardrails
**Status**: [x]

**Description**: Create input and output guardrails for validation and safety.

**Acceptance Criteria**:
- [x] Create `guardrails.py` with guardrail functions
- [x] Implement `input_validation_guardrail` with @input_guardrail decorator
- [x] Validate message length (1-1000 characters)
- [x] Check for empty messages
- [x] Implement `output_quality_guardrail` with @output_guardrail decorator
- [x] Validate output is not empty or too short
- [x] Return GuardrailFunctionOutput with tripwire_triggered flag
- [x] Provide clear error messages in output_info

**Files**:
- `src/agent_sdk/guardrails.py`

**Test Cases**:
- Input guardrail rejects empty messages
- Input guardrail rejects messages > 1000 chars
- Input guardrail accepts valid messages
- Output guardrail rejects empty responses
- Output guardrail accepts valid responses
- Tripwire flags set correctly

---

### Task 6: Implement Runner Service
**Status**: [x]

**Description**: Create runner service to execute agents using SDK Runner.

**Acceptance Criteria**:
- [x] Create `runner_service.py` with runner functions
- [x] Implement `run_agent()` for synchronous execution
- [x] Use `Runner.run()` with agent, message, session, context_variables
- [x] Handle MaxTurnsExceeded exception
- [x] Handle general exceptions with clear error messages
- [x] Return final_output string
- [x] Implement `run_agent_streamed()` for streaming execution
- [x] Use `Runner.run_streamed()` with same parameters
- [x] Yield events as they arrive
- [x] Handle streaming errors gracefully

**Files**:
- `src/agent_sdk/runner_service.py`

**Test Cases**:
- run_agent executes successfully
- run_agent handles MaxTurnsExceeded
- run_agent handles general errors
- run_agent_streamed yields events
- run_agent_streamed handles errors
- Context variables passed correctly

---

### Task 7: Update Chat Service
**Status**: [x]

**Description**: Update chat service to use Agent SDK instead of direct OpenAI calls.

**Acceptance Criteria**:
- [x] Update `chat_service.py` to use Agent SDK components
- [x] Replace OpenAI client calls with Agent SDK Runner
- [x] Use `get_or_create_session()` for session management
- [x] Use `create_function_tools()` for tool creation
- [x] Use `create_task_agent()` for agent creation
- [x] Use `run_agent()` for execution
- [x] Remove custom conversation history logic
- [x] Simplify error handling
- [x] Maintain same return format

**Files**:
- `src/services/chat_service.py`

**Test Cases**:
- Chat service creates new conversations
- Chat service continues existing conversations
- Chat service returns correct response format
- Chat service handles errors properly
- Session persists across calls

---

### Task 8: Add Streaming Endpoint
**Status**: [x]

**Description**: Add new streaming endpoint to chat API for real-time responses.

**Acceptance Criteria**:
- [x] Add `POST /api/chat/stream` endpoint to `chat.py`
- [x] Accept same ChatRequest as regular endpoint
- [x] Use `run_agent_streamed()` for execution
- [x] Return StreamingResponse with text/event-stream media type
- [x] Implement event_generator() async function
- [x] Yield SSE format events (event: type\ndata: json\n\n)
- [x] Handle text events from stream
- [x] Send complete event with conversation_id at end
- [x] Handle errors in stream gracefully

**Files**:
- `src/api/chat.py`

**Test Cases**:
- Streaming endpoint accepts requests
- Streaming endpoint returns SSE format
- Events are streamed in real-time
- Complete event sent at end
- Errors handled gracefully
- Authentication required

---

### Task 9: Create Tests
**Status**: [x]

**Description**: Create comprehensive tests for Agent SDK integration.

**Acceptance Criteria**:
- [x] Create `tests/test_agent_sdk.py` for unit tests
- [x] Test agent service creation
- [x] Test session service functions
- [x] Test tool adapter wrapping
- [x] Test guardrails validation
- [x] Test runner service execution
- [x] Create `tests/test_streaming.py` for streaming tests
- [x] Test streaming endpoint
- [x] Test SSE format
- [x] Test error handling in streams
- [x] All tests pass

**Files**:
- `tests/test_agent_sdk.py`
- `tests/test_streaming.py`

**Test Cases**:
- All unit tests pass
- All integration tests pass
- Streaming tests pass
- Error scenarios covered

---

### Task 10: Update Documentation
**Status**: [x]

**Description**: Update API documentation to include Agent SDK features and streaming endpoint.

**Acceptance Criteria**:
- [x] Update `API.md` with streaming endpoint documentation
- [x] Document SSE event format
- [x] Add streaming examples
- [x] Document Agent SDK architecture
- [x] Add troubleshooting section
- [x] Update requirements and setup instructions

**Files**:
- `backend/API.md`
- `backend/README.md` (if exists)

**Test Cases**:
- Documentation is clear and complete
- Examples are accurate
- All endpoints documented

---

## Task Dependencies

```
Task 1 (Setup)
  ↓
Task 2 (Agent Service) ← Task 5 (Guardrails)
  ↓
Task 3 (Session Service)
  ↓
Task 4 (Tool Adapter)
  ↓
Task 6 (Runner Service)
  ↓
Task 7 (Chat Service Update)
  ↓
Task 8 (Streaming Endpoint)
  ↓
Task 9 (Tests)
  ↓
Task 10 (Documentation)
```

## Implementation Notes

- Keep existing code functional during implementation
- Test each component independently before integration
- Use type hints throughout for better IDE support
- Follow existing code style and conventions
- Add docstrings to all public functions
- Handle errors gracefully with user-friendly messages

## Success Criteria

- [x] All 10 tasks completed
- [x] All tests passing
- [x] Existing chat endpoint works with Agent SDK
- [x] New streaming endpoint functional
- [x] Documentation updated
- [x] No breaking changes to API contract
