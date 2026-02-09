# Phase III AI Chatbot - ChatKit UI Implementation Plan

## Overview

This plan details the implementation strategy for integrating OpenAI's ChatKit framework with the Phase III AI Chatbot backend (Agent SDK + LiteLLM).

## Architecture Decisions

### 1. Integration Approach

**Decision**: Use Advanced Integration (ChatKit Python SDK on our infrastructure)

**Rationale**:
- We already have a custom Agent SDK backend
- Need full control over agent behavior and tools
- Want to leverage existing LiteLLM multi-provider support
- Can customize widget generation for task management
- Maintains existing authentication and session management

**Implementation**:
- Create ChatKitServer subclass in backend
- Bridge Agent SDK with ChatKit interface
- Generate widgets for task display and interaction
- Handle actions for task operations

### 2. Frontend Architecture

**Decision**: Simple React app with ChatKit embed

**Rationale**:
- ChatKit handles all chat UI complexity
- Focus on configuration and theming
- Minimal custom code needed
- Fast development and maintenance

**Implementation**:
- Create React app with ChatKit component
- Configure ChatKit to connect to our backend
- Implement theme switching
- Add authentication wrapper

### 3. Widget Strategy

**Decision**: Generate widgets server-side for task management

**Rationale**:
- ChatKit widgets provide rich, interactive UI
- Server controls what widgets to show
- Type-safe widget generation in Python
- Consistent with ChatKit patterns

**Implementation**:
- Create widget builders for tasks
- Generate Card widgets with task lists
- Add action buttons (complete, delete, edit)
- Implement form widgets for task creation/editing

### 4. Streaming Integration

**Decision**: Adapt existing SSE streaming to ChatKit events

**Rationale**:
- Already have streaming endpoint
- ChatKit expects specific event format
- Need to convert Agent SDK events to ChatKit events
- Maintain real-time response experience

**Implementation**:
- Create event adapter for ChatKit format
- Stream text deltas as they arrive
- Show tool execution indicators
- Handle completion events

### 5. Action Handling

**Decision**: Server-side action handling with Agent SDK integration

**Rationale**:
- Actions trigger backend operations
- Need to call MCP tools for task operations
- Want to generate AI responses after actions
- Maintain conversation context

**Implementation**:
- Implement action() method in ChatKitServer
- Route actions to appropriate handlers
- Call MCP tools for task operations
- Generate AI responses using Agent SDK

### 6. Authentication Strategy

**Decision**: Reuse existing Bearer token authentication

**Rationale**:
- Already have auth system in place
- ChatKit supports custom auth headers
- No need to rebuild authentication
- Maintains security model

**Implementation**:
- Pass Bearer token from frontend to ChatKit
- ChatKit includes token in backend requests
- Backend validates token as before
- No changes to existing auth flow

## Component Design

### 1. ChatKitServer Implementation (`backend/src/chatkit/server.py`)

**Purpose**: Bridge Agent SDK with ChatKit interface

**Key Methods**:
- `generate()`: Generate AI responses using Agent SDK
- `action()`: Handle widget actions (complete, delete, edit tasks)
- `create_task_widgets()`: Generate widgets for task display
- `create_task_form()`: Generate form widgets for task creation/editing

**Design**:
```python
from openai_chatkit import ChatKitServer, Event
from src.agent_sdk import create_task_agent, get_or_create_session, create_function_tools, run_agent

class TaskChatKitServer(ChatKitServer):
    async def generate(self, context, thread):
        # Get user_id from context
        user_id = context.user_id

        # Get or create session
        session, conv_id = get_or_create_session(thread.id)

        # Create tools and agent
        tools = create_function_tools(user_id)
        agent = create_task_agent(tools)

        # Get last user message
        messages = await self.get_thread_messages(thread.id)
        last_message = messages[-1].content

        # Run agent with streaming
        async for event in run_agent_streamed(agent, last_message, session, user_id):
            # Convert to ChatKit events
            yield self.convert_to_chatkit_event(event)

    async def action(self, thread, action, sender, context):
        # Handle task actions
        if action.type == "complete_task":
            await self.complete_task(action.payload['task_id'], context.user_id)
        elif action.type == "delete_task":
            await self.delete_task(action.payload['task_id'], context.user_id)
        elif action.type == "edit_task":
            await self.update_task(action.payload, context.user_id)

        # Generate AI response
        async for event in self.generate(context, thread):
            yield event
```

### 2. Widget Builders (`backend/src/chatkit/widgets.py`)

**Purpose**: Generate ChatKit widgets for task management

**Key Functions**:
- `build_task_list_widget(tasks)`: Create ListView of tasks
- `build_task_card(task)`: Create Card for single task
- `build_task_form(task=None)`: Create Form for task creation/editing
- `build_starter_prompts()`: Create starter prompt buttons

**Design**:
```python
from openai_chatkit.widgets import Card, ListView, ListViewItem, Button, Form, Text, Title

def build_task_list_widget(tasks):
    return Card(
        children=[
            Title(value="Your Tasks"),
            ListView(
                items=[
                    ListViewItem(
                        title=task.title,
                        description=task.description,
                        badge=Badge(label=task.status),
                        actions=[
                            Button(
                                label="Complete",
                                onClickAction=ActionConfig(
                                    type="complete_task",
                                    payload={"task_id": task.id}
                                )
                            ),
                            Button(
                                label="Delete",
                                onClickAction=ActionConfig(
                                    type="delete_task",
                                    payload={"task_id": task.id}
                                )
                            )
                        ]
                    )
                    for task in tasks
                ]
            )
        ]
    )
```

