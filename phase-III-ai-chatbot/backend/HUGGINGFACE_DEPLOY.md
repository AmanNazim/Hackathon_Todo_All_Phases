# Phase III AI Chatbot Backend - Hugging Face Deployment

## Quick Deploy to Hugging Face Spaces

### 1. Create New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose:
   - **Space name**: `phase-iii-chatbot-backend`
   - **License**: Apache 2.0
   - **Space SDK**: Docker
   - **Visibility**: Public or Private

### 2. Set Environment Variables (Secrets)

In your Space settings, add these secrets:

```bash
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_CDA80JRTZFLG@ep-cool-fog-a1y1cy20-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

LLM_MODEL=mistral/mistral-small-latest

LLM_API_KEY=xWFxBxFx0MbfR5aqu2pkLyDtudqpiDpP

CORS_ORIGINS=["*"]
```

### 3. Upload Files

Upload the entire `backend/` directory to your Space:
- `main.py`
- `requirements.txt`
- `Dockerfile` (created below)
- `src/` directory (all files)

### 4. Access Your API

Once deployed, your API will be available at:
```
https://YOUR-USERNAME-phase-iii-chatbot-backend.hf.space
```

**Endpoints:**
- Health: `GET /health`
- Chat: `POST /api/chat` (requires Bearer token)
- API Docs: `GET /docs`

### 5. Test Deployment

```bash
# Health check
curl https://YOUR-USERNAME-phase-iii-chatbot-backend.hf.space/health

# Chat test (with auth token)
curl -X POST https://YOUR-USERNAME-phase-iii-chatbot-backend.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"message": "Add a task to buy groceries"}'
```

## Troubleshooting

**If deployment fails:**
1. Check Space logs for errors
2. Verify all secrets are set correctly
3. Ensure DATABASE_URL uses `postgresql+asyncpg://` prefix
4. Check that LLM_API_KEY is valid

**If API returns errors:**
1. Check that Mistral API key is active
2. Verify Neon database is accessible
3. Review Space logs for detailed error messages

## Integration with Phase II

Once deployed, update your Phase II frontend to use this backend URL for AI chat features while keeping the existing Phase II backend for regular todo operations.
