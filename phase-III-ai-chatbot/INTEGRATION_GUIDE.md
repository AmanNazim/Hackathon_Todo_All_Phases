# Phase III AI Chatbot - Complete Integration Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (React Frontend / Claude Desktop)             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Chat API     │  │ ChatKit API  │  │ Health Check │         │
│  │ /api/chat    │  │ /api/chatkit │  │ /health      │         │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘         │
│         │                  │                                     │
│         └──────────┬───────┘                                     │
│                    ▼                                             │
│         ┌─────────────────────┐                                 │
│         │  Agent SDK Service  │                                 │
│         │  (OpenAI Agents)    │                                 │
│         └──────────┬──────────┘                                 │
│                    │                                             │
│         ┌──────────┴──────────┐                                 │
│         │                     │                                 │
│         ▼                     ▼                                 │
│  ┌─────────────┐      ┌─────────────┐                         │
│  │  LiteLLM    │      │ Agent Tools │                         │
│  │  (100+ LLMs)│      │ (MCP Tools) │                         │
│  └─────────────┘      └──────┬──────┘                         │
│                               │                                 │
│                               ▼                                 │
│                      ┌─────────────────┐                       │
│                      │  Task Service   │                       │
│                      └────────┬────────┘                       │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   PostgreSQL/SQLite   │
                    │   (Task Database)     │
                    └───────────────────────┘
```

## Component Connections

### 1. Frontend → Backend
- **Connection**: HTTP REST API
- **Endpoints**: `/api/chat`, `/api/chatkit`
- **Authentication**: Bearer token (optional)
- **CORS**: Configured in backend

### 2. Backend → Agent SDK
- **Connection**: Direct Python imports
- **Flow**: API routes → Agent Service → Runner Service
- **Tools**: Agent SDK function tools with user_id injection

### 3. Agent SDK → LiteLLM
- **Connection**: LiteLLM model integration
- **Configuration**: Model name + API key
- **Supports**: OpenAI, Anthropic, Google, Azure, AWS, Ollama, 100+ providers

### 4. Agent SDK → MCP Tools
- **Connection**: Tool adapter wraps TaskService
- **Tools**: add_task, list_tasks, complete_task, delete_task, update_task
- **Context**: user_id injected automatically

### 5. MCP Tools → Task Service
- **Connection**: Direct Python imports
- **Operations**: CRUD operations on tasks
- **Validation**: User isolation, error handling

### 6. Task Service → Database
- **Connection**: SQLAlchemy async
- **Database**: PostgreSQL (production) or SQLite (development)
- **Models**: Task, User, Session

## Required Credentials

### 1. Environment Variables (.env file)

Create `.env` file in `backend/` directory:

```bash
# App Configuration
APP_NAME=Phase III AI Chatbot
ENVIRONMENT=development
DEBUG=true

# Database Configuration
# Option 1: PostgreSQL (Production)
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/chatbot_db

# Option 2: SQLite (Development)
# DATABASE_URL=sqlite+aiosqlite:///./chatbot.db

# LLM Configuration (Choose one provider)
# The model format is: "provider/model-name"

# Option 1: OpenAI (Recommended)
LLM_MODEL=openai/gpt-4o-mini
LLM_API_KEY=sk-your-openai-api-key-here

# Option 2: Anthropic Claude
# LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
# LLM_API_KEY=sk-ant-your-anthropic-api-key-here

# Option 3: Google Gemini
# LLM_MODEL=gemini/gemini-pro
# LLM_API_KEY=your-google-api-key-here

# Option 4: Azure OpenAI
# LLM_MODEL=azure/gpt-4
# LLM_API_KEY=your-azure-api-key-here
# AZURE_API_BASE=https://your-resource.openai.azure.com
# AZURE_API_VERSION=2024-02-15-preview

# Option 5: Ollama (Local, no API key needed)
# LLM_MODEL=ollama/llama2
# LLM_API_KEY=not-needed

# CORS Configuration (Frontend URLs)
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:5173"]

# Session Configuration (Optional)
SESSION_DB_PATH=./data/sessions.db
```

### 2. Database Credentials

#### PostgreSQL (Production)
```bash
# Install PostgreSQL
# Ubuntu/Debian: sudo apt install postgresql
# macOS: brew install postgresql

# Create database
createdb chatbot_db

# Create user (optional)
psql -c "CREATE USER chatbot_user WITH PASSWORD 'your_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;"

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://chatbot_user:your_password@localhost:5432/chatbot_db
```

#### SQLite (Development)
```bash
# No setup needed - file will be created automatically
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db
```

### 3. LLM Provider API Keys

#### OpenAI (Recommended)
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy key to `.env`:
   ```bash
   LLM_MODEL=openai/gpt-4o-mini
   LLM_API_KEY=sk-proj-...your-key...
   ```

#### Anthropic Claude
1. Go to https://console.anthropic.com/
2. Create API key
3. Copy key to `.env`:
   ```bash
   LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
   LLM_API_KEY=sk-ant-...your-key...
   ```

#### Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Create API key
3. Copy key to `.env`:
   ```bash
   LLM_MODEL=gemini/gemini-pro
   LLM_API_KEY=...your-key...
   ```

#### Ollama (Local - No API Key)
1. Install Ollama: https://ollama.ai/
2. Pull model: `ollama pull llama2`
3. Update `.env`:
   ```bash
   LLM_MODEL=ollama/llama2
   LLM_API_KEY=not-needed
   ```

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd phase-III-ai-chatbot/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

**Required changes in .env:**
1. Set `DATABASE_URL` (PostgreSQL or SQLite)
2. Set `LLM_MODEL` (choose provider)
3. Set `LLM_API_KEY` (your API key)
4. Update `CORS_ORIGINS` if needed

### Step 3: Initialize Database

```bash
# Run database migrations (if using Alembic)
alembic upgrade head

# Or initialize database directly
python -c "from src.database.initialize import init_db; import asyncio; asyncio.run(init_db())"
```

### Step 4: Start Backend Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Backend will be available at: http://localhost:8000

### Step 5: Verify Backend

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"phase-iii-chatbot"}

# Check API docs
# Open browser: http://localhost:8000/docs
```

### Step 6: Start Frontend (Optional)

```bash
cd phase-III-ai-chatbot/frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000/api" > .env

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### Step 7: Test Integration

#### Test Chat API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "user_id": "test_user"
  }'
```

Expected response:
```json
{
  "response": "I've added 'Buy groceries' to your tasks",
  "conversation_id": "...",
  "usage": {...}
}
```

#### Test Task Creation

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all my tasks",
    "user_id": "test_user"
  }'
```

## MCP Server Integration (Optional)

### For Claude Desktop

1. **Create MCP Server Config**:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "task-management": {
      "command": "python",
      "args": ["/absolute/path/to/phase-III-ai-chatbot/backend/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/phase-III-ai-chatbot/backend"
      }
    }
  }
}
```

2. **Restart Claude Desktop**

3. **Test MCP Tools**:
   - "Add a task to buy milk"
   - "Show my tasks"
   - "Mark task 1 as complete"

## Troubleshooting

### Backend Won't Start

**Issue**: Import errors or module not found

**Solution**:
```bash
# Ensure you're in the backend directory
cd phase-III-ai-chatbot/backend

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Connection Errors

**Issue**: Can't connect to database

**Solution**:
```bash
# For PostgreSQL - check if running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# For SQLite - check file permissions
ls -la chatbot.db

# Test connection
python -c "from src.database import engine; print('Connected!')"
```

### LLM API Errors

**Issue**: API key invalid or quota exceeded

**Solution**:
1. Verify API key in `.env` file
2. Check API key validity on provider website
3. Check usage limits/quotas
4. Try different model:
   ```bash
   # Switch to cheaper model
   LLM_MODEL=openai/gpt-3.5-turbo
   ```

### CORS Errors

**Issue**: Frontend can't connect to backend

**Solution**:
```bash
# Update CORS_ORIGINS in .env
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Restart backend
```

### MCP Tools Not Working

**Issue**: Tools not appearing in Claude Desktop

**Solution**:
1. Check config file syntax (valid JSON)
2. Use absolute paths
3. Restart Claude Desktop completely
4. Check server logs:
   ```bash
   python mcp_server.py 2> mcp_errors.log
   ```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Database connection works
- [ ] LLM API key valid
- [ ] Chat endpoint responds to messages
- [ ] Tasks can be created via chat
- [ ] Tasks can be listed via chat
- [ ] Tasks can be completed via chat
- [ ] Tasks can be deleted via chat
- [ ] Frontend connects to backend (if using)
- [ ] MCP server works with Claude Desktop (if using)

## Production Deployment

### Environment Variables for Production

```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/chatbot_db
LLM_MODEL=openai/gpt-4o-mini
LLM_API_KEY=sk-prod-key-here
CORS_ORIGINS=["https://yourdomain.com"]
```

### Security Checklist

- [ ] Use PostgreSQL (not SQLite)
- [ ] Use strong database passwords
- [ ] Enable HTTPS
- [ ] Restrict CORS origins
- [ ] Use environment variables (never commit .env)
- [ ] Enable rate limiting
- [ ] Add authentication/authorization
- [ ] Monitor API usage
- [ ] Set up logging
- [ ] Configure backups

## Summary

Your Phase III AI Chatbot is now fully integrated with:

✅ **Backend**: FastAPI with Agent SDK and LiteLLM
✅ **Agent**: OpenAI Agents SDK with guardrails
✅ **LLM**: LiteLLM supporting 100+ providers
✅ **Tools**: MCP tools for task management
✅ **Database**: PostgreSQL or SQLite
✅ **Frontend**: React (optional)
✅ **MCP Server**: Claude Desktop integration (optional)

All components are connected and ready to use!
