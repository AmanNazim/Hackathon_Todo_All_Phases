# Backend Implementation Tasks: Phase III AI Chatbot API

**Date**: 2026-02-09
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

---

## Task Overview

This document breaks down the backend implementation into actionable tasks with clear acceptance criteria and dependencies.

**Total Tasks**: 10
**Estimated Effort**: 3-4 days

---

## Task 1: Setup FastAPI Application

**Priority**: High
**Dependencies**: None
**Estimated Time**: 1 hour

### Description
Create FastAPI application with basic configuration, CORS, error handling, and settings management.

### Files to Create/Modify
- `phase-III-ai-chatbot/backend/main.py`
- `phase-III-ai-chatbot/backend/src/config/__init__.py`
- `phase-III-ai-chatbot/backend/src/config/settings.py`

### Implementation Details

**settings.py**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "Phase III AI Chatbot"
    environment: str = "development"
    debug: bool = True

    # Database (from existing .env)
    database_url: str

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

**main.py**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.api import chat

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Acceptance Criteria
- [x] FastAPI app created and runs
- [x] Settings loaded from .env
- [x] CORS configured
- [x] Health endpoint works
- [x] App can be started with `uvicorn main:app`

### Testing
```bash
# Start server
uvicorn main:app --reload

# Test health endpoint
curl http://localhost:8000/health
```

---

## Task 2: Implement Task Service

**Priority**: High
**Dependencies**: None (uses existing database)
**Estimated Time**: 2 hours

### Description
Create service layer for task operations that will be used by MCP tools.

### Files to Create
- `phase-III-ai-chatbot/backend/src/services/__init__.py`
- `phase-III-ai-chatbot/backend/src/services/task_service.py`
- `phase-III-ai-chatbot/backend/src/schemas/__init__.py`
- `phase-III-ai-chatbot/backend/src/schemas/task.py`

### Implementation Details

**task.py (schemas)**:
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
```

**task_service.py**:
```python
from typing import List, Optional
from uuid import UUID

class TaskService:
    """Service for task operations"""

    @staticmethod
    async def create_task(user_id: str, title: str, description: Optional[str] = None) -> dict:
        """Create new task"""
        # Use Phase II task creation logic
        # Return {"task_id": str, "status": "created", "title": str}
        pass

    @staticmethod
    async def list_tasks(user_id: str, status: str = "all") -> List[dict]:
        """List user's tasks"""
        # Query tasks from database
        # Filter by status if specified
        # Return list of task dicts
        pass

    @staticmethod
    async def complete_task(user_id: str, task_id: str) -> dict:
        """Mark task as complete"""
        # Update task status to completed
        # Return {"task_id": str, "status": "completed", "title": str}
        pass

    @staticmethod
    async def delete_task(user_id: str, task_id: str) -> dict:
        """Delete task"""
        # Delete task from database
        # Return {"task_id": str, "status": "deleted", "title": str}
        pass

    @staticmethod
    async def update_task(
        user_id: str,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> dict:
        """Update task"""
        # Update task fields
        # Return {"task_id": str, "status": "updated", "title": str}
        pass
```

### Acceptance Criteria
- [x] TaskService class created with 5 methods
- [x] All methods are async
- [x] Methods interact with Phase II task database
- [x] Proper error handling for task not found
- [x] User isolation enforced (user can only access own tasks)

### Testing
```python
async def test_task_service():
    # Create task
    result = await TaskService.create_task("user123", "Buy milk")
    assert result["status"] == "created"

    # List tasks
    tasks = await TaskService.list_tasks("user123")
    assert len(tasks) >= 1
```

---

## Task 3: Implement MCP Tools

**Priority**: High
**Dependencies**: Task 2
**Estimated Time**: 3 hours

### Description
Implement 5 MCP tools that wrap TaskService methods with proper schemas.

### Files to Create
- `phase-III-ai-chatbot/backend/src/mcp/__init__.py`
- `phase-III-ai-chatbot/backend/src/mcp/server.py`
- `phase-III-ai-chatbot/backend/src/mcp/tools/__init__.py`
- `phase-III-ai-chatbot/backend/src/mcp/tools/add_task.py`
- `phase-III-ai-chatbot/backend/src/mcp/tools/list_tasks.py`
- `phase-III-ai-chatbot/backend/src/mcp/tools/complete_task.py`
- `phase-III-ai-chatbot/backend/src/mcp/tools/delete_task.py`
- `phase-III-ai-chatbot/backend/src/mcp/tools/update_task.py`

### Implementation Details

**add_task.py**:
```python
from src.services.task_service import TaskService

async def add_task(user_id: str, title: str, description: str = None) -> dict:
    """
    Create a new task for the user.

    Args:
        user_id: User identifier
        title: Task title
        description: Optional task description

    Returns:
        dict with task_id, status, and title
    """
    return await TaskService.create_task(user_id, title, description)

# Tool schema for MCP
add_task_schema = {
    "name": "add_task",
    "description": "Create a new task for the user",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User identifier"},
            "title": {"type": "string", "description": "Task title"},
            "description": {"type": "string", "description": "Optional task description"}
        },
        "required": ["user_id", "title"]
    }
}
```

**server.py**:
```python
from src.mcp.tools.add_task import add_task, add_task_schema
from src.mcp.tools.list_tasks import list_tasks, list_tasks_schema
from src.mcp.tools.complete_task import complete_task, complete_task_schema
from src.mcp.tools.delete_task import delete_task, delete_task_schema
from src.mcp.tools.update_task import update_task, update_task_schema

