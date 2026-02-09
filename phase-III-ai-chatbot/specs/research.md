# Research & Technology Decisions: AI-Powered Conversational Task Management

**Date**: 2026-02-09
**Phase**: 0 (Research)
**Plan Reference**: [plan.md](./plan.md)

## Overview

This document captures research findings and technology decisions for implementing the AI-powered conversational task management system. All decisions are based on requirements from the feature specification and align with Phase III constitutional requirements.

---

## R1: OpenAI Agents SDK Integration

### Research Question
How to configure OpenAI Agents SDK for task management with MCP tools?

### Research Findings

**OpenAI Agents SDK Overview**:
- Provides high-level abstraction for building AI agents with tool use
- Supports function calling with structured tool definitions
- Handles conversation context and multi-turn interactions
- Built on top of OpenAI Chat Completions API
- Supports streaming and non-streaming responses

**Agent Configuration Pattern**:
```python
from openai import OpenAI
from openai.agents import Agent

agent = Agent(
    name="TaskManagementAgent",
    instructions="You are a helpful assistant that manages todo tasks...",
    tools=[add_task_tool, list_tasks_tool, ...],
    model="gpt-4o-mini"  # Cost-effective for task management
)
```

**Tool Registration**:
- Tools defined as Python functions with type hints
- Automatic schema generation from function signatures
- Support for async tool execution
- Error handling through exceptions

**Context Management**:
- Agent maintains conversation history internally
- Can be initialized with previous messages for stateless operation
- Context window management handled automatically
- Token counting available for cost monitoring

### Decision

**Use OpenAI Agents SDK with stateless initialization pattern**

### Rationale

1. **Ease of MCP Tool Integration**: Agent SDK supports function-based tools that align well with MCP tool pattern
2. **Stateless Operation**: Can initialize agent with conversation history from database on each request
3. **Performance**: gpt-4o-mini provides good balance of accuracy and latency
4. **Error Handling**: Built-in exception handling and retry logic
5. **Maintenance**: Official SDK with ongoing support and updates

### Alternatives Considered

**Alternative 1: Direct OpenAI Chat Completions API**
- Pros: More control, lower-level access
- Cons: Manual tool calling logic, more complex implementation
- Rejected: Agent SDK provides needed abstractions without sacrificing flexibility

**Alternative 2: LangChain Agents**
- Pros: Rich ecosystem, many integrations
- Cons: Heavier dependency, more complex than needed
- Rejected: Overkill for our use case, prefer official SDK

**Alternative 3: Custom Agent Implementation**
- Pros: Full control, no external dependencies
- Cons: Significant development effort, reinventing wheel
- Rejected: Not justified given SDK availability

### Implementation Notes

1. **Model Selection**: Use `gpt-4o-mini` for cost efficiency (90% cheaper than GPT-4)
2. **Streaming**: Start with non-streaming for simplicity, add streaming if latency issues
3. **Context Window**: Limit conversation history to last 20 messages to control costs
4. **Error Handling**: Wrap agent calls in try-except with fallback responses
5. **Prompt Engineering**: Include few-shot examples in system instructions

### Risks and Mitigations

**Risk**: OpenAI API rate limits
**Mitigation**: Implement exponential backoff, monitor rate limit headers

**Risk**: Token costs exceed budget
**Mitigation**: Set max_tokens limits, monitor usage, implement conversation pruning

**Risk**: Agent SDK breaking changes
**Mitigation**: Pin SDK version, test upgrades in staging

---

## R2: MCP Server Architecture

### Research Question
How to implement MCP server with Official MCP SDK in FastAPI?

### Research Findings

**MCP (Model Context Protocol) Overview**:
- Standard protocol for AI-tool integration
- Defines tool schemas, invocation patterns, and response formats
- Official SDK provides Python implementation
- Supports both synchronous and asynchronous tools
- JSON-RPC based communication

**Integration Patterns**:

**Pattern 1: Embedded MCP Server**
- MCP server runs within FastAPI process
- Tools called directly as Python functions
- No network overhead
- Simpler deployment

**Pattern 2: Separate MCP Server Process**
- MCP server as standalone service
- Communication via HTTP or IPC
- Better isolation
- More complex deployment

**Tool Definition Schema**:
```python
{
    "name": "add_task",
    "description": "Create a new task",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "title": {"type": "string"}
        },
        "required": ["user_id", "title"]
    }
}
```

**Database Access in Tools**:
- Tools need database connection for task operations
- Options: Dependency injection, global connection pool, context managers
- Must handle transactions and error rollback

