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
- [X] Add Task – Create new todo items
- [X] Delete Task – Remove tasks from the list
- [X] Update Task – Modify existing task details
- [X] View Task List – Display all tasks
- [X] Mark as Complete – Toggle task completion status

### Additional Web Features
- [X] Multi-user support with authentication
- [X] Persistent storage in database
- [X] Responsive web interface
- [X] RESTful API endpoints
- [X] User session management
- [X] Secure API with JWT authentication

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
   uv pip install -r requirements.txt
   python run.py
   ```

## Authentication Flow

1. User logs in on Frontend → Better Auth creates session and issues JWT token
2. Frontend makes API calls → Includes JWT token in Authorization: Bearer `<token>` header
3. Backend receives request → Verifies JWT signature using shared secret
4. Backend identifies user → Matches user ID in token with user ID in URL
5. Backend filters data → Returns only tasks belonging to that user

## Project Structure

```
phase-II-todo-full-stack-web-app/
├── backend/
│   ├── main.py                 # Main FastAPI application
│   ├── run.py                  # Script to run the application
│   ├── models.py               # SQLModel database models
│   ├── auth.py                 # Authentication utilities
│   ├── database/
│   │   ├── __init__.py         # Database connection setup
│   │   ├── database.py         # Database configuration
│   │   └── init_db.py          # Database initialization
│   ├── routes/
│   │   ├── tasks.py            # Task management API routes
│   │   └── auth.py             # Authentication API routes
│   ├── middleware.py           # Custom middleware
│   ├── requirements.txt        # Python dependencies
│   └── alembic/                # Database migration files
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   ├── components/         # React components
│   │   ├── lib/                # Utility functions
│   │   ├── types/              # TypeScript type definitions
│   │   └── styles/             # Global styles
│   ├── package.json            # Node.js dependencies
│   └── next.config.ts          # Next.js configuration
├── specs/                      # Specification documents
│   ├── spec.md                 # Feature specification
│   ├── plan.md                 # Implementation plan
│   └── tasks.md                # Development tasks
└── README.md                   # This file
```

## Running the Application

### Backend (FastAPI)
1. Navigate to the backend directory: `cd backend`
2. Create virtual environment: `uv venv`
3. Activate virtual environment: `source .venv/bin/activate`
4. Install dependencies: `uv pip install -r requirements.txt`
5. Run the application: `python run.py`

### Frontend (Next.js)
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run the development server: `npm run dev`
4. Visit `http://localhost:3000` in your browser

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://localhost/todo_app_dev
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

Unit and integration tests for both frontend and backend components are located in their respective directories. Run tests using:
- Backend: `pytest` (if using pytest)
- Frontend: `npm run test`

## Deployment

The application is designed to be deployed separately:
- Backend: Deploy to any Python hosting service (Heroku, AWS, etc.)
- Frontend: Deploy to Vercel, Netlify, or any static hosting service

Configure environment variables appropriately for each deployment environment.