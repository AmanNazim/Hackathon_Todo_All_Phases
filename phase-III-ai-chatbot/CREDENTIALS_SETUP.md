# Credentials Setup Checklist

## Quick Reference - What You Need

### 1. Database Credentials ✓

**Option A: SQLite (Easiest - for development)**
```bash
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db
```
✅ No setup needed - file created automatically

**Option B: PostgreSQL (Recommended - for production)**
```bash
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/chatbot_db
```
📝 You need:
- PostgreSQL installed
- Database created: `createdb chatbot_db`
- Username and password

---

### 2. LLM API Key (Required) ⚠️

**Choose ONE provider:**

#### OpenAI (Recommended)
```bash
LLM_MODEL=openai/gpt-4o-mini
LLM_API_KEY=sk-proj-xxxxxxxxxxxxx
```
🔗 Get key: https://platform.openai.com/api-keys
💰 Cost: ~$0.15 per 1M tokens (gpt-4o-mini)

#### Anthropic Claude
```bash
LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
LLM_API_KEY=sk-ant-xxxxxxxxxxxxx
```
🔗 Get key: https://console.anthropic.com/
💰 Cost: ~$3 per 1M tokens

#### Google Gemini
```bash
LLM_MODEL=gemini/gemini-pro
LLM_API_KEY=xxxxxxxxxxxxx
```
🔗 Get key: https://makersuite.google.com/app/apikey
💰 Cost: Free tier available

#### Ollama (Local - No API Key)
```bash
LLM_MODEL=ollama/llama2
LLM_API_KEY=not-needed
```
🔗 Install: https://ollama.ai/
💰 Cost: Free (runs locally)
📝 Setup: `ollama pull llama2`

---

### 3. Frontend Configuration (Optional)

```bash
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```
✅ Default works for most cases

---

## Step-by-Step Setup

### Step 1: Copy Environment File
```bash
cd phase-III-ai-chatbot/backend
cp .env.example .env
```

### Step 2: Edit .env File
```bash
nano .env  # or use your preferred editor
```

### Step 3: Add Your Credentials

**Minimum required changes:**
1. ✅ Keep `DATABASE_URL=sqlite+aiosqlite:///./chatbot.db` (easiest)
2. ⚠️ Change `LLM_MODEL` to your chosen provider
3. ⚠️ Change `LLM_API_KEY` to your actual API key

**Example .env file (OpenAI):**
```bash
# App Configuration
APP_NAME=Phase III AI Chatbot
ENVIRONMENT=development
DEBUG=true

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db

# LLM Configuration
LLM_MODEL=openai/gpt-4o-mini
LLM_API_KEY=sk-proj-abc123xyz789...  # ← YOUR KEY HERE

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Step 4: Verify Setup
```bash
# Run quick start script
./quick-start.sh

# Or manually start server
uvicorn main:app --reload
```

### Step 5: Test
```bash
# Check health
curl http://localhost:8000/health

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to test the system", "user_id": "test"}'
```

---

## Common Issues

### ❌ "API key invalid"
- Check API key is correct in .env
- Verify key is active on provider website
- Check for extra spaces or quotes

### ❌ "Database connection failed"
- For SQLite: Check file permissions
- For PostgreSQL: Verify database exists and credentials are correct

### ❌ "Module not found"
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### ❌ "CORS error"
- Add your frontend URL to CORS_ORIGINS in .env
- Restart backend server

---

## Security Notes

⚠️ **NEVER commit .env file to git**
✅ .env is in .gitignore by default

⚠️ **Use different API keys for dev/prod**
✅ Create separate keys for each environment

⚠️ **Rotate API keys regularly**
✅ Update keys every 90 days

---

## Cost Estimates (Monthly)

### Development (Low Usage)
- OpenAI gpt-4o-mini: ~$1-5/month
- Anthropic Claude: ~$5-10/month
- Google Gemini: Free tier sufficient
- Ollama: $0 (local)

### Production (Medium Usage)
- OpenAI gpt-4o-mini: ~$20-50/month
- Anthropic Claude: ~$50-100/month
- Google Gemini: ~$10-30/month
- Ollama: $0 (local)

---

## Quick Start Command

```bash
# One-line setup (after adding credentials to .env)
cd phase-III-ai-chatbot/backend && ./quick-start.sh
```

---

## Need Help?

1. Check INTEGRATION_GUIDE.md for detailed instructions
2. Check backend logs for error messages
3. Verify all credentials are correct
4. Try with SQLite + Ollama (no credentials needed)

---

## Minimal Setup (No Credentials)

Want to test without any API keys?

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama2

# Update .env
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db
LLM_MODEL=ollama/llama2
LLM_API_KEY=not-needed

# Start server
uvicorn main:app --reload
```

✅ Works completely offline!
