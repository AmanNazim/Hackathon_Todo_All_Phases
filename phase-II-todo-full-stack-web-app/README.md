# Phase II: Todo Full-Stack Web Application

A modern multi-user web application with persistent storage, transitioning from the CLI interface to a responsive web interface with user authentication and database persistence.

## Overview

Phase II transforms the in-memory CLI todo application from Phase I into a full-stack web application with:
- **Frontend**: Next.js 16+ with App Router
- **Backend**: Python FastAPI API
- **Database**: Neon Serverless PostgreSQL with SQLModel ORM
- **Authentication**: Better Auth with JWT tokens
- **Architecture**: Clean separation of concerns with proper API design

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16+ (App Router), TypeScript, Tailwind CSS |
| Backend | Python FastAPI |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth with JWT |
| Spec-Driven | Claude Code + Spec-Kit Plus |

## Features

### Basic Level Functionality
- [ ] Add Task – Create new todo items
- [ ] Delete Task – Remove tasks from the list
- [ ] Update Task – Modify existing task details
- [ ] View Task List – Display all tasks
- [ ] Mark as Complete – Toggle task completion status

### Additional Web Features
- [ ] Multi-user support with authentication
- [ ] Persistent storage in database
- [ ] Responsive web interface
- [ ] RESTful API endpoints
- [ ] User session management
- [ ] Secure API with JWT authentication

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks for user |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion status |

## Database Schema

### Tasks Table
- `id`: integer (primary key)
- `user_id`: string (foreign key to users.id)
- `title`: string (not null)
- `description`: text (nullable)
- `completed`: boolean (default false)
- `created_at`: timestamp
- `updated_at`: timestamp

## Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hackathon-II-todo-all-phases
   ```

2. Navigate to Phase II:
   ```bash
   cd phase-II-todo-full-stack-web-app
   ```

3. Set up frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Set up backend:
   ```bash
   cd backend
   uv venv
   source .venv/bin/activate
   pip install fastapi sqlmodel python-multipart python-jose[cryptography] passlib[bcrypt] psycopg2-binary
   uvicorn main:app --reload
   ```

## Authentication Flow

1. User logs in on Frontend → Better Auth creates session and issues JWT token
2. Frontend makes API calls → Includes JWT token in Authorization: Bearer `<token>` header
3. Backend receives request → Verifies JWT signature using shared secret
4. Backend identifies user → Matches user ID in token with user ID in URL
5. Backend filters data → Returns only tasks belonging to that user

## Next Steps

1. Create Phase II specifications (spec, plan, tasks)
2. Implement FastAPI backend with SQLModel and database
3. Create Next.js frontend with authentication
4. Integrate Better Auth for user management
5. Connect frontend to backend API
6. Test multi-user functionality