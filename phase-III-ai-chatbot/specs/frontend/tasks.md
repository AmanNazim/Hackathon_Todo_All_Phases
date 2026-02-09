# Phase III AI Chatbot - ChatKit UI Implementation Tasks

## Overview

Implementation tasks for integrating OpenAI ChatKit framework with Phase III AI Chatbot backend.

## Tasks

### Task 1: Backend ChatKit Setup
**Status**: [x]

**Description**: Install ChatKit SDK and create project structure for ChatKit integration.

**Acceptance Criteria**:
- [x] Add `openai-chatkit>=0.1.0` to requirements.txt
- [x] Create `src/chatkit/` directory
- [x] Create `__init__.py` files
- [x] Create basic ChatKitServer subclass
- [x] Verify imports work correctly

**Files**:
- `backend/requirements.txt`
- `backend/src/chatkit/__init__.py`
- `backend/src/chatkit/server.py`

---

### Task 2: Implement Widget Builders
**Status**: [x]

**Description**: Create widget builder functions for task management UI.

**Acceptance Criteria**:
- [x] Create `widgets.py` with widget builders
- [x] Implement `build_task_list_widget(tasks)` function
- [x] Implement `build_task_card(task)` function
- [x] Implement `build_task_form(task=None)` function
- [x] Implement `build_starter_prompts()` function
- [x] Use ChatKit widget components (Card, ListView, Button, Form, etc.)

**Files**:
- `backend/src/chatkit/widgets.py`

**Test Cases**:
- Widget builders return valid ChatKit widgets
- Task list widget displays multiple tasks
- Task form widget has required fields
- Starter prompts are clickable

---

### Task 3: Implement Event Adapters
**Status**: [x]

**Description**: Create adapters to convert Agent SDK events to ChatKit event format.

**Acceptance Criteria**:
- [x] Create `events.py` with event conversion functions
- [x] Implement `convert_text_event()` for text deltas
- [x] Implement `convert_tool_event()` for tool calls
- [x] Implement `convert_complete_event()` for completion
- [x] Handle all Agent SDK event types

**Files**:
- `backend/src/chatkit/events.py`

**Test Cases**:
- Text events convert correctly
- Tool events convert correctly
- Complete events convert correctly
- Unknown events pass through safely

---

### Task 4: Implement Action Handlers
**Status**: [x]

**Description**: Create action handlers for widget interactions (complete, delete, edit tasks).

**Acceptance Criteria**:
- [x] Create `actions.py` with action handler functions
- [x] Implement `handle_complete_task(task_id, user_id)` function
- [x] Implement `handle_delete_task(task_id, user_id)` function
- [x] Implement `handle_update_task(payload, user_id)` function
- [x] Implement `handle_create_task(payload, user_id)` function
- [x] Call MCP tools for task operations

**Files**:
- `backend/src/chatkit/actions.py`

**Test Cases**:
- Complete task action works
- Delete task action works
- Update task action works
- Create task action works
- Actions call correct MCP tools

---

### Task 5: Implement ChatKitServer
**Status**: [x]

**Description**: Create ChatKitServer implementation that bridges Agent SDK with ChatKit.

**Acceptance Criteria**:
- [x] Implement `generate()` method using Agent SDK
- [x] Implement `action()` method for widget actions
- [x] Integrate with existing session management
- [x] Convert Agent SDK events to ChatKit events
- [x] Handle errors gracefully
- [x] Support streaming responses

**Files**:
- `backend/src/chatkit/server.py`

**Test Cases**:
- Generate method produces ChatKit events
- Action method handles all action types
- Sessions are created and managed correctly
- Streaming works properly
- Errors are handled gracefully

---

### Task 6: Add ChatKit API Routes
**Status**: [x]

**Description**: Create FastAPI routes for ChatKit endpoints.

**Acceptance Criteria**:
- [x] Create `src/api/chatkit.py` with ChatKit routes
- [x] Implement `POST /api/chatkit/generate` endpoint
- [x] Implement `POST /api/chatkit/action` endpoint
- [x] Implement `GET /api/chatkit/threads` endpoint (optional)
- [x] Add authentication with Bearer token
- [x] Include routes in main app

**Files**:
- `backend/src/api/chatkit.py`
- `backend/main.py` (update to include routes)

**Test Cases**:
- Generate endpoint returns streaming events
- Action endpoint handles actions correctly
- Authentication is required
- Unauthorized requests are rejected

---

### Task 7: Create React Frontend
**Status**: [x]

**Description**: Set up React application with TypeScript and ChatKit component.

**Acceptance Criteria**:
- [x] Create React app with TypeScript
- [x] Install `@openai/chatkit` package
- [x] Create `App.tsx` with ChatKit component
- [x] Configure ChatKit to connect to backend
- [x] Add authentication wrapper
- [x] Implement basic layout

**Files**:
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/src/App.tsx`
- `frontend/src/index.tsx`

**Test Cases**:
- App renders without errors
- ChatKit component displays
- Backend connection works
- Authentication token is sent

---

### Task 8: Implement Theme System
**Status**: [x]

**Description**: Create theme configuration for light and dark modes.

**Acceptance Criteria**:
- [x] Create theme configuration file
- [x] Implement light theme
- [x] Implement dark theme
- [x] Add theme toggle button
- [x] Persist theme preference
- [x] Apply theme to ChatKit

**Files**:
- `frontend/src/config/theme.ts`
- `frontend/src/components/ThemeToggle.tsx`

**Test Cases**:
- Light theme displays correctly
- Dark theme displays correctly
- Theme toggle switches themes
- Theme preference persists across sessions

---

### Task 9: Implement Authentication
**Status**: [x]

**Description**: Create authentication wrapper for ChatKit.

**Acceptance Criteria**:
- [x] Create AuthWrapper component
- [x] Implement login form or token input
- [x] Store token in localStorage
- [x] Pass token to ChatKit configuration
- [x] Implement logout functionality
- [x] Handle token expiration

**Files**:
- `frontend/src/components/AuthWrapper.tsx`
- `frontend/src/utils/auth.ts`

**Test Cases**:
- Login form accepts token
- Token is stored securely
- Token is included in requests
- Logout clears token
- Expired tokens are handled

---

### Task 10: Create Documentation
**Status**: [x]

**Description**: Document ChatKit UI setup, configuration, and usage.

**Acceptance Criteria**:
- [x] Create frontend README.md
- [x] Document installation steps
- [x] Document configuration options
- [x] Document theme customization
- [x] Add usage examples
- [x] Document widget customization

**Files**:
- `frontend/README.md`
- `backend/CHATKIT.md`

**Test Cases**:
- Documentation is clear and complete
- Examples are accurate
- Setup instructions work

---

## Task Dependencies

```
Task 1 (Backend Setup)
  ↓
Task 2 (Widget Builders) ← Task 3 (Event Adapters) ← Task 4 (Action Handlers)
  ↓
Task 5 (ChatKitServer)
  ↓
Task 6 (API Routes)
  ↓
Task 7 (React Frontend)
  ↓
Task 8 (Theme System)
  ↓
Task 9 (Authentication)
  ↓
Task 10 (Documentation)
```

## Implementation Notes

- Keep implementation simple and focused
- Use ChatKit's built-in features where possible
- Follow ChatKit best practices from documentation
- Test each component independently
- Ensure backward compatibility with existing API

## Success Criteria

- [x] All 10 tasks completed
- [x] ChatKit UI connects to backend
- [x] Streaming responses work
- [x] Widgets display and function correctly
- [x] Actions execute successfully
- [x] Theme switching works
- [x] Authentication is secure
- [x] Documentation is complete