### Decision

**Implement embedded MCP server within FastAPI with dependency injection for database access**

### Rationale

1. **Simplicity**: Single process deployment, no inter-process communication
2. **Performance**: Direct function calls, no network overhead
3. **Development**: Easier debugging and testing
4. **Compatibility**: FastAPI's dependency injection works well with tool functions
5. **Scalability**: Can scale horizontally by running multiple FastAPI instances

### Alternatives Considered

**Alternative 1: Separate MCP Server Process**
- Pros: Better isolation, independent scaling
- Cons: Added complexity, network latency, deployment overhead
- Rejected: Premature optimization, embedded approach sufficient for Phase III

**Alternative 2: MCP Server as Sidecar Container**
- Pros: Kubernetes-native pattern, resource isolation
- Cons: Overkill for Phase III, adds deployment complexity
- Rejected: Reserved for Phase IV (Kubernetes deployment)

### Implementation Notes

1. **Tool Registration**: Register all 5 tools at FastAPI startup
2. **Database Connections**: Use FastAPI dependency injection for SQLModel sessions
3. **Error Handling**: Tools return structured error responses, not exceptions
4. **Validation**: Use Pydantic models for parameter validation
5. **Testing**: Each tool has unit tests with mocked database
6. **Logging**: Log all tool invocations with parameters and results

### Risks and Mitigations

**Risk**: Tool execution failures break conversation
**Mitigation**: Comprehensive error handling, graceful degradation

**Risk**: Database connection pool exhaustion
**Mitigation**: Configure appropriate pool size, implement connection timeouts

**Risk**: Tool parameter validation failures
**Mitigation**: Pydantic validation with clear error messages

---

## R3: OpenAI ChatKit Integration

### Research Question
How to integrate OpenAI ChatKit with custom backend?

### Research Findings

**OpenAI ChatKit Overview**:
- Pre-built React chat UI component library
- Designed for OpenAI API integration
- Supports custom backend endpoints
- Mobile-responsive design
- Accessibility features built-in

**Configuration Requirements**:
1. **Domain Allowlist**: Must register production domain at OpenAI platform
2. **Domain Key**: Obtained after domain registration
3. **API Endpoint**: Configure custom backend URL
4. **Authentication**: Pass auth tokens in headers

**Setup Process**:
```typescript
import { ChatKit } from '@openai/chatkit';

<ChatKit
  apiEndpoint="https://api.yourdomain.com/chat"
  domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
  authToken={userAuthToken}
/>
```

**Message Format**:
- ChatKit expects specific message structure
- Supports text, tool calls, and metadata
- Handles typing indicators automatically
- Auto-scrolling and history management

**Customization Options**:
- Theme customization (colors, fonts)
- Custom message renderers
- Action buttons and quick replies
- File upload support (not needed for Phase III)

### Decision

**Use OpenAI ChatKit with custom backend integration and domain allowlist configuration**

### Rationale

1. **Development Speed**: Pre-built UI saves significant frontend development time
2. **Quality**: Production-ready with accessibility and mobile support
3. **Maintenance**: Official component with ongoing updates
4. **User Experience**: Familiar chat interface pattern
5. **Integration**: Straightforward custom backend integration

### Alternatives Considered

**Alternative 1: Custom React Chat UI**
- Pros: Full control, no external dependencies
- Cons: Significant development effort, need to handle accessibility, mobile, etc.
- Rejected: Not justified given ChatKit availability

**Alternative 2: Third-party Chat Libraries (react-chat-widget, etc.)**
- Pros: Open source, customizable
- Cons: Less maintained, may lack features, not optimized for AI chat
- Rejected: ChatKit better suited for AI conversations

**Alternative 3: Headless Chat Logic + Custom UI**
- Pros: Maximum flexibility
- Cons: Most development effort, need to build all UI components
- Rejected: Overkill for Phase III requirements

### Implementation Notes

1. **Domain Allowlist**: Register domain early in development process
2. **Environment Variables**: Store domain key in .env, never commit
3. **Authentication**: Integrate with Phase II Better Auth tokens
4. **Error Handling**: Display user-friendly error messages in chat
5. **Loading States**: Show typing indicator during AI processing
6. **Mobile Testing**: Test on various screen sizes and devices

### Risks and Mitigations

**Risk**: Domain allowlist misconfiguration blocks deployment
**Mitigation**: Configure and test early, document setup process clearly

**Risk**: ChatKit breaking changes in updates
**Mitigation**: Pin version, test updates in staging environment