### 3. Event Adapter (`backend/src/chatkit/events.py`)

**Purpose**: Convert Agent SDK events to ChatKit events

**Key Functions**:
- `convert_text_event(event)`: Convert text delta to ChatKit format
- `convert_tool_event(event)`: Convert tool call to ChatKit format
- `convert_complete_event(event)`: Convert completion to ChatKit format

**Design**:
```python
def convert_to_chatkit_event(agent_event):
    if hasattr(agent_event, 'text'):
        return TextDeltaEvent(text=agent_event.text)
    elif hasattr(agent_event, 'tool_name'):
        return ToolCallEvent(tool=agent_event.tool_name)
    elif agent_event.type == 'complete':
        return CompleteEvent()
    else:
        return agent_event
```

### 4. React Frontend (`frontend/src/App.tsx`)

**Purpose**: ChatKit UI with theme and auth

**Key Components**:
- `App`: Main application component
- `ChatKitProvider`: ChatKit configuration
- `ThemeProvider`: Light/dark mode management
- `AuthProvider`: Authentication wrapper

**Design**:
```typescript
import { ChatKit } from '@openai/chatkit';
import { useState } from 'react';

function App() {
  const [theme, setTheme] = useState('light');
  const [token, setToken] = useState(localStorage.getItem('auth_token'));

  const chatKitConfig = {
    apiUrl: 'http://localhost:8000/api/chatkit',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    theme: {
      colorScheme: theme,
      // ... theme configuration
    }
  };

  return (
    <div className="app">
      <ChatKit config={chatKitConfig} />
    </div>
  );
}
```

### 5. Backend API Routes (`backend/src/api/chatkit.py`)

**Purpose**: ChatKit-specific API endpoints

**Key Endpoints**:
- `POST /api/chatkit/generate`: Generate AI responses
- `POST /api/chatkit/action`: Handle widget actions
- `GET /api/chatkit/threads`: List conversation threads

**Design**:
```python
from fastapi import APIRouter, Depends
from src.chatkit.server import TaskChatKitServer
from src.api.dependencies import get_current_user

router = APIRouter()
chatkit_server = TaskChatKitServer()

@router.post("/chatkit/generate")
async def generate(request: GenerateRequest, user_id: str = Depends(get_current_user)):
    async for event in chatkit_server.generate(request.context, request.thread):
        yield event

@router.post("/chatkit/action")
async def action(request: ActionRequest, user_id: str = Depends(get_current_user)):
    async for event in chatkit_server.action(
        request.thread,
        request.action,
        request.sender,
        request.context
    ):
        yield event
```

## Project Structure

```
phase-III-ai-chatbot/
├── backend/
│   ├── src/
│   │   ├── chatkit/              # New: ChatKit integration
│   │   │   ├── __init__.py
│   │   │   ├── server.py         # ChatKitServer implementation
│   │   │   ├── widgets.py        # Widget builders
│   │   │   ├── events.py         # Event adapters
│   │   │   └── actions.py        # Action handlers
│   │   └── api/
│   │       └── chatkit.py        # New: ChatKit API routes
│   └── requirements.txt          # Add openai-chatkit
├── frontend/                     # New: React frontend
│   ├── public/
│   ├── src/
│   │   ├── App.tsx              # Main app component
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── ThemeToggle.tsx
│   │   │   └── AuthWrapper.tsx
│   │   ├── config/
│   │   │   └── chatkit.ts       # ChatKit configuration
│   │   └── styles/
│   │       └── theme.ts         # Theme definitions
│   ├── package.json
│   └── tsconfig.json
└── specs/
    └── frontend/
        ├── spec.md
        ├── plan.md              # This file
        └── tasks.md
```

## Implementation Strategy

### Phase 1: Backend ChatKit Integration
1. Install openai-chatkit package
2. Create ChatKitServer implementation
3. Implement widget builders
4. Create event adapters
5. Add ChatKit API routes

### Phase 2: Frontend Setup
1. Create React app with TypeScript
2. Install ChatKit SDK
3. Configure ChatKit component
4. Implement theme system
5. Add authentication wrapper

### Phase 3: Widget Implementation
1. Create task list widgets
2. Create task form widgets
3. Implement action handlers
4. Test widget interactions

### Phase 4: Integration Testing
1. Test backend-frontend communication
2. Test streaming responses
3. Test widget actions
4. Test theme switching
5. Test authentication flow

## Testing Strategy

### Backend Tests
- ChatKitServer method tests
- Widget generation tests
- Event conversion tests
- Action handler tests

### Frontend Tests
- Component rendering tests
- ChatKit configuration tests
- Theme switching tests
- Authentication flow tests

### Integration Tests
- End-to-end chat flow
- Widget interaction flow
- Streaming response flow
- Error handling flow

## Migration Path

1. Implement ChatKit backend alongside existing API
2. Create frontend with ChatKit
3. Test thoroughly in development
4. Deploy frontend and backend together
5. Monitor for issues
6. Gradually migrate users to ChatKit UI

## Success Metrics

1. ChatKit successfully connects to backend
2. Streaming responses work smoothly
3. Widgets render and function correctly
4. Actions execute without errors
5. Theme switching is instant
6. Authentication is secure
7. Performance is acceptable (< 100ms response time)

## Dependencies

### Backend
```
openai-chatkit>=0.1.0
```

### Frontend
```json
{
  "@openai/chatkit": "latest",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.0.0"
}
```

## Timeline Estimate

- Backend ChatKit integration: 3-4 hours
- Frontend setup: 2-3 hours
- Widget implementation: 2-3 hours
- Testing and refinement: 2-3 hours

Total: 9-13 hours of development time
