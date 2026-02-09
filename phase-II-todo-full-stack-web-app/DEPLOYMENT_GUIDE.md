# Deployment Guide: Todo Full-Stack Application

Complete step-by-step guide to deploy the Todo application to production.

---

## Deployment Architecture

```
Vercel (Frontend)
    ↓
Hugging Face Spaces (Backend API)
    ↓
Neon (PostgreSQL Database)
```

---

## Prerequisites

Before starting, create accounts on:
1. **Neon** - https://neon.tech (Database)
2. **Hugging Face** - https://huggingface.co (Backend)
3. **Vercel** - https://vercel.com (Frontend)
4. **GitHub** - https://github.com (Code repository)

---

## Part 1: Database Setup (Neon PostgreSQL)

### Step 1: Create Neon Account

1. Go to https://neon.tech
2. Click "Sign Up" (use GitHub for easy integration)
3. Verify your email

### Step 2: Create Database Project

1. Click "Create Project"
2. **Project Name**: `todo-app-db`
3. **Region**: Choose closest to your users (e.g., US East, EU West)
4. **PostgreSQL Version**: 15 (default)
5. Click "Create Project"

### Step 3: Get Connection String

1. After project creation, you'll see the dashboard
2. Click "Connection Details"
3. **Copy the connection string** - it looks like:
   ```
   postgresql://username:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
4. **Save this** - you'll need it for backend deployment

### Step 4: Initialize Database (Optional)

You can initialize the database later from Railway, or use Neon's SQL Editor:

1. Click "SQL Editor" in Neon dashboard
2. Run this SQL to create tables:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(50) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'todo',
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

---

## Part 2: Backend Deployment (Hugging Face Spaces)

### Step 1: Prepare Backend for Deployment

1. Ensure `backend/requirements.txt` has all dependencies
2. Verify `backend/Dockerfile` exists and uses port 7860
3. Create `backend/README.md` for Hugging Face Space:

```markdown
---
title: Todo App Backend
emoji: 📝
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Todo App Backend API

FastAPI backend for Todo application with PostgreSQL database.
```

### Step 2: Push Code to GitHub

```bash
# Navigate to project root
cd phase-II-todo-full-stack-web-app

# Add all files
git add .

# Commit
git commit -m "Prepare backend for Hugging Face deployment"

# Push to GitHub
git push origin main
```

### Step 3: Create Hugging Face Space

1. Go to https://huggingface.co
2. Click your profile → "New Space"
3. Configure:
   - **Space name**: `todo-app-backend`
   - **License**: Apache 2.0
   - **Select SDK**: Docker
   - **Space hardware**: CPU basic (free)
   - **Visibility**: Public or Private
4. Click "Create Space"

### Step 4: Connect GitHub Repository

**Option A: Direct Git Push (Recommended)**

1. In your Space, click "Files" → "Add file" → "Create a new file"
2. Or use git to push directly:

```bash
# Navigate to backend directory
cd backend

# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/todo-app-backend

# Push to Hugging Face
git push hf main
```

**Option B: Upload Files via Web Interface**

1. Click "Files" tab in your Space
2. Upload these files from `backend/` directory:
   - `Dockerfile`
   - `main.py`
   - `models.py`
   - `database.py`
   - `auth.py`
   - `requirements.txt`
   - `README.md`
   - All files in `routes/` folder

### Step 5: Configure Environment Variables

1. In your Space, click "Settings"
2. Scroll to "Repository secrets"
3. Add these secrets (click "New secret" for each):

```env
DATABASE_URL=<YOUR_NEON_CONNECTION_STRING>
JWT_SECRET=<GENERATE_RANDOM_32_CHAR_STRING>
BETTER_AUTH_SECRET=<GENERATE_RANDOM_32_CHAR_STRING>
ALLOWED_ORIGINS=https://your-app.vercel.app
APP_ENV=production
DEBUG=false
```

**To generate secrets:**
```bash
# Run in terminal
openssl rand -base64 32
```

Or use the deploy-helper.sh script:
```bash
cd phase-II-todo-full-stack-web-app
./deploy-helper.sh
```

### Step 6: Deploy and Wait

1. After adding secrets, Hugging Face will automatically build and deploy
2. Build takes 3-5 minutes
3. Watch the "Logs" tab for build progress
4. Once complete, you'll see "Running" status
5. Your API URL will be: `https://YOUR_USERNAME-todo-app-backend.hf.space`