**Risk**: Limited customization for specific UX needs
**Mitigation**: Evaluate customization options early, have fallback plan

---

## R4: Conversation State Management

### Research Question
How to implement stateless server with database-persisted conversation state?

### Research Findings

**Stateless Architecture Benefits**:
- Horizontal scalability (any server can handle any request)
- Resilience to server restarts
- Simplified deployment and load balancing
- No session affinity required

**State Persistence Patterns**:

**Pattern 1: Full History Retrieval**
- Load entire conversation history on each request
- Simple implementation
- May be slow for long conversations

**Pattern 2: Windowed History**
- Load only recent N messages
- Better performance
- May lose context for very long conversations

**Pattern 3: Summarization + Recent Messages**
- Summarize old messages, keep recent ones verbatim
- Best of both worlds
- More complex implementation

**Database Schema Considerations**:
- Conversations table: metadata and status
- Messages table: individual messages with role and content
- Indexes on conversation_id and created_at for efficient retrieval
- JSONB for metadata (tool calls, actions)

**Query Optimization**:
- Use database connection pooling
- Index on (conversation_id, created_at) for ordered retrieval
- Limit query to recent messages with LIMIT clause
- Consider read replicas for high load

### Decision

**Implement stateless server with windowed history retrieval (last 20 messages)**

### Rationale

1. **Performance**: Limits database query size and API token usage
2. **Scalability**: Stateless design enables horizontal scaling
3. **Simplicity**: Straightforward implementation without summarization complexity
4. **Sufficient Context**: 20 messages provides adequate context for task management
5. **Cost Control**: Limits tokens sent to OpenAI API

### Alternatives Considered

**Alternative 1: Full History Retrieval**
- Pros: Complete context always available
- Cons: Performance degrades with conversation length, higher API costs
- Rejected: Not scalable for long conversations

**Alternative 2: Summarization + Recent Messages**
- Pros: Best context preservation with controlled size
- Cons: Complex implementation, summarization costs
- Rejected: Premature optimization, windowed approach sufficient

**Alternative 3: In-Memory Session State**
- Pros: Fastest access, no database queries
- Cons: Not stateless, requires session affinity, lost on restart
- Rejected: Violates stateless architecture requirement

### Implementation Notes

1. **History Window**: Start with 20 messages, make configurable
2. **Database Indexes**: Create composite index on (conversation_id, created_at DESC)
3. **Connection Pooling**: Configure SQLModel with asyncpg connection pool
4. **Caching**: Consider Redis cache for very active conversations (future optimization)
5. **Pagination**: Support pagination for viewing full history in UI
6. **Cleanup**: Implement background job to archive old conversations (90 days)

### Risks and Mitigations

**Risk**: Context loss in very long conversations
**Mitigation**: Implement conversation summarization in future phase if needed

**Risk**: Database query latency impacts response time
**Mitigation**: Proper indexing, connection pooling, monitoring

**Risk**: Concurrent message creation causes race conditions
**Mitigation**: Use database transactions, optimistic locking if needed

---

## R5: Natural Language Intent Extraction

### Research Question
How to optimize agent for task management intent recognition?

### Research Findings

**Prompt Engineering Techniques**:

**1. System Instructions**:
- Clear role definition
- Explicit capabilities and limitations
- Response format guidelines
- Error handling instructions

**2. Few-Shot Examples**:
- Provide examples of user inputs and expected tool calls
- Cover common variations and edge cases
- Include ambiguity resolution examples

**3. Tool Descriptions**:
- Clear, concise tool descriptions
- Explicit parameter requirements
- Usage examples in descriptions

**Intent Recognition Patterns**:

**Pattern 1: Direct Tool Mapping**
- User: "Add task to buy milk" → add_task tool
- Clear intent, straightforward mapping

**Pattern 2: Implicit Intent**
- User: "I need to remember to call mom" → add_task tool
- Requires understanding of implicit task creation

**Pattern 3: Ambiguous Intent**
- User: "What about the meeting?" → Needs clarification
- Multiple possible interpretations

**Pattern 4: Multi-Step Intent**
- User: "Add task and show me all tasks" → Multiple tool calls
- Requires sequential execution

**Accuracy Optimization**:
- Use specific, action-oriented tool names
- Include common phrasings in tool descriptions
- Provide examples of ambiguous cases with clarification responses
- Test with diverse user inputs

### Decision

**Use comprehensive system prompt with few-shot examples and explicit tool descriptions**