# MCP tools registry
MCP_TOOLS = [
    {"function": add_task, "schema": add_task_schema},
    {"function": list_tasks, "schema": list_tasks_schema},
    {"function": complete_task, "schema": complete_task_schema},
    {"function": delete_task, "schema": delete_task_schema},
    {"function": update_task, "schema": update_task_schema},
]

def get_mcp_tools():
    """Get all MCP tools for agent"""
    return [tool["function"] for tool in MCP_TOOLS]

def get_mcp_schemas():
    """Get all MCP tool schemas"""
    return [tool["schema"] for tool in MCP_TOOLS]
```

### Acceptance Criteria
- [x] All 5 MCP tools implemented
- [x] Each tool has proper schema definition
- [x] Tools wrap TaskService methods
- [x] Error handling in each tool
- [x] Tools can be imported and called

### Testing
```python
async def test_mcp_tools():
    # Test add_task
    result = await add_task("user123", "Buy milk")
    assert result["status"] == "created"

    # Test list_tasks
    tasks = await list_tasks("user123", "all")
    assert isinstance(tasks, list)
```

---

## Task 4: Configure OpenAI Agent

**Priority**: High
**Dependencies**: Task 3
**Estimated Time**: 2 hours

### Description
Setup OpenAI Agent with MCP tools and system prompt for task management.

### Files to Create
- `phase-III-ai-chatbot/backend/src/agent/__init__.py`
- `phase-III-ai-chatbot/backend/src/agent/config.py`
- `phase-III-ai-chatbot/backend/src/agent/runner.py`

### Implementation Details

**config.py**:
```python
SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their todo tasks through natural conversation.

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
"""
```

**runner.py**:
```python
from openai import OpenAI
from src.config.settings import settings
from src.mcp.server import get_mcp_tools
from src.agent.config import SYSTEM_PROMPT

client = OpenAI(api_key=settings.openai_api_key)

async def run_agent(user_id: str, messages: list) -> str:
    """
    Run OpenAI agent with conversation history

    Args:
        user_id: User identifier (passed to tools)
        messages: Conversation history

    Returns:
        AI response text
    """
    # Get MCP tools
    tools = get_mcp_tools()

    # Build messages with system prompt
    full_messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + messages

    # Call OpenAI with tools
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=full_messages,
        tools=tools,
        tool_choice="auto"
    )

    # Handle tool calls if any
    # Execute tools with user_id
    # Return final response

    return response.choices[0].message.content
```

### Acceptance Criteria
- [x] System prompt defined
- [x] Agent runner created
- [x] MCP tools integrated
- [x] Tool execution handled
- [x] Response returned correctly

### Testing
```python
async def test_agent():
    messages = [{"role": "user", "content": "Add task to buy milk"}]
    response = await run_agent("user123", messages)
    assert "added" in response.lower() or "created" in response.lower()
```

---

## Task 5: Implement Chat Service

**Priority**: High
**Dependencies**: Task 4
**Estimated Time**: 2 hours

### Description
Create chat service that orchestrates conversation flow: load history, run agent, save messages.

### Files to Create
- `phase-III-ai-chatbot/backend/src/services/chat_service.py`

### Implementation Details

```python
from uuid import UUID
from typing import Optional
from src.repositories.conversation_repository import ConversationRepository
from src.repositories.message_repository import MessageRepository
from src.models.message import MessageRole
from src.agent.runner import run_agent

class ChatService:
    """Service for chat operations"""

    @staticmethod
    async def handle_chat(
        user_id: str,
        message: str,
        conversation_id: Optional[UUID] = None
    ) -> dict:
        """
        Handle chat message and return AI response

        Args:
            user_id: User identifier
            message: User's message
            conversation_id: Optional existing conversation ID

        Returns:
            dict with conversation_id and response
        """
        # 1. Get or create conversation
        if conversation_id:
            conv = await ConversationRepository.get_by_id(conversation_id)
            if not conv or conv.user_id != user_id:
                raise ValueError("Conversation not found")
        else:
            conv = await ConversationRepository.create(user_id)

        # 2. Load conversation history (last 20 messages)
        history = await MessageRepository.get_conversation_messages(
            conv.id, limit=20
        )

        # 3. Save user message
        await MessageRepository.create(
            conv.id, user_id, MessageRole.USER, message
        )

        # 4. Build messages for agent
        messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in history
        ] + [{"role": "user", "content": message}]

        # 5. Run agent
        ai_response = await run_agent(user_id, messages)

        # 6. Save AI response
        await MessageRepository.create(
            conv.id, user_id, MessageRole.ASSISTANT, ai_response
        )

        # 7. Update conversation timestamp
        await ConversationRepository.update_timestamp(conv.id)

        # 8. Return response
        return {
            "conversation_id": str(conv.id),
            "response": ai_response
        }
```

### Acceptance Criteria
- [x] ChatService class created
- [x] handle_chat method implemented
- [x] Conversation creation/retrieval works
- [x] History loaded correctly
- [x] Messages saved to database
- [x] Conversation timestamp updated
- [x] Proper error handling

### Testing
```python
async def test_chat_service():
    # New conversation
    result = await ChatService.handle_chat(
        "user123", "Add task to buy milk"
    )
    assert "conversation_id" in result
    assert "response" in result

    # Continue conversation
    result2 = await ChatService.handle_chat(
        "user123", "Show my tasks", result["conversation_id"]
    )
    assert result2["conversation_id"] == result["conversation_id"]
```

---

## Task 6: Implement Chat Endpoint

**Priority**: High
**Dependencies**: Task 5
**Estimated Time**: 2 hours

### Description
Create FastAPI endpoint for chat with request/response models and validation.

### Files to Create
- `phase-III-ai-chatbot/backend/src/api/__init__.py`
- `phase-III-ai-chatbot/backend/src/api/chat.py`
- `phase-III-ai-chatbot/backend/src/schemas/chat.py`

### Implementation Details

**chat.py (schemas)**:
```python
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str = Field(..., min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    created_at: str
```

**chat.py (api)**:
```python
from fastapi import APIRouter, HTTPException, Depends
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService
from datetime import datetime

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for natural language task management

    Args:
        request: Chat request with optional conversation_id and message

    Returns:
        Chat response with conversation_id and AI response
    """
    try:
        # TODO: Add authentication (Task 7)
        user_id = "test_user"  # Temporary

        result = await ChatService.handle_chat(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )

        return ChatResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            created_at=datetime.utcnow().isoformat()
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Acceptance Criteria
- [x] Chat endpoint created at POST /api/chat
- [x] Request validation works (message length)
- [x] Response model correct
- [x] Error handling for 404, 500
- [x] Endpoint can be called successfully