### Step 7: Initialize Database

```bash
# Test health endpoint first
curl https://YOUR_USERNAME-todo-app-backend.hf.space/health

# Initialize database (if you have init endpoint)
curl -X POST https://YOUR_USERNAME-todo-app-backend.hf.space/api/init-db
```

### Step 8: Test Backend

```bash
# Test health endpoint
curl https://YOUR_USERNAME-todo-app-backend.hf.space/health

# View API documentation
open https://YOUR_USERNAME-todo-app-backend.hf.space/docs
```

---

## Part 3: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

1. Update `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-todo-app-backend.hf.space
NEXT_PUBLIC_APP_NAME=Todo App
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

2. Ensure `frontend/package.json` has build script:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

### Step 2: Deploy to Vercel

**Option A: Vercel CLI (Recommended)**

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

**Option B: Vercel Dashboard**

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Step 3: Configure Environment Variables in Vercel

1. In Vercel project settings
2. Go to "Settings" → "Environment Variables"
3. Add these variables:

```env
NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-todo-app-backend.hf.space
NEXT_PUBLIC_APP_NAME=Todo App
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

4. Click "Save"
5. Redeploy: "Deployments" → "..." → "Redeploy"

### Step 4: Update Backend CORS

1. Go back to Hugging Face Space
2. Click "Settings" → "Repository secrets"
3. Update `ALLOWED_ORIGINS` secret:
   ```
   https://your-app.vercel.app,https://your-app-git-main.vercel.app
   ```
4. Space will auto-redeploy (takes 3-5 minutes)

---

## Part 4: Final Configuration

### Update Frontend URL in Backend

If your Vercel URL is different from expected:

1. Hugging Face Space → Settings → Repository secrets
2. Update `ALLOWED_ORIGINS` with actual Vercel URL
3. Save (auto-redeploys in 3-5 minutes)

### Update Backend URL in Frontend

If your Hugging Face Space URL changed:

1. Vercel → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL`
3. Redeploy

---

## Part 5: Testing Deployment

### Test Backend

```bash
# Health check
curl https://YOUR_USERNAME-todo-app-backend.hf.space/health

# API docs
open https://YOUR_USERNAME-todo-app-backend.hf.space/docs
```

### Test Frontend

1. Open `https://your-app.vercel.app`
2. Should see landing page
3. Try to register a new account
4. Try to login
5. Create a task
6. Test all features

### Test Integration

1. Open browser DevTools (F12)
2. Go to Network tab
3. Perform actions (login, create task)
4. Verify API calls to Hugging Face backend succeed
5. Check for CORS errors (should be none)

---

## Part 6: Troubleshooting

### Backend Issues

**Problem**: 500 Internal Server Error
```
Solution:
1. Check Hugging Face Space logs: Space → Logs tab
2. Look for database connection errors
3. Verify DATABASE_URL is correct in secrets
4. Check all environment variables are set
5. Restart Space: Settings → Factory reboot
```

**Problem**: CORS errors
```
Solution:
1. Verify ALLOWED_ORIGINS includes your Vercel URL
2. Include both main URL and preview URLs
3. Format: https://app.vercel.app,https://app-git-main.vercel.app
4. Update in Space Settings → Repository secrets
5. Wait 3-5 minutes for rebuild
```

**Problem**: Database connection failed
```
Solution:
1. Verify Neon database is active
2. Check connection string format
3. Ensure ?sslmode=require is in connection string
4. Test connection from local machine first
```

**Problem**: Space not building
```
Solution:
1. Check Dockerfile syntax
2. Verify all files are uploaded
3. Check build logs for errors
4. Ensure requirements.txt has all dependencies
5. Try Factory reboot in Settings
```

### Frontend Issues

**Problem**: Cannot connect to backend
```
Solution:
1. Verify NEXT_PUBLIC_API_URL is correct
2. Check Railway backend is running
3. Test backend directly: curl https://backend-url/health
4. Check browser console for errors
```