### Rationale

1. **Accuracy**: Few-shot examples significantly improve intent recognition
2. **Maintainability**: Prompt engineering easier than model fine-tuning
3. **Flexibility**: Can iterate on prompts without retraining
4. **Cost**: No fine-tuning costs, only inference costs
5. **Transparency**: Prompt logic is visible and debuggable

### System Prompt Template

```
You are a helpful task management assistant. You help users manage their todo tasks through natural conversation.

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
- Handle multiple tasks in one request when clear

EXAMPLES:
User: "Add a task to buy groceries"
Action: Call add_task with title="Buy groceries"

User: "What do I need to do?"
Action: Call list_tasks with status="pending"

User: "I finished the report"
Action: Search for task matching "report", then call complete_task

User: "Delete the old tasks"
Action: Ask for clarification about which tasks to delete

When unsure, always ask for clarification rather than guessing.
```

### Alternatives Considered

**Alternative 1: Fine-tuned Model**
- Pros: Potentially higher accuracy for specific domain
- Cons: High cost, maintenance burden, less flexible
- Rejected: Prompt engineering sufficient for Phase III

**Alternative 2: Rule-Based Intent Classification**
- Pros: Deterministic, fast, no API costs
- Cons: Brittle, hard to maintain, poor handling of variations
- Rejected: LLM-based approach more robust

**Alternative 3: Hybrid (Rules + LLM)**
- Pros: Fast path for common cases, LLM for complex cases
- Cons: Added complexity, two systems to maintain
- Rejected: Premature optimization

### Implementation Notes

1. **Prompt Versioning**: Store prompts in configuration, version control
2. **A/B Testing**: Support multiple prompt variants for testing
3. **Monitoring**: Log intent recognition accuracy, track failure cases
4. **Feedback Loop**: Collect user corrections to improve prompts
5. **Fallback**: Always provide helpful response when intent unclear

### Risks and Mitigations

**Risk**: Intent accuracy below 90% target
**Mitigation**: Iterate on prompts, add more examples, monitor and improve

**Risk**: Prompt injection attacks
**Mitigation**: Input validation, sanitization, rate limiting

**Risk**: Inconsistent responses across requests
**Mitigation**: Use temperature=0 for deterministic outputs

---

## R6: Integration with Phase II Systems

### Research Question
How to integrate with existing Phase II authentication and task database?

### Research Findings

**Phase II Architecture Review**:
- Backend: FastAPI with Better Auth
- Database: Neon PostgreSQL with SQLModel
- Authentication: Better Auth with JWT tokens
- Task Model: Existing tasks table with user_id, title, description, status

**Integration Points**:

**1. Authentication**:
- Reuse Better Auth middleware
- Extract user_id from JWT token
- Pass user_id to MCP tools for authorization

**2. Task Database**:
- Reuse existing tasks table
- No schema changes needed for basic operations
- May add indexes for chat-specific queries

**3. API Endpoints**:
- New /api/chat endpoint alongside existing task endpoints
- Shared authentication middleware
- Consistent error handling patterns

**Database Schema Extensions**:
- Add conversations table (new)
- Add messages table (new)
- Foreign key from conversations.user_id to users table
- No changes to existing tasks table

**Code Reuse Opportunities**:
- Task service layer for CRUD operations
- Database connection management
- Authentication middleware
- Error handling utilities
- Logging and monitoring setup

### Decision

**Extend Phase II system with new chat endpoint and conversation tables, reuse authentication and task services**

### Rationale

1. **Consistency**: Maintains architectural patterns from Phase II
2. **Code Reuse**: Leverages existing services and infrastructure
3. **Data Integrity**: Single source of truth for tasks
4. **Security**: Consistent authentication and authorization
5. **Maintainability**: Unified codebase, shared utilities

### Integration Architecture

```
Phase II (Existing)          Phase III (New)
┌─────────────────┐         ┌──────────────────┐
│ Task Endpoints  │         │  Chat Endpoint   │
│ /api/tasks      │         │  /api/chat       │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         └───────────┬───────────────┘
                     │
         ┌───────────▼────────────┐
         │  Better Auth Middleware │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │   Task Service Layer   │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │   Database (Neon PG)   │
         │  - users               │
         │  - tasks               │
         │  - conversations (new) │
         │  - messages (new)      │
         └────────────────────────┘
```

### Alternatives Considered

**Alternative 1: Separate Phase III Application**
- Pros: Complete isolation, independent deployment
- Cons: Duplicate authentication, task data sync issues
- Rejected: Violates single source of truth principle

