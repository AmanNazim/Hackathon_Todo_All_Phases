# Implementation Plan: AI-Powered Conversational Task Management

**Branch**: `main/phase-III-ai-chatbot` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `phase-III-ai-chatbot/specs/spec.md`

## Summary

Implement an AI-powered chatbot interface that enables users to manage todo tasks through natural language conversations. The system uses OpenAI Agents SDK for natural language understanding, MCP (Model Context Protocol) server architecture for tool-based task operations, and maintains stateless server design with database-persisted conversation state. Users can create, list, update, complete, and delete tasks through conversational commands while the system maintains context across sessions.

**Technical Approach**: Build a three-tier architecture with OpenAI ChatKit frontend, FastAPI backend hosting both chat endpoint and MCP server, and Neon PostgreSQL for persistent storage. The AI agent uses MCP tools as standardized interfaces for task operations, enabling composable and testable task management capabilities through natural language.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js (frontend with ChatKit)
**Primary Dependencies**:
- Backend: FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, asyncpg
- Frontend: OpenAI ChatKit, Next.js, React, Tailwind CSS
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (from Phase II)

**Storage**: Neon Serverless PostgreSQL (conversations, messages, tasks)
**Testing**: pytest (backend), Jest/React Testing Library (frontend), MCP tool testing
**Target Platform**: Web application (desktop and mobile browsers)
**Project Type**: Web (frontend + backend + MCP server)
**Performance Goals**:
- 95% of AI responses within 3 seconds
- 90% intent interpretation accuracy
- Support 100+ concurrent chat sessions
- Database query latency <100ms p95

**Constraints**:
- Stateless server architecture (no in-memory session state)
- Message length limit: 1000 characters
- Conversation history retention: 90 days
- English language only (initial release)
- Must integrate with Phase II authentication and task system

**Scale/Scope**:
- Support 1000+ active users
- Handle 10,000+ messages per day
- Maintain 50 active conversations per user
- 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III — AI-Powered Todo Chatbot Rules Compliance

✅ **Natural language processing integration**: OpenAI Agents SDK provides NLP capabilities
✅ **AI agent implementation for todo management**: Agent uses MCP tools for task operations
✅ **Conversational interface design**: OpenAI ChatKit provides chat UI
✅ **Intent recognition and command parsing**: Agent SDK handles intent extraction
✅ **Context preservation across sessions**: Database-persisted conversation history
✅ **Safety and guardrail implementation**: Input validation, rate limiting, authentication
✅ **NLP and command grammar rules**: Agent SDK with structured tool definitions
✅ **Integration with previous phases**: Uses Phase II authentication and task database
✅ **Adaptive learning capabilities**: Agent improves with usage patterns (future enhancement)
✅ **Conversational state management**: Stateless server with database state persistence

### Cross-Phase Compliance

✅ **Spec-Driven Development**: Following Specification → Plan → Tasks → Implementation
✅ **Claude Code Usage**: All code generated through Claude Code
✅ **Technology Stack Constraints**: Using approved technologies (Python, FastAPI, PostgreSQL)
✅ **Code Quality Principles**: OOP, domain-driven design, proper testing
✅ **Repository Structure**: Following established directory patterns
✅ **No Prohibited Actions**: No manual coding, no unauthorized technologies

### Potential Violations

None identified. All Phase III requirements can be met within constitutional constraints.

## Project Structure

### Documentation (this feature)

```text
phase-III-ai-chatbot/specs/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Database schema and entities
├── quickstart.md        # Phase 1: Setup and development guide
├── contracts/           # Phase 1: API contracts and MCP tool definitions
│   ├── chat-api.yaml    # Chat endpoint OpenAPI spec
│   └── mcp-tools.json   # MCP tool definitions
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2: Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
phase-III-ai-chatbot/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py           # Chat endpoint
│   │   │   └── middleware.py     # Auth, rate limiting
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── task_agent.py     # OpenAI Agent configuration
│   │   │   └── runner.py         # Agent execution logic
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   ├── server.py         # MCP server implementation
│   │   │   └── tools/
│   │   │       ├── __init__.py
│   │   │       ├── add_task.py
│   │   │       ├── list_tasks.py
│   │   │       ├── complete_task.py
│   │   │       ├── delete_task.py
│   │   │       └── update_task.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py   # Conversation model
│   │   │   ├── message.py        # Message model
│   │   │   └── task.py           # Task model (from Phase II)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── conversation_service.py
│   │   │   └── task_service.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   └── migrations/
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   └── main.py               # FastAPI application
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_mcp_tools.py
│   │   │   ├── test_agent.py
│   │   │   └── test_services.py
│   │   ├── integration/
│   │   │   ├── test_chat_api.py
│   │   │   └── test_conversation_flow.py
│   │   └── contract/
│   │       └── test_mcp_contracts.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── chat/
│   │   │   │   └── page.tsx      # Chat interface page
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   └── TypingIndicator.tsx
│   │   │   └── ui/
│   │   ├── hooks/
│   │   │   ├── useChat.ts
│   │   │   └── useConversation.ts
│   │   ├── services/
│   │   │   └── chatApi.ts
│   │   ├── types/
│   │   │   └── chat.ts
│   │   └── utils/
│   ├── public/
│   ├── tests/
│   │   ├── components/
│   │   └── integration/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── README.md
├── docs/
│   ├── architecture.md           # System architecture overview
│   ├── mcp-integration.md        # MCP server integration guide
│   ├── agent-configuration.md    # OpenAI Agent setup
│   └── deployment.md             # Deployment instructions
├── docker-compose.yml            # Local development setup
├── .env.example
└── README.md                     # Project overview
```

