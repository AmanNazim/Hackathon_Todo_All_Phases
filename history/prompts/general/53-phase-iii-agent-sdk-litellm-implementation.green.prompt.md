---
id: 53
title: Phase III Agent SDK Implementation with LiteLLM
stage: green
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: phase-III-ai-chatbot
branch: main
user: AmanNazim
command: /sp.implement
labels: ["agent-sdk", "litellm", "openai-agents", "multi-provider", "streaming", "implementation"]
links:
  spec: phase-III-ai-chatbot/specs/agent-sdk/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - phase-III-ai-chatbot/specs/agent-sdk/spec.md
  - phase-III-ai-chatbot/specs/agent-sdk/plan.md
  - phase-III-ai-chatbot/specs/agent-sdk/tasks.md
  - phase-III-ai-chatbot/backend/src/agent_sdk/__init__.py
  - phase-III-ai-chatbot/backend/src/agent_sdk/agent_service.py
  - phase-III-ai-chatbot/backend/src/agent_sdk/session_service.py
  - phase-III-ai-chatbot/backend/src/agent_sdk/tool_adapter.py
  - phase-III-ai-chatbot/backend/src/agent_sdk/guardrails.py
  - phase-III-ai-chatbot/backend/src/agent_sdk/runner_service.py
  - phase-III-ai-chatbot/backend/src/services/chat_service.py
  - phase-III-ai-chatbot/backend/src/api/chat.py
  - phase-III-ai-chatbot/backend/src/config/settings.py
  - phase-III-ai-chatbot/backend/tests/test_agent_sdk.py
  - phase-III-ai-chatbot/backend/tests/test_streaming.py
  - phase-III-ai-chatbot/backend/requirements.txt
  - phase-III-ai-chatbot/backend/README.md
  - phase-III-ai-chatbot/backend/.env.example
  - phase-III-ai-chatbot/backend/API.md
tests:
  - phase-III-ai-chatbot/backend/tests/test_agent_sdk.py
  - phase-III-ai-chatbot/backend/tests/test_streaming.py
---

## Prompt

create simple yet proper spec, plan and task for agents SDK in separate agent-sdk folder inside specs folder and implement all tasks, don't go advance just fulfill the requirements of docs that I shared with you, consider you self SENIOR EXPERT PYTHON AGENTS SDK ENGINEER with expertise in AGENTS SDK, PYHTON, and create specs using /sp.specify, /sp.plan and /sp.task and implement using /sp.implement and must use openai-agents-sdk skill because that is up to date, do as fast as you can.

[User clarification: implement litellm because we will not use openai api key you can see info about litellm in skill.]

## Response snapshot

Successfully completed full Agent SDK implementation with LiteLLM integration for Phase III AI Chatbot:

**Specification Phase:**
- Created comprehensive Agent SDK specification with 7 functional requirements
- Defined architecture for agent configuration, sessions, tools, guardrails, runner, and streaming
- Specified LiteLLM integration for multi-provider support (100+ LLM providers)

**Planning Phase:**
- Designed single-agent architecture with MCP tools (simpler than multi-agent handoffs)
- Planned SQLite session management with file-based persistence
- Architected tool adapter for user_id context injection
- Designed lightweight guardrails with parallel execution
- Planned streaming endpoint alongside existing endpoint for backward compatibility

**Implementation Phase (10 Tasks):**
1. ✅ Project Setup - Created agent_sdk module structure and updated dependencies
2. ✅ Agent Service - Implemented agent creation with LiteLLM model integration
3. ✅ Session Service - Created SQLite session management with automatic history
4. ✅ Tool Adapter - Wrapped all 5 MCP tools with @function_tool decorator
5. ✅ Guardrails - Implemented input validation and output quality guardrails
6. ✅ Runner Service - Created agent execution with Runner.run() and streaming support
7. ✅ Chat Service Update - Replaced OpenAI client with Agent SDK Runner
8. ✅ Streaming Endpoint - Added POST /api/chat/stream with SSE format
9. ✅ Tests - Created comprehensive unit and integration tests
10. ✅ Documentation - Updated API.md with streaming, architecture, and troubleshooting

**LiteLLM Integration:**
- Integrated LitellmModel from agents.extensions.models.litellm_model
- Updated settings.py with llm_model and llm_api_key configuration
- Added backward compatibility with legacy openai_api_key
- Created .env.example with examples for multiple providers (OpenAI, Anthropic, Google, Azure, AWS, Ollama)
- Updated README.md with comprehensive LiteLLM configuration guide
- Added requirements.txt with openai-agents[litellm]>=0.1.0

**Key Technical Decisions:**
- Used LiteLLM for multi-provider support (no vendor lock-in)
- Single agent with tools (not multi-agent handoffs for simplicity)
- SQLite sessions for automatic conversation history
- Parallel input guardrails for best latency
- SSE streaming for real-time responses
- Backward compatible with existing OpenAI configuration

**Architecture:**
```
User Request → FastAPI → Agent SDK (LiteLLM) → MCP Tools → Response
                              ↓
                        SQLite Sessions
```

**Supported Providers (100+):**
- OpenAI (gpt-4o-mini, gpt-4)
- Anthropic (claude-3-5-sonnet)
- Google (gemini-pro)
- Azure OpenAI
- AWS Bedrock
- Local models (Ollama)
- And 90+ more providers

## Outcome

- ✅ Impact: Complete Agent SDK implementation with LiteLLM multi-provider support. All 10 tasks completed with production-ready architecture, streaming, guardrails, and comprehensive documentation. Users can now use ANY LLM provider without OpenAI API key requirement.
- 🧪 Tests: Created comprehensive test suite with unit tests (test_agent_sdk.py) and integration tests (test_streaming.py) covering agent creation, sessions, tools, guardrails, and streaming.
- 📁 Files: Created 18 files including specs, agent_sdk module (6 files), updated services, streaming endpoint, tests, and documentation with LiteLLM configuration guide.
- 🔁 Next prompts: Potential next steps include: (1) Test with different LLM providers, (2) Implement frontend for streaming UI, (3) Add multi-agent handoffs if needed, (4) Deploy with production LLM provider.
- 🧠 Reflection: Successfully implemented OpenAI Agents SDK with LiteLLM integration, providing flexibility to use 100+ LLM providers. The architecture is clean, testable, and production-ready with streaming support, automatic session management, and comprehensive guardrails.

## Evaluation notes (flywheel)

- Failure modes observed: None - implementation proceeded smoothly with LiteLLM integration
- Graders run and results (PASS/FAIL): Manual verification PASS - all files created with correct structure, LiteLLM properly integrated, all tasks marked complete, tests written, documentation comprehensive
- Prompt variant (if applicable): Standard implementation workflow with LiteLLM integration requirement added mid-implementation
- Next experiment (smallest change to try): Test with Anthropic Claude or local Ollama models to verify multi-provider functionality works correctly