**Problem**: Build fails
```
Solution:
1. Check Vercel build logs
2. Verify all dependencies in package.json
3. Ensure TypeScript has no errors
4. Try building locally: npm run build
```

**Problem**: Environment variables not working
```
Solution:
1. Ensure variables start with NEXT_PUBLIC_
2. Redeploy after adding variables
3. Clear Vercel cache: Settings → Clear Cache
```

---

## Part 7: Post-Deployment

### Monitor Application

**Hugging Face Spaces (Backend)**:
- Space Dashboard → Logs tab
- Monitor build and runtime logs
- Check for errors and warnings
- View resource usage

**Vercel (Frontend)**:
- Analytics → Overview
- Monitor page views, performance
- Check deployment logs
- View function execution logs

**Neon (Database)**:
- Dashboard → Monitoring
- Check connection count
- Monitor query performance
- View storage usage

### Set Up Custom Domain (Optional)

**Vercel**:
1. Settings → Domains
2. Add your domain
3. Configure DNS records
4. Update ALLOWED_ORIGINS in Hugging Face Space

**Hugging Face Spaces**:
- Custom domains not supported on free tier
- Use provided .hf.space URL
- Or upgrade to Enterprise for custom domains

---

## Part 8: Security Checklist

- [ ] Changed all default secrets
- [ ] JWT_SECRET is strong (32+ characters)
- [ ] BETTER_AUTH_SECRET is strong (32+ characters)
- [ ] CORS is restricted to your domain only
- [ ] Database has strong password
- [ ] SSL/HTTPS enabled (automatic on Vercel/Railway)
- [ ] Environment variables not committed to git
- [ ] Debug mode disabled in production

---

## Part 9: Scaling Considerations

### If You Get More Users

**Database (Neon)**:
- Free tier: 0.5 GB storage, 100 hours compute
- Upgrade to Pro: $19/month for more resources
- Scale: 10 GB storage, unlimited compute hours

**Backend (Hugging Face Spaces)**:
- Free tier: CPU basic (2 vCPU, 16 GB RAM)
- Upgrade options:
  - CPU upgrade: $0.60/hour for better performance
  - GPU: Starting at $0.60/hour (if needed for ML features)
  - Persistent storage: Available on paid tiers
- Note: Free tier may have cold starts after inactivity

**Frontend (Vercel)**:
- Free tier: 100 GB bandwidth
- Upgrade to Pro: $20/month for more bandwidth
- Scale: 1 TB bandwidth, advanced analytics

---

## Quick Reference

### URLs After Deployment

- **Frontend**: https://your-app.vercel.app
- **Backend**: https://YOUR_USERNAME-todo-app-backend.hf.space
- **API Docs**: https://YOUR_USERNAME-todo-app-backend.hf.space/docs
- **Database**: Neon dashboard

### Important Commands

```bash
# Generate secrets
./deploy-helper.sh

# Redeploy backend (push to Hugging Face)
cd backend
git push hf main

# Redeploy frontend
cd frontend
vercel --prod

# View Hugging Face logs
# Go to Space → Logs tab in browser

# View Vercel logs
vercel logs

# Test backend health
curl https://YOUR_USERNAME-todo-app-backend.hf.space/health
```

---

## Support

If you encounter issues:

1. **Check logs first**:
   - Hugging Face: Space → Logs tab
   - Vercel: Deployments → View Function Logs
   - Neon: Dashboard → Monitoring

2. **Common fixes**:
   - Redeploy both frontend and backend
   - Clear Vercel cache
   - Factory reboot Hugging Face Space (Settings)
   - Check all environment variables/secrets
   - Verify CORS settings

3. **Test endpoints**:
   - Backend health: `/health`
   - API docs: `/docs`
   - Frontend: homepage

4. **Hugging Face Specific**:
   - Free tier may have cold starts (first request slower)
   - Check Space status indicator (should be green/running)
   - Verify Dockerfile builds locally first
   - Ensure port 7860 is used in application

---

**Deployment Complete!** 🎉

Your Todo application should now be live and accessible worldwide.