**Structure Decision**: Web application structure with separate backend and frontend directories. Backend contains FastAPI server with integrated MCP server and OpenAI Agent. Frontend uses Next.js with OpenAI ChatKit for chat interface. This structure maintains clear separation of concerns while enabling tight integration between chat endpoint, AI agent, and MCP tools.

## Complexity Tracking

No constitutional violations requiring justification. All requirements align with Phase III rules and cross-phase constraints.

---

## Phase 0: Research & Technology Decisions

### Research Tasks

#### R1: OpenAI Agents SDK Integration
**Question**: How to configure OpenAI Agents SDK for task management with MCP tools?
**Research Areas**:
- Agent configuration and initialization
- Tool registration and invocation patterns
- Context management across turns
- Error handling and fallback strategies
- Streaming vs non-streaming responses

**Decision Criteria**:
- Ease of MCP tool integration
- Support for stateless operation
- Performance characteristics
- Error handling capabilities

#### R2: MCP Server Architecture
**Question**: How to implement MCP server with Official MCP SDK in FastAPI?
**Research Areas**:
- MCP SDK installation and setup
- Tool definition schema and validation
- Integration with FastAPI endpoints
- Stateless tool execution patterns
- Database connection management in tools

**Decision Criteria**:
- Compatibility with FastAPI
- Tool composability
- Testing capabilities
- Performance overhead

#### R3: OpenAI ChatKit Integration
**Question**: How to integrate OpenAI ChatKit with custom backend?
**Research Areas**:
- ChatKit configuration and setup
- Domain allowlist requirements
- Custom API endpoint integration
- Message formatting and display
- Authentication integration

**Decision Criteria**:
- Ease of backend integration
- Customization capabilities
- Mobile responsiveness
- Accessibility features

#### R4: Conversation State Management
**Question**: How to implement stateless server with database-persisted conversation state?
**Research Areas**:
- Conversation and message schema design
- Efficient history retrieval patterns
- Context window management
- State synchronization strategies
- Performance optimization for history queries

**Decision Criteria**:
- Query performance
- Scalability
- Data consistency
- Recovery capabilities

#### R5: Natural Language Intent Extraction
**Question**: How to optimize agent for task management intent recognition?
**Research Areas**:
- Prompt engineering for task operations
- Few-shot examples for intent clarity
- Ambiguity resolution strategies
- Confirmation patterns
- Error message design

**Decision Criteria**:
- Intent accuracy (target: 90%)
- Response quality
- User experience
- Maintainability

#### R6: Integration with Phase II Systems
**Question**: How to integrate with existing Phase II authentication and task database?
**Research Areas**:
- Better Auth integration patterns
- Task model compatibility
- Database schema extensions
- API endpoint reuse vs new endpoints
- Migration strategies

**Decision Criteria**:
- Minimal disruption to Phase II
- Code reuse opportunities
- Data consistency
- Security alignment

### Research Outputs

Research findings will be documented in `research.md` with the following structure:
- **Decision**: Technology/approach chosen
- **Rationale**: Why this choice was made
- **Alternatives Considered**: Other options evaluated
- **Implementation Notes**: Key considerations for implementation
- **Risks and Mitigations**: Potential issues and solutions

---

## Phase 1: Design & Contracts

### Phase 1.1: Data Model Design

**Output**: `data-model.md`

#### Entities

**Conversation**
- `id` (UUID, primary key)
- `user_id` (string, foreign key to Phase II users)
- `status` (enum: active, archived)
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Relationships**: One-to-many with Message

**Validation Rules**:
- user_id must reference existing user
- status must be valid enum value
- created_at <= updated_at

**State Transitions**: active → archived (one-way)

**Message**
- `id` (UUID, primary key)
- `conversation_id` (UUID, foreign key to Conversation)
- `user_id` (string, foreign key to Phase II users)
- `role` (enum: user, assistant)
- `content` (text, max 1000 chars for user, unlimited for assistant)
- `metadata` (JSONB, optional - tool calls, actions)
- `created_at` (timestamp)

