# Local Development Setup Guide

This guide will help you set up and run the Todo Full-Stack Web Application locally for testing.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v20 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.11 or higher) - [Download](https://www.python.org/)
- **PostgreSQL** (v15 or higher) - [Download](https://www.postgresql.org/)
- **Git** - [Download](https://git-scm.com/)

**Optional (Recommended):**
- **Docker** and **Docker Compose** - [Download](https://www.docker.com/)

---

## Quick Start (Using Docker - Recommended)

The easiest way to run the application locally is using Docker Compose:

### 1. Start All Services

```bash
# From the project root directory
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend application on port 3000

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 3. Stop All Services

```bash
docker-compose down
```

To remove all data (including database):
```bash
docker-compose down -v
```

---

## Manual Setup (Without Docker)

If you prefer to run services manually:

### 1. Set Up PostgreSQL Database

#### Option A: Local PostgreSQL Installation

```bash
# Create database and user
psql -U postgres
CREATE DATABASE todo_db;
CREATE USER todo_user WITH PASSWORD 'todo_password';
GRANT ALL PRIVILEGES ON DATABASE todo_db TO todo_user;
\q
```

#### Option B: Use Neon PostgreSQL (Cloud)

1. Sign up at [Neon](https://neon.tech/)
2. Create a new project
3. Copy the connection string
4. Update `backend/.env` with your Neon connection string

### 2. Set Up Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify .env file exists and is configured
# Edit backend/.env if needed

# Initialize database
python init_db.py

# Run the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### 3. Set Up Frontend (Next.js)

```bash
# Open a new terminal
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Verify .env file exists and is configured
# Edit frontend/.env if needed

# Run the development server
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## Environment Configuration

### Backend Environment Variables

Edit `backend/.env`:

```env
# Database - Update with your PostgreSQL connection
DATABASE_URL="postgresql://todo_user:todo_password@localhost:5432/todo_db"

# Authentication - Change these in production!
BETTER_AUTH_SECRET="dev-secret-key-change-in-production-min-32-chars"
JWT_SECRET="dev-jwt-secret-change-in-production-min-32-chars"

# CORS - Add your frontend URLs
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:3001"
```

### Frontend Environment Variables

Edit `frontend/.env`:

```env
# API URL - Update if backend runs on different port
NEXT_PUBLIC_API_URL="http://localhost:8000"

# App Configuration
NEXT_PUBLIC_APP_NAME="Todo App"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

---

## Testing the Application

### 1. Create a Test Account

1. Open http://localhost:3000
2. Click "Sign Up" or "Register"
3. Fill in the registration form:
   - Email: test@example.com
   - Password: Test123!@#
   - Name: Test User
4. Click "Create Account"

### 2. Log In

1. Use the credentials you just created
2. You should be redirected to the dashboard

### 3. Create Tasks

1. Click "New Task" or "Add Task"
2. Fill in task details:
   - Title: "My First Task"
   - Description: "Testing the application"
   - Priority: High
   - Due Date: Tomorrow
3. Click "Create"

### 4. Test Task Operations

- **View Tasks**: See your task list on the dashboard
- **Edit Task**: Click on a task to edit it
- **Complete Task**: Check the checkbox to mark as complete
- **Delete Task**: Click the delete button
- **Filter Tasks**: Use filters to sort by priority, status, etc.

---

## API Testing

### Using the Interactive API Documentation

1. Open http://localhost:8000/docs
2. You'll see the Swagger UI with all available endpoints
3. Click "Authorize" and enter your JWT token (obtained after login)
4. Test endpoints directly from the browser

### Using cURL

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'

# Get tasks (replace TOKEN with your JWT token)
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer TOKEN"
```

---

## Troubleshooting

### Backend Issues

**Problem**: Database connection error
```
Solution:
1. Verify PostgreSQL is running: pg_isready
2. Check DATABASE_URL in backend/.env
3. Ensure database exists: psql -U postgres -l
```

**Problem**: Module not found errors
```
Solution:
1. Activate virtual environment
2. Reinstall dependencies: pip install -r requirements.txt
```

**Problem**: Port 8000 already in use
```
Solution:
1. Find process: lsof -i :8000 (macOS/Linux) or netstat -ano | findstr :8000 (Windows)
2. Kill process or use different port: uvicorn main:app --port 8001
```

### Frontend Issues

**Problem**: Cannot connect to backend
```
Solution:
1. Verify backend is running: curl http://localhost:8000/health
2. Check NEXT_PUBLIC_API_URL in frontend/.env
3. Check browser console for CORS errors
```

**Problem**: Module not found errors
```
Solution:
1. Delete node_modules: rm -rf node_modules
2. Delete package-lock.json: rm package-lock.json
3. Reinstall: npm install
```

**Problem**: Port 3000 already in use
```
Solution:
1. Use different port: PORT=3001 npm run dev
2. Or kill existing process
```

### Docker Issues

**Problem**: Containers won't start
```
Solution:
1. Check logs: docker-compose logs
2. Rebuild: docker-compose build --no-cache
3. Remove volumes: docker-compose down -v
```

**Problem**: Database connection refused
```
Solution:
1. Wait for database to be ready (check health status)
2. Restart services: docker-compose restart
```

---

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Edit Python files in `backend/`
   - FastAPI will auto-reload (if using --reload flag)
   - Check logs for errors

2. **Frontend Changes**:
   - Edit TypeScript/React files in `frontend/src/`
   - Next.js will auto-reload
   - Check browser console for errors

3. **Database Changes**:
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Apply migration: `alembic upgrade head`

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

---

## Database Management

### View Database Contents

```bash
# Connect to database
psql -U todo_user -d todo_db

# List tables
\dt

# View users
SELECT * FROM users;

# View tasks
SELECT * FROM tasks;

# Exit
\q
```

### Reset Database

```bash
# Drop and recreate
psql -U postgres
DROP DATABASE todo_db;
CREATE DATABASE todo_db;
GRANT ALL PRIVILEGES ON DATABASE todo_db TO todo_user;
\q

# Reinitialize
cd backend
python init_db.py
```

---

## Next Steps

After successful local testing:

1. **Review Features**: Test all functionality thoroughly
2. **Check Performance**: Monitor response times and resource usage
3. **Security Review**: Verify authentication and authorization
4. **Prepare for Deployment**: Update environment variables for production
5. **Documentation**: Update any missing documentation

---

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review backend logs: `docker-compose logs backend`
3. Review frontend logs: `docker-compose logs frontend`
4. Check API documentation: http://localhost:8000/docs

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

**Last Updated**: 2026-02-09
**Version**: 1.0.0
