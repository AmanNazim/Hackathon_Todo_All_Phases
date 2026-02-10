---
title: Todo Chatbot Backend
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

# Phase III AI Chatbot Backend - Agent SDK with LiteLLM

## Overview

This backend uses OpenAI Agents SDK with LiteLLM integration, allowing you to use **100+ different LLM providers** without being locked into OpenAI.

## Features

- **Multi-Provider Support**: Use OpenAI, Anthropic, Google, Azure, AWS, and 100+ other providers
- **Agent SDK**: Production-ready agent framework with sessions, guardrails, and streaming
- **MCP Tools**: Natural language task management with 5 MCP tools
- **Streaming Responses**: Real-time SSE streaming for better UX
- **Session Management**: Automatic conversation history with SQLite

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create data directory for sessions
mkdir -p data

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

## LiteLLM Configuration

### Supported Providers

LiteLLM supports 100+ providers. Here are some popular ones:

**OpenAI**:
```env
LLM_MODEL=openai/gpt-4o-mini
LLM_API_KEY=sk-...
```

**Anthropic (Claude)**:
```env
LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
LLM_API_KEY=sk-ant-...
```

**Google (Gemini)**:
```env
LLM_MODEL=gemini/gemini-pro
LLM_API_KEY=...
```

**Azure OpenAI**:
```env
LLM_MODEL=azure/gpt-4
LLM_API_KEY=...
AZURE_API_BASE=https://your-resource.openai.azure.com
AZURE_API_VERSION=2023-05-15
```

**AWS Bedrock**:
```env
LLM_MODEL=bedrock/anthropic.claude-v2
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=us-east-1
```

**Local Models (Ollama)**:
```env
LLM_MODEL=ollama/llama2
LLM_API_KEY=dummy  # Not used for local models
```

For complete list, see: https://docs.litellm.ai/docs/providers

## Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Chat (Standard)
```bash
POST /api/chat
```

### Chat (Streaming)
```bash
POST /api/chat/stream
```

See `API.md` for complete documentation.

## Architecture

```
User Request → FastAPI → Agent SDK (LiteLLM) → MCP Tools → Response
                              ↓
                        SQLite Sessions
```

### Components

- **Agent Service**: Creates agents with LiteLLM models
- **Session Service**: Manages conversation history
- **Tool Adapter**: Converts MCP tools to SDK function tools
- **Guardrails**: Input/output validation
- **Runner Service**: Executes agents with streaming support

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agent_sdk.py
```

## Environment Variables

Required:
- `DATABASE_URL`: PostgreSQL connection string
- `LLM_MODEL`: LiteLLM model identifier (e.g., "openai/gpt-4o-mini")
- `LLM_API_KEY`: API key for your LLM provider

Optional:
- `APP_NAME`: Application name (default: "Phase III AI Chatbot")
- `ENVIRONMENT`: Environment (default: "development")
- `DEBUG`: Debug mode (default: true)
- `CORS_ORIGINS`: Allowed CORS origins (default: ["http://localhost:3000"])

## Troubleshooting

### "No LLM API key configured"
- Ensure `LLM_API_KEY` is set in `.env`
- Or set `OPENAI_API_KEY` for backward compatibility

### "Failed to create/retrieve session"
- Ensure `data/` directory exists: `mkdir -p data`
- Check write permissions: `chmod 755 data`

### "Maximum turns exceeded"
- Request is too complex, break into smaller parts
- Agent has `max_iterations=10` to prevent infinite loops

### Model not working
- Check model name format: `provider/model-name`
- Verify API key is correct for the provider
- Check provider-specific environment variables (Azure, AWS, etc.)

## Development

### Adding New Tools

1. Create tool function in `src/mcp/tools/`
2. Add to tool adapter in `src/agent_sdk/tool_adapter.py`
3. Update agent instructions if needed

### Changing LLM Provider

Simply update `.env`:
```env
# Switch from OpenAI to Anthropic
LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
LLM_API_KEY=sk-ant-your-key
```

No code changes required!

## Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Set `DEBUG=false`
3. Use production database URL
4. Configure proper CORS origins
5. Use process manager (systemd, supervisor, or Docker)
6. Set up reverse proxy (nginx, caddy)
7. Enable HTTPS

## License

MIT

## Support

For issues or questions:
- Check API documentation: `/docs`
- Review Agent SDK docs: https://openai.github.io/openai-agents-python/
- Review LiteLLM docs: https://docs.litellm.ai/