**Relationships**: Many-to-one with Conversation

**Validation Rules**:
- conversation_id must reference existing conversation
- user_id must match conversation.user_id
- role must be valid enum value
- content length validation based on role
- metadata must be valid JSON

**Task (existing from Phase II, referenced)**
- `id` (UUID, primary key)
- `user_id` (string, foreign key)
- `title` (string, required)
- `description` (text, optional)
- `status` (enum: pending, completed)
- `created_at` (timestamp)
- `updated_at` (timestamp)
- `completed_at` (timestamp, optional)

**Relationships**: Referenced by MCP tools, not directly linked to conversations

#### Database Indexes

- `conversations.user_id` (B-tree) - for user conversation lookup
- `conversations.updated_at` (B-tree) - for recent conversation queries
- `messages.conversation_id` (B-tree) - for message history retrieval
- `messages.created_at` (B-tree) - for chronological ordering
- `tasks.user_id, tasks.status` (composite B-tree) - for filtered task queries

#### Data Retention

- Conversations: 90 days from last update
- Messages: Cascade delete with conversation
- Tasks: Managed by Phase II retention policy

### Phase 1.2: API Contracts

**Output**: `contracts/chat-api.yaml` (OpenAPI), `contracts/mcp-tools.json` (MCP tool definitions)

#### Chat API Endpoint

**POST /api/chat**

Request:
```json
{
  "conversation_id": "uuid | null",
  "message": "string (max 1000 chars)"
}
```

Response:
```json
{
  "conversation_id": "uuid",
  "response": "string",
  "tool_calls": [
    {
      "tool": "string",
      "parameters": "object",
      "result": "object"
    }
  ],
  "created_at": "timestamp"
}
```

Error Responses:
- 400: Invalid request (message too long, invalid conversation_id)
- 401: Unauthorized (missing or invalid authentication)
- 429: Rate limit exceeded
- 500: Internal server error

#### MCP Tool Contracts

**Tool: add_task**
```json
{
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
  },
  "returns": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "status": {"type": "string", "enum": ["created"]},
      "title": {"type": "string"}
    }
  }
}
```

**Tool: list_tasks**
```json
{
  "name": "list_tasks",
  "description": "Retrieve user's tasks with optional status filter",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string", "description": "User identifier"},
      "status": {"type": "string", "enum": ["all", "pending", "completed"], "default": "all"}
    },
    "required": ["user_id"]
  },
  "returns": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "status": {"type": "string"},
        "created_at": {"type": "string"}
      }
    }
  }
}
```

**Tool: complete_task**
```json
{
  "name": "complete_task",
  "description": "Mark a task as completed",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string", "description": "User identifier"},
      "task_id": {"type": "string", "description": "Task identifier"}
    },
    "required": ["user_id", "task_id"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "status": {"type": "string", "enum": ["completed"]},
      "title": {"type": "string"}
    }
  }
}
```

**Tool: delete_task**
```json
{
  "name": "delete_task",
  "description": "Remove a task from the user's list",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string", "description": "User identifier"},
      "task_id": {"type": "string", "description": "Task identifier"}
    },
    "required": ["user_id", "task_id"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "status": {"type": "string", "enum": ["deleted"]},
      "title": {"type": "string"}
    }
  }
}
```

**Tool: update_task**
```json
{
  "name": "update_task",
  "description": "Modify task title or description",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string", "description": "User identifier"},
      "task_id": {"type": "string", "description": "Task identifier"},
      "title": {"type": "string", "description": "New task title (optional)"},
      "description": {"type": "string", "description": "New task description (optional)"}
    },
    "required": ["user_id", "task_id"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "status": {"type": "string", "enum": ["updated"]},
      "title": {"type": "string"}
    }
  }
}
```

### Phase 1.3: Quickstart Guide

**Output**: `quickstart.md`

Content will include:
- Prerequisites (Python 3.11+, Node.js 18+, PostgreSQL)
- Environment setup (.env configuration)
- Database initialization (migrations)
- Backend setup (dependencies, MCP server, agent configuration)
- Frontend setup (ChatKit configuration, domain allowlist)
- Running locally (docker-compose or manual)
- Testing the chat interface
- Common troubleshooting

### Phase 1.4: Agent Context Update

Run agent context update script to add Phase III technologies to appropriate agent context files.

---

## Phase 2: Task Generation

**Note**: Phase 2 (task generation) is handled by the `/sp.tasks` command, not by `/sp.plan`.

The tasks will be generated based on this plan and will include:
- Database schema creation and migrations
- MCP server implementation with 5 tools
- OpenAI Agent configuration and integration
- Chat API endpoint implementation
- Conversation and message services
- Frontend ChatKit integration
- Authentication and authorization
- Rate limiting and input validation
- Testing (unit, integration, contract)
- Documentation
- Deployment configuration