**Alternative 2: Duplicate Task Table for Chat**
- Pros: No impact on Phase II
- Cons: Data inconsistency, sync complexity
- Rejected: Violates data integrity principles

**Alternative 3: Microservices Architecture**
- Pros: Independent scaling, technology flexibility
- Cons: Overkill for current scale, added complexity
- Rejected: Premature optimization, monolith sufficient

### Implementation Notes

1. **Database Migration**: Create conversations and messages tables via Alembic
2. **Service Layer**: Create conversation_service.py, reuse task_service.py
3. **Middleware**: Reuse Better Auth middleware for /api/chat endpoint
4. **Error Handling**: Follow Phase II error response format
5. **Testing**: Integration tests verify Phase II functionality unchanged
6. **Documentation**: Update API docs to include chat endpoint

### Risks and Mitigations

**Risk**: Chat feature impacts Phase II performance
**Mitigation**: Separate database indexes, monitor query performance

**Risk**: Breaking changes to Phase II during integration
**Mitigation**: Comprehensive integration tests, feature flags

**Risk**: Authentication token compatibility issues
**Mitigation**: Use same Better Auth configuration, test thoroughly

---

## Technology Stack Summary

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (from Phase II)
- **AI Agent**: OpenAI Agents SDK with gpt-4o-mini
- **MCP**: Official MCP SDK (embedded in FastAPI)
- **ORM**: SQLModel (from Phase II)
- **Database**: Neon Serverless PostgreSQL (from Phase II)
- **Authentication**: Better Auth (from Phase II)
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: Next.js 14+ with App Router
- **UI Library**: OpenAI ChatKit
- **Language**: TypeScript
- **Styling**: Tailwind CSS (from Phase II)
- **Testing**: Jest, React Testing Library

### Infrastructure
- **Database**: Neon PostgreSQL (shared with Phase II)
- **Deployment**: Docker Compose (local), Vercel (frontend), Railway/Render (backend)
- **Monitoring**: Logging to stdout, error tracking TBD

### Development Tools
- **Package Manager**: UV (Python), npm (Node.js)
- **Code Quality**: ruff (Python), ESLint (TypeScript)
- **Version Control**: Git
- **CI/CD**: GitHub Actions (TBD)

---

## Implementation Priorities

### Phase 1 (MVP - Core Chat Functionality)
1. Database schema (conversations, messages)
2. MCP server with 5 tools
3. OpenAI Agent configuration
4. Chat API endpoint
5. Basic ChatKit integration
6. Authentication integration

### Phase 2 (Polish & Testing)
1. Comprehensive testing (unit, integration, contract)
2. Error handling and edge cases
3. Rate limiting and input validation
4. Performance optimization
5. Documentation

### Phase 3 (Deployment & Monitoring)
1. Docker Compose setup
2. Production deployment
3. Monitoring and logging
4. User feedback collection
5. Iteration based on usage

---

## Open Questions

### Q1: OpenAI API Key Management
**Question**: How to securely manage OpenAI API keys?
**Options**:
- Environment variables (simple, standard)
- Secret management service (more secure, complex)
**Recommendation**: Start with environment variables, migrate to secret manager for production

### Q2: Conversation Archival Strategy
**Question**: How to handle 90-day conversation retention?
**Options**:
- Background job to delete old conversations
- Soft delete with archived status
- Move to cold storage
**Recommendation**: Soft delete with archived status, implement background cleanup job

### Q3: Rate Limiting Strategy
**Question**: What rate limits to apply to chat endpoint?
**Options**:
- Per-user limits (10 messages/minute)
- Global limits (1000 messages/minute)
- Adaptive limits based on load
**Recommendation**: Start with per-user limits (10/min), monitor and adjust

### Q4: Error Message Localization
**Question**: Should error messages support multiple languages?
**Options**:
- English only (Phase III scope)
- Multi-language support (future phase)
**Recommendation**: English only for Phase III, design for future localization

---

## Conclusion

All research tasks completed with clear decisions and rationale. Technology stack aligns with Phase III constitutional requirements and integrates well with Phase II systems. Ready to proceed to Phase 1 (Design & Contracts).

**Next Steps**:
1. Generate data-model.md with complete database schema
2. Generate API contracts (chat-api.yaml, mcp-tools.json)
3. Generate quickstart.md with setup instructions
4. Update agent context files

**Research Status**: ✅ Complete
**Blockers**: None
**Ready for Phase 1**: Yes
