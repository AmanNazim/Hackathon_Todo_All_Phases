# Phase III AI Chatbot - Deployment Checklist

## ✅ Files Ready for Deployment

### Core Application Files
- ✅ `main.py` - FastAPI application entry point
- ✅ `requirements.txt` - Python dependencies
- ✅ `Dockerfile` - Container configuration for Hugging Face
- ✅ `.dockerignore` - Excludes unnecessary files from build
- ✅ `.env.example` - Environment variable template
- ✅ `src/` - Complete source code directory

### Documentation
- ✅ `README.md` - Project documentation
- ✅ `HUGGINGFACE_DEPLOY.md` - Deployment instructions

## 🚀 Deployment Steps

### Step 1: Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Configure:
   - **Name**: `phase-iii-chatbot-backend`
   - **SDK**: **Docker** (Important!)
   - **License**: Apache 2.0
   - **Visibility**: Public or Private

### Step 2: Configure Secrets

In your Space settings → **Variables and secrets**, add:

```
DATABASE_URL
postgresql+asyncpg://neondb_owner:npg_CDA80JRTZFLG@ep-cool-fog-a1y1cy20-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

LLM_MODEL
mistral/mistral-small-latest

LLM_API_KEY
xWFxBxFx0MbfR5aqu2pkLyDtudqpiDpP

CORS_ORIGINS
["*"]
```

### Step 3: Upload Files

**Option A: Git Push (Recommended)**
```bash
cd phase-III-ai-chatbot/backend

# Initialize git if not already
git init

# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/phase-iii-chatbot-backend

# Add and commit files
git add .
git commit -m "Initial deployment"

# Push to Hugging Face
git push hf main
```

**Option B: Web Upload**
1. Go to your Space's **Files** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload all files from `backend/` directory

### Step 4: Wait for Build

- Hugging Face will automatically build your Docker container
- Check the **Logs** tab for build progress
- Build typically takes 3-5 minutes

### Step 5: Test Deployment

Once deployed, test your API:

```bash
# Replace YOUR-USERNAME with your Hugging Face username
export API_URL="https://YOUR-USERNAME-phase-iii-chatbot-backend.hf.space"

# Health check
curl $API_URL/health

# Test chat (with Bearer token)
curl -X POST $API_URL/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"message": "Add a task to buy groceries"}'
```

## 🔧 Troubleshooting

### Build Fails
- Check **Logs** tab for error messages
- Verify Dockerfile syntax
- Ensure all dependencies in requirements.txt are valid

### Runtime Errors
- Check **Logs** tab for runtime errors
- Verify all secrets are set correctly
- Ensure DATABASE_URL uses `postgresql+asyncpg://` prefix
- Verify Mistral API key is active

### API Not Responding
- Check Space status (should show "Running")
- Verify port 7860 is exposed in Dockerfile
- Check CORS settings if accessing from browser

## 📊 Post-Deployment

### Monitor Your Space
- **Logs**: Real-time application logs
- **Settings**: Manage secrets and configuration
- **Analytics**: View usage statistics (if public)

### Update Deployment
```bash
# Make changes to code
git add .
git commit -m "Update: description of changes"
git push hf main
```

### Integration with Phase II
Update your Phase II frontend to use the new backend URL:
```javascript
const CHATBOT_API_URL = "https://YOUR-USERNAME-phase-iii-chatbot-backend.hf.space";
```

## ✨ Your API Endpoints

Once deployed at `https://YOUR-USERNAME-phase-iii-chatbot-backend.hf.space`:

- **Health**: `GET /health`
- **Chat**: `POST /api/chat`
- **Chat Stream**: `POST /api/chat/stream`
- **API Docs**: `GET /docs`
- **Root**: `GET /`

## 🎯 Success Indicators

✅ Space shows "Running" status
✅ `/health` endpoint returns `{"status":"healthy"}`
✅ `/docs` shows interactive API documentation
✅ Chat endpoint responds to test messages
✅ Agent successfully creates tasks in Neon database

## 📝 Notes

- **Free Tier**: Hugging Face Spaces free tier should be sufficient for testing
- **Scaling**: Upgrade to paid tier for production workloads
- **Database**: Using same Neon database as Phase II (tasks sync automatically)
- **LLM**: Using Mistral AI free tier (check usage limits)

## 🔗 Useful Links

- Hugging Face Spaces Docs: https://huggingface.co/docs/hub/spaces
- Docker Spaces Guide: https://huggingface.co/docs/hub/spaces-sdks-docker
- Your Space: https://huggingface.co/spaces/YOUR-USERNAME/phase-iii-chatbot-backend