---

## Architecture Decisions

### AD1: Stateless Server with Database State
**Decision**: Implement stateless FastAPI server with all conversation state in PostgreSQL
**Rationale**: Enables horizontal scaling, resilience to restarts, and simplified deployment
**Trade-offs**: Slightly higher latency for history retrieval vs in-memory state
**Mitigation**: Database indexing, connection pooling, efficient query patterns

### AD2: MCP Tools as Abstraction Layer
**Decision**: Use MCP server to expose task operations as standardized tools
**Rationale**: Provides composable, testable interface for AI agent; enables tool reuse
**Trade-offs**: Additional abstraction layer adds complexity
**Mitigation**: Clear tool contracts, comprehensive testing, good documentation

### AD3: Single Endpoint for Chat
**Decision**: Single POST /api/chat endpoint handles all conversation interactions
**Rationale**: Simplifies API surface, agent handles routing to appropriate tools
**Trade-offs**: Less explicit than separate endpoints per operation
**Mitigation**: Clear API documentation, comprehensive error handling

### AD4: OpenAI ChatKit for Frontend
**Decision**: Use OpenAI ChatKit instead of custom chat UI
**Rationale**: Production-ready chat interface, reduces frontend development time
**Trade-offs**: Requires domain allowlist configuration, less customization
**Mitigation**: Follow ChatKit setup guide, configure domain allowlist early

### AD5: Integration with Phase II Systems
**Decision**: Reuse Phase II authentication and task database, extend with new tables
**Rationale**: Maintains consistency, avoids duplication, leverages existing infrastructure
**Trade-offs**: Dependency on Phase II schema and APIs
**Mitigation**: Clear interface boundaries, database migrations for extensions

---

## Risk Analysis

### Risk 1: AI Response Latency
**Impact**: High - Affects user experience (target: 95% < 3s)
**Probability**: Medium
**Mitigation**:
- Optimize database queries with proper indexing
- Use connection pooling
- Implement response streaming if needed
- Monitor and alert on p95 latency

### Risk 2: Intent Interpretation Accuracy
**Impact**: High - Core functionality (target: 90% accuracy)
**Probability**: Medium
**Mitigation**:
- Comprehensive prompt engineering
- Few-shot examples in agent configuration
- Fallback to clarification questions
- User feedback mechanism for improvements

### Risk 3: OpenAI API Costs
**Impact**: Medium - Operational costs scale with usage
**Probability**: High
**Mitigation**:
- Use efficient models (GPT-4o-mini for most operations)
- Implement conversation length limits
- Monitor token usage
- Consider caching for common queries

### Risk 4: MCP SDK Integration Complexity
**Impact**: Medium - May require custom implementation
**Probability**: Medium
**Mitigation**:
- Research MCP SDK thoroughly in Phase 0
- Start with simple tool implementation
- Build comprehensive tests
- Document integration patterns

### Risk 5: ChatKit Domain Allowlist Configuration
**Impact**: Low - Deployment blocker if misconfigured
**Probability**: Low
**Mitigation**:
- Configure domain allowlist early in development
- Document setup process clearly
- Test with production domains before launch

---

## Success Metrics

### Development Metrics
- All 5 MCP tools implemented and tested
- 90%+ test coverage for backend services
- All API contracts validated with contract tests
- Documentation complete and reviewed

### Performance Metrics
- p95 response latency < 3 seconds
- Database query latency < 100ms p95
- Support 100+ concurrent chat sessions
- 99.9% uptime for chat endpoint

### Quality Metrics
- 90%+ intent interpretation accuracy
- <5% "I don't understand" error rate
- Zero critical security vulnerabilities
- All acceptance tests passing

---

## Next Steps

1. **Complete Phase 0 Research** (`/sp.plan` generates research.md)
   - Research OpenAI Agents SDK integration patterns
   - Research MCP SDK implementation with FastAPI
   - Research ChatKit configuration and setup
   - Document all technology decisions

2. **Complete Phase 1 Design** (`/sp.plan` generates design artifacts)
   - Create data-model.md with complete schema
   - Generate API contracts (chat-api.yaml, mcp-tools.json)
   - Write quickstart.md with setup instructions
   - Update agent context files

3. **Generate Tasks** (`/sp.tasks` command)
   - Break down implementation into actionable tasks
   - Define task dependencies and order
   - Assign acceptance criteria to each task

4. **Implementation** (`/sp.implement` or manual)
   - Execute tasks in dependency order
   - Run tests continuously
   - Update documentation as needed

---

**Plan Status**: Phase 0 and Phase 1 artifacts pending generation
**Next Command**: Continue with Phase 0 research generation
