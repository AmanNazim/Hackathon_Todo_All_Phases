# Phase III AI Chatbot - ChatKit UI Frontend Specification

## Overview

Implement a modern chat interface using OpenAI's ChatKit framework to provide an intuitive user experience for the Phase III AI Chatbot. ChatKit will connect to the existing Agent SDK backend with streaming support.

## Goals

- Create a production-ready chat UI using ChatKit framework
- Integrate with existing Phase III backend (Agent SDK + LiteLLM)
- Support streaming responses for real-time feedback
- Implement task management widgets for rich interactions
- Provide responsive design for mobile and desktop
- Enable theme customization (light/dark mode)

## Non-Goals

- Building custom chat UI from scratch (use ChatKit instead)
- Modifying the backend API (use existing endpoints)
- Implementing voice or video features
- Building a mobile native app

## Requirements

### 1. ChatKit Integration

**FR-1.1**: Set up ChatKit React component with configuration:
- Connect to Phase III backend API
- Configure authentication with Bearer token
- Enable streaming mode for real-time responses
- Set up error handling and retry logic

**FR-1.2**: Implement ChatKit backend adapter (Python):
- Create ChatKitServer implementation
- Bridge Agent SDK backend with ChatKit interface
- Handle streaming events from Agent SDK
- Convert backend responses to ChatKit format

### 2. Chat Interface

**FR-2.1**: Implement basic chat functionality:
- Message input with composer
- Message history display
- User and assistant message bubbles
- Typing indicators during streaming
- Error message display

**FR-2.2**: Support streaming responses:
- Display partial responses as they arrive
- Show tool execution indicators
- Handle stream interruption gracefully
- Provide stop generation button

### 3. Task Management Widgets

**FR-3.1**: Create task list widget:
- Display tasks in Card containers
- Show task title, description, status
- Support task filtering (all, pending, completed)
- Implement task actions (complete, delete, edit)

**FR-3.2**: Create task creation widget:
- Form with title and description inputs
- Submit button with loading state
- Validation for required fields
- Success/error feedback

**FR-3.3**: Create task edit widget:
- Pre-filled form with existing task data
- Update button with loading state
- Cancel button to dismiss
- Confirmation on save

### 4. Theming and Styling

**FR-4.1**: Implement light theme:
- Clean, modern color scheme
- High contrast for readability
- Consistent spacing and typography
- Professional appearance

**FR-4.2**: Implement dark theme:
- Dark background with light text
- Reduced eye strain colors
- Maintained contrast ratios
- Theme toggle button

**FR-4.3**: Responsive design:
- Mobile-optimized layout (compact density)
- Desktop-optimized layout (regular density)
- Adaptive font sizes
- Touch-friendly controls on mobile

### 5. Starter Prompts

**FR-5.1**: Implement welcome screen:
- Display starter prompts for common tasks
- Examples: "Add a task", "Show my tasks", "What's pending?"
- Click to populate composer
- Smooth transition to chat

**FR-5.2**: Starter prompt categories:
- Task creation prompts
- Task query prompts
- Task management prompts
- Help and guidance prompts

### 6. Actions and Interactions

**FR-6.1**: Implement widget actions:
- Button click actions
- Form submit actions
- Task action handlers (complete, delete, edit)
- Client-side action routing

**FR-6.2**: Server-side action handling:
- Action endpoint in backend
- Action type routing
- Payload validation
- Response generation

### 7. Error Handling

**FR-7.1**: Handle connection errors:
- Display connection status
- Retry failed requests
- Show user-friendly error messages
- Provide reconnection button

**FR-7.2**: Handle validation errors:
- Form validation feedback
- Input error messages
- Prevent invalid submissions
- Clear error states on correction

### 8. Authentication

**FR-8.1**: Implement authentication flow:
- Login form or token input
- Store token securely (localStorage/sessionStorage)
- Include token in API requests
- Handle token expiration
- Logout functionality

## Technical Architecture

### Frontend Stack

- **Framework**: React 18+
- **ChatKit**: OpenAI ChatKit SDK
- **Styling**: ChatKit theming system
- **State Management**: React hooks + ChatKit state
- **HTTP Client**: Fetch API with streaming support

### Backend Integration

- **API Endpoint**: `http://localhost:8000/api/chat`
- **Streaming Endpoint**: `http://localhost:8000/api/chat/stream`
- **Authentication**: Bearer token in Authorization header
- **Response Format**: ChatKit-compatible events

### Component Structure

```
ChatKitApp
├── ChatKitProvider (configuration)
├── ThemeProvider (light/dark mode)
├── AuthProvider (authentication)
└── ChatInterface
    ├── Header (title, theme toggle, logout)
    ├── MessageList (chat history)
    │   ├── UserMessage
    │   ├── AssistantMessage
    │   └── WidgetMessage (task widgets)
    ├── Composer (message input)
    └── StartScreen (starter prompts)
```

### Data Flow

```
User Input → Composer → ChatKit → Backend API → Agent SDK → LLM
                                                      ↓
User Display ← ChatKit ← Streaming Events ← Backend ← Agent Response
```

### Widget Architecture

```python
# Backend: Generate widgets for tasks
Card(
    children=[
        Title(value="My Tasks"),
        ListView(
            items=[
                ListViewItem(
                    title=task.title,
                    description=task.description,
                    actions=[
                        Button(label="Complete", onClickAction=...),
                        Button(label="Delete", onClickAction=...)
                    ]
                )
                for task in tasks
            ]
        )
    ]
)
```

## API Contract

### Chat Request (Existing)
```json
POST /api/chat
{
  "conversation_id": "uuid | null",
  "message": "string"
}
```

### Chat Response (Existing)
```json
{
  "conversation_id": "uuid",
  "response": "string",
  "created_at": "timestamp"
}
```

### Streaming Response (Existing)
```
POST /api/chat/stream
Server-Sent Events (SSE)
```

### New: ChatKit Action Endpoint
```json
POST /api/chatkit/action
{
  "type": "complete_task",
  "payload": {
    "task_id": "123"
  }
}
```

## Dependencies

### Frontend
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@openai/chatkit": "latest",
    "typescript": "^5.0.0"
  }
}
```

### Backend (Additional)
```
openai-chatkit>=0.1.0
```

## Success Criteria

1. ChatKit UI successfully connects to backend
2. Users can send messages and receive streaming responses
3. Task widgets display and function correctly
4. Actions (complete, delete, edit) work as expected
5. Theme switching works smoothly
6. Responsive design works on mobile and desktop
7. Error handling provides clear feedback
8. Authentication flow is secure and user-friendly

## Testing Requirements

1. Unit tests for React components
2. Integration tests for ChatKit-backend communication
3. E2E tests for complete user flows
4. Widget rendering tests
5. Action handling tests
6. Theme switching tests
7. Responsive design tests

## Future Enhancements

- File attachments in chat
- Voice input support
- Multi-user collaboration
- Task notifications
- Advanced task filtering
- Task analytics dashboard
- Export chat history
