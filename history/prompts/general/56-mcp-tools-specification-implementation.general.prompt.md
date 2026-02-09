---
id: 56
title: MCP Tools Specification and Implementation
stage: general
date: 2026-02-10
surface: agent
model: claude-sonnet-4-5
feature: mcp-tools
branch: main
user: AmanNazim
command: specification-implementation
labels: ["mcp-tools", "mcp-sdk", "task-management", "specification", "implementation", "agent-sdk"]
links:
  spec: phase-III-ai-chatbot/specs/mcp-tools/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - phase-III-ai-chatbot/specs/mcp-tools/spec.md
  - phase-III-ai-chatbot/specs/mcp-tools/plan.md
  - phase-III-ai-chatbot/specs/mcp-tools/tasks.md
  - phase-III-ai-chatbot/specs/mcp-tools/README.md
  - phase-III-ai-chatbot/backend/src/mcp/tools/complete_task.py
  - phase-III-ai-chatbot/backend/src/mcp/tools/delete_task.py
  - phase-III-ai-chatbot/backend/src/mcp/tools/update_task.py
  - phase-III-ai-chatbot/backend/src/services/task_service.py
tests:
  - Manual verification of tool signatures
  - Schema validation for integer task_id
  - Return format validation
---

## Prompt

I want you to create simple yet proper spec, plan and task for mcp tool in separate mcp-tools folder inside specs folder and implement all tasks using mcp-sdk skill, I know you have implemented mcp and tools so we will update them using specs, don't go advance just fulfill the requirements of docs which is this: MCP Tools Specification

The MCP server must expose the following tools for the AI agent:

**Tool: add_task**
- Purpose: Create a new task
- Parameters: user_id (string, required), title (string, required), description (string, optional)
- Returns: task_id, status, title
- Example Input: {"user_id": "ziakhan", "title": "Buy groceries", "description": "Milk, eggs, bread"}
- Example Output: {"task_id": 5, "status": "created", "title": "Buy groceries"}

**Tool: list_tasks**
- Purpose: Retrieve tasks from the list
- Parameters: user_id (string, required), status (string, optional: "all", "pending", "completed")
- Returns: Array of task objects
- Example Input: {"user_id": "ziakhan", "status": "pending"}
- Example Output: [{"id": 1, "title": "Buy groceries", "completed": false}, ...]

**Tool: complete_task**
- Purpose: Mark a task as complete
- Parameters: user_id (string, required), task_id (integer, required)
- Returns: task_id, status, title
- Example Input: {"user_id": "ziakhan", "task_id": 3}
- Example Output: {"task_id": 3, "status": "completed", "title": "Call mom"}

**Tool: delete_task**
- Purpose: Remove a task from the list
- Parameters: user_id (string, required), task_id (integer, required)
- Returns: task_id, status, title
- Example Input: {"user_id": "ziakhan", "task_id": 2}
- Example Output: {"task_id": 2, "status": "deleted", "title": "Old task"}

**Tool: update_task**
- Purpose: Modify task title or description
- Parameters: user_id (string, required), task_id (integer, required), title (string, optional), description (string, optional)
- Returns: task_id, status, title
- Example Input: {"user_id": "ziakhan", "task_id": 1, "title": "Buy groceries and fruits"}
- Example Output: {"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}

Agent Behavior: Natural language understanding, conversation flow (stateless request cycle), error handling.

Consider yourself SENIOR EXPERT PYTHON MCP SDK ENGINEER with expertise in MCP SDK, PYTHON and MCP TOOLS CREATION, and implement on existing mcp folder don't duplicate.

## Response snapshot

Successfully created MCP tools specification, plan, tasks, and updated existing implementation to match requirements:

**Specification Created** (`specs/mcp-tools/spec.md`):
- 7 functional requirements covering all 5 tools
- Natural language understanding requirements
- Error handling specifications
- Conversation flow documentation
- Success criteria and acceptance criteria
- Clear scope boundaries

**Plan Created** (`specs/mcp-tools/plan.md`):
- Technical approach using existing MCP structure
- Integration strategy with TaskService
- Tool schema definitions
- Error handling patterns
- File structure and organization
- Testing strategy
- Risk mitigation

**Tasks Created** (`specs/mcp-tools/tasks.md`):
- 9 implementation tasks with acceptance criteria
- Task dependencies clearly defined
- Test cases for each task
- Success criteria checklist

**Implementation Updates**:

1. **Updated complete_task.py**:
   - Changed task_id parameter from string to integer
   - Updated schema to use "integer" type
   - Matches specification exactly

2. **Updated delete_task.py**:
   - Changed task_id parameter from string to integer
   - Updated schema to use "integer" type
   - Matches specification exactly

3. **Updated update_task.py**:
   - Changed task_id parameter from string to integer
   - Updated schema to use "integer" type
   - Matches specification exactly

4. **Updated task_service.py**:
   - Updated create_task to return integer task_id (not UUID string)
   - Updated list_tasks to return integer id and completed field
   - Updated complete_task to accept integer task_id
   - Updated delete_task to accept integer task_id
   - Updated update_task to accept integer task_id
   - All methods now match specification requirements

**Documentation Created** (`specs/mcp-tools/README.md`):
- Complete tool documentation with examples
- Natural language trigger examples
- Agent integration explanation
- Error handling guide
- Testing instructions
- Troubleshooting section

**Key Changes from Existing Implementation**:
- task_id changed from string (UUID) to integer across all tools
- list_tasks return format simplified to match spec (id, title, completed)
- All tool signatures now exactly match specification
- Mock responses updated to use integer IDs

## Outcome

- ✅ Impact: Created comprehensive MCP tools specification, plan, and tasks documentation. Updated existing MCP tool implementations to match exact specification requirements. All 5 tools (add_task, list_tasks, complete_task, delete_task, update_task) now use integer task_id and return formats matching specification. Documentation provides complete guide for usage, testing, and troubleshooting.
- 🧪 Tests: Manual verification completed - all tool signatures updated, schemas validated for integer task_id, return formats match specification exactly.
- 📁 Files: Created 4 new files (spec.md, plan.md, tasks.md, README.md) and updated 4 existing files (complete_task.py, delete_task.py, update_task.py, task_service.py).
- 🔁 Next prompts: Potential next steps include: (1) Integrate with actual Phase II task database (currently using mock data), (2) Add comprehensive unit tests for all tools, (3) Test with MCP Inspector, (4) Test natural language commands with Agent SDK, (5) Add error handling for edge cases.
- 🧠 Reflection: Successfully aligned existing MCP tools implementation with detailed specification requirements. The main change was switching from string UUIDs to integer task_ids throughout the system. The specification provides clear requirements, the plan explains technical approach, tasks break down implementation steps, and documentation enables easy usage and troubleshooting. The existing MCP structure was well-designed and only needed parameter type updates to match the specification.

## Evaluation notes (flywheel)

- Failure modes observed: None - existing implementation was well-structured and only needed type updates to match specification.
- Graders run and results (PASS/FAIL): Manual validation PASS - all tool signatures updated correctly, schemas use integer type, return formats match specification, documentation is comprehensive and accurate.
- Prompt variant (if applicable): Standard specification-plan-tasks-implementation workflow with focus on updating existing code rather than creating from scratch.
- Next experiment (smallest change to try): Test the updated tools with MCP Inspector to verify integer task_id handling works correctly in practice, then integrate with actual database to replace mock responses.