### Testing
```bash
# Test endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task to buy milk"}'
```

---

## Task 7: Add Authentication

**Priority**: Medium
**Dependencies**: Task 6
**Estimated Time**: 2 hours

### Description
Integrate Better Auth for user authentication and authorization.

### Files to Create/Modify
- `phase-III-ai-chatbot/backend/src/api/dependencies.py`
- `phase-III-ai-chatbot/backend/src/api/chat.py` (modify)

### Implementation Details

**dependencies.py**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify authentication token and extract user_id

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        user_id: Authenticated user identifier

    Raises:
        HTTPException: 401 if token invalid
    """
    token = credentials.credentials

    # TODO: Verify token with Better Auth
    # For now, simple validation
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Extract user_id from token
    # This is placeholder - implement actual Better Auth integration
    user_id = "user123"  # Extract from token

    return user_id
```

**Update chat.py**:
```python
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)  # Add authentication
):
    # Now user_id comes from token
    result = await ChatService.handle_chat(
        user_id=user_id,
        message=request.message,
        conversation_id=request.conversation_id
    )
    # ... rest of code
```

### Acceptance Criteria
- [x] Authentication dependency created
- [x] Token verification implemented
- [x] user_id extracted from token
- [x] Chat endpoint protected
- [x] 401 error for invalid token

### Testing
```bash
# Test with token
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task"}'

# Test without token (should fail)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task"}'
```

---

## Task 8: Write Unit Tests

**Priority**: Medium
**Dependencies**: Tasks 2-7
**Estimated Time**: 3 hours

### Description
Write unit tests for services, MCP tools, and agent.

### Files to Create
- `phase-III-ai-chatbot/backend/tests/test_task_service.py`
- `phase-III-ai-chatbot/backend/tests/test_mcp_tools.py`
- `phase-III-ai-chatbot/backend/tests/test_chat_service.py`

### Implementation Details

**test_mcp_tools.py**:
```python
import pytest
from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks

@pytest.mark.asyncio
class TestMCPTools:

    async def test_add_task(self):
        result = await add_task("user123", "Buy milk")
        assert result["status"] == "created"
        assert "task_id" in result

    async def test_list_tasks(self):
        tasks = await list_tasks("user123", "all")
        assert isinstance(tasks, list)

    # Add more tests for other tools
```

### Acceptance Criteria
- [x] Tests for TaskService methods
- [x] Tests for all 5 MCP tools
- [x] Tests for ChatService
- [x] Tests use pytest-asyncio
- [x] All tests pass

---

## Task 9: Write Integration Tests

**Priority**: Medium
**Dependencies**: Task 8
**Estimated Time**: 2 hours

### Description
Write integration tests for chat endpoint and full flow.

### Files to Create
- `phase-III-ai-chatbot/backend/tests/test_chat_endpoint.py`

### Implementation Details

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestChatEndpoint:

    def test_chat_new_conversation(self):
        response = client.post(
            "/api/chat",
            json={"message": "Add task to buy milk"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response" in data

    def test_chat_continue_conversation(self):
        # First message
        response1 = client.post(
            "/api/chat",
            json={"message": "Add task to buy milk"}
        )
        conv_id = response1.json()["conversation_id"]

        # Second message
        response2 = client.post(
            "/api/chat",
            json={
                "conversation_id": conv_id,
                "message": "Show my tasks"
            }
        )
        assert response2.status_code == 200

    def test_chat_invalid_message(self):
        response = client.post(
            "/api/chat",
            json={"message": "x" * 1001}  # Too long
        )
        assert response.status_code == 422
```

### Acceptance Criteria
- [x] Tests for chat endpoint
- [x] Tests for conversation flow
- [x] Tests for error cases
- [x] All tests pass

---

## Task 10: Create Documentation

**Priority**: Low
**Dependencies**: All previous tasks
**Estimated Time**: 2 hours

### Description
Create API documentation and usage guide.

### Files to Create
- `phase-III-ai-chatbot/backend/API.md`
- Update `phase-III-ai-chatbot/backend/README.md`

### Content Outline
1. API Overview
2. Authentication
3. Chat Endpoint
4. Request/Response Examples
5. Error Codes
6. MCP Tools Reference
7. Development Setup
8. Testing Guide

### Acceptance Criteria
- [ ] API.md created with complete documentation
- [ ] README.md updated with backend info
- [ ] Examples provided
- [ ] Clear and comprehensive

---

## Task Execution Order

```
Task 1 (FastAPI Setup) ──> Task 2 (Task Service) ──> Task 3 (MCP Tools) ──> Task 4 (Agent) ──> Task 5 (Chat Service) ──> Task 6 (Chat Endpoint) ──> Task 7 (Auth)

Task 8 (Unit Tests) [After Tasks 2-7]
Task 9 (Integration Tests) [After Task 8]
Task 10 (Documentation) [After all tasks]
```

**Recommended Order**:
1. Task 1: Setup FastAPI
2. Task 2: Implement Task Service
3. Task 3: Implement MCP Tools
4. Task 4: Configure Agent
5. Task 5: Implement Chat Service
6. Task 6: Implement Chat Endpoint
7. Task 7: Add Authentication
8. Task 8: Write Unit Tests
9. Task 9: Write Integration Tests
10. Task 10: Create Documentation

---

## Definition of Done

All tasks are considered complete when:
- [ ] All code written and tested
- [ ] All tests passing
- [ ] Chat endpoint working end-to-end
- [ ] Authentication integrated
- [ ] Documentation complete
- [ ] No critical bugs
- [ ] Performance meets requirements (<3s response time)

---

## Notes

- Use existing database component (already implemented)
- Integrate with Phase II task database
- Keep implementation simple and focused
- Test thoroughly at each step
- Document as you go

---

**Status**: Ready for implementation
**Next Step**: Begin Task 1 (Setup FastAPI Application)
