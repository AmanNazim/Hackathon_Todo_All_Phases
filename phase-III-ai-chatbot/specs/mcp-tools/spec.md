# MCP Tools for Task Management

## Overview

Expose task management capabilities to AI agents through standardized MCP (Model Context Protocol) tools. The AI agent will be able to create, list, complete, delete, and update tasks through natural language commands.

## User Scenarios

### Scenario 1: Creating Tasks
**Actor**: User
**Goal**: Add a new task to remember something
**Flow**:
1. User says "Add a task to buy groceries" or "I need to remember to pay bills"
2. Agent understands intent and calls add_task tool
3. Agent confirms task creation with friendly response

### Scenario 2: Viewing Tasks
**Actor**: User
**Goal**: See current tasks
**Flow**:
1. User says "Show me all my tasks" or "What's pending?"
2. Agent calls list_tasks with appropriate filter
3. Agent displays tasks in readable format

### Scenario 3: Completing Tasks
**Actor**: User
**Goal**: Mark a task as done
**Flow**:
1. User says "Mark task 3 as complete" or "I finished the groceries task"
2. Agent calls complete_task
3. Agent confirms completion

### Scenario 4: Deleting Tasks
**Actor**: User
**Goal**: Remove unwanted tasks
**Flow**:
1. User says "Delete the meeting task" or "Remove task 2"
2. Agent may list tasks first to identify correct task
3. Agent calls delete_task
4. Agent confirms deletion

### Scenario 5: Updating Tasks
**Actor**: User
**Goal**: Modify task details
**Flow**:
1. User says "Change task 1 to 'Call mom tonight'"
2. Agent calls update_task with new details
3. Agent confirms update

## Functional Requirements

### FR1: Add Task Tool
**Description**: Create a new task for a user

**Inputs**:
- user_id (string, required) - User identifier
- title (string, required) - Task title
- description (string, optional) - Task description

**Outputs**:
- task_id (integer) - Created task ID
- status (string) - "created"
- title (string) - Task title

**Acceptance Criteria**:
- Tool accepts user_id and title as required parameters
- Tool accepts optional description parameter
- Tool returns task_id, status, and title
- Tool validates required parameters before processing
- Tool returns error if user_id or title is missing

### FR2: List Tasks Tool
**Description**: Retrieve tasks for a user with optional filtering

**Inputs**:
- user_id (string, required) - User identifier
- status (string, optional) - Filter: "all", "pending", "completed" (default: "all")

**Outputs**:
- Array of task objects with id, title, completed fields

**Acceptance Criteria**:
- Tool accepts user_id as required parameter
- Tool accepts optional status filter
- Tool defaults to "all" if status not provided
- Tool returns array of tasks matching filter
- Tool returns empty array if no tasks found
- Tool validates user_id before processing

### FR3: Complete Task Tool
**Description**: Mark a task as complete

**Inputs**:
- user_id (string, required) - User identifier
- task_id (integer, required) - Task ID to complete

**Outputs**:
- task_id (integer) - Completed task ID
- status (string) - "completed"
- title (string) - Task title

**Acceptance Criteria**:
- Tool accepts user_id and task_id as required parameters
- Tool marks task as completed
- Tool returns task_id, status, and title
- Tool returns error if task not found
- Tool returns error if task doesn't belong to user

### FR4: Delete Task Tool
**Description**: Remove a task from the list

**Inputs**:
- user_id (string, required) - User identifier
- task_id (integer, required) - Task ID to delete

**Outputs**:
- task_id (integer) - Deleted task ID
- status (string) - "deleted"
- title (string) - Task title

**Acceptance Criteria**:
- Tool accepts user_id and task_id as required parameters
- Tool deletes task from storage
- Tool returns task_id, status, and title before deletion
- Tool returns error if task not found
- Tool returns error if task doesn't belong to user

### FR5: Update Task Tool
**Description**: Modify task title or description

**Inputs**:
- user_id (string, required) - User identifier
- task_id (integer, required) - Task ID to update
- title (string, optional) - New task title
- description (string, optional) - New task description

**Outputs**:
- task_id (integer) - Updated task ID
- status (string) - "updated"
- title (string) - Updated task title

**Acceptance Criteria**:
- Tool accepts user_id and task_id as required parameters
- Tool accepts optional title and description
- Tool updates only provided fields
- Tool returns task_id, status, and updated title
- Tool returns error if task not found
- Tool returns error if task doesn't belong to user
- Tool returns error if neither title nor description provided

### FR6: Natural Language Understanding
**Description**: Agent understands natural language commands and maps them to appropriate tools

**Behavior Mapping**:
- "Add/create/remember" → add_task
- "Show/list/see" → list_tasks
- "Done/complete/finished" → complete_task
- "Delete/remove/cancel" → delete_task
- "Change/update/rename" → update_task

**Acceptance Criteria**:
- Agent correctly identifies intent from natural language
- Agent extracts parameters from user message
- Agent calls appropriate tool with correct parameters
- Agent provides friendly confirmation after tool execution

### FR7: Error Handling
**Description**: Gracefully handle errors and provide clear feedback

**Error Cases**:
- Task not found
- Invalid user_id
- Invalid task_id
- Missing required parameters
- Task doesn't belong to user

**Acceptance Criteria**:
- All errors return clear, user-friendly messages
- Agent explains what went wrong
- Agent suggests corrective action when possible

## Success Criteria

- Users can create tasks through natural language in under 5 seconds
- Users can view their tasks with appropriate filtering
- Users can complete, delete, and update tasks by ID or description
- 95% of natural language commands are correctly interpreted
- All tool operations complete in under 1 second
- Error messages are clear and actionable
- Agent provides friendly confirmations for all actions

## Conversation Flow

The system operates in a stateless request cycle:

1. Receive user message
2. Fetch conversation history from database
3. Build message array for agent (history + new message)
4. Store user message in database
5. Run agent with MCP tools available
6. Agent invokes appropriate MCP tool(s)
7. Store assistant response in database
8. Return response to client
9. Server holds NO state (ready for next request)

## Assumptions

- Task storage mechanism already exists (database or file-based)
- User authentication is handled by calling application
- Each user has isolated task list (user_id scoping)
- Tasks have at minimum: id, user_id, title, description, completed fields
- Agent SDK integration already exists
- STDIO transport will be used for MCP communication

## Out of Scope

- Task priorities or due dates
- Task categories or tags
- Recurring tasks
- Task notifications or reminders
- Task sharing between users
- Advanced search or filtering beyond status
- Task history or audit logs
- Authentication/authorization (handled externally)
- Task attachments or comments
