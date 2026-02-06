# Hackathon II: The Evolution of Todo – Mastering Spec-Driven Development & Cloud Native AI

This repository contains the complete implementation of the 5-phase "Evolution of Todo" project, showcasing the progression from a simple CLI app to a cloud-native AI system.

## Project Structure

- `phase-I-todo-in-memory-console-app/` - Phase I: In-Memory Python CLI Todo Application
- `phase-I-todo-in-memory-console-app/specs/` - Phase I specifications (constitution, spec, plan, tasks)
- `phase-II-todo-full-stack-web-app/` - Phase II: Full-Stack Web Application with Next.js, FastAPI, SQLModel
- `phase-II-todo-full-stack-web-app/specs/` - Phase II specifications (spec, plan, tasks)
- `history/` - Prompt History Records and Architectural Decision Records
- `.specify/` - Spec-Kit Plus configuration and templates
- `.claude/` - Claude Code configuration and commands

## Phase I: CLI Todo Application (Complete)

Phase I implementation includes:

- **CLI Interface**: Hybrid interaction modes (menu-based and command-based)
- **Improved UI**: Enhanced spacing and formatting for better readability
- **Task Management**: Add, list, update, delete, complete/incomplete tasks
- **Event Sourcing**: In-memory event tracking for all operations
- **Plugin Architecture**: Extensible system with various plugin types

## Phase II: Full-Stack Web Application (Complete)

Phase II successfully transformed the CLI app into a modern multi-user web application with persistent storage:

- **Frontend**: Next.js 16+ with App Router, TypeScript, Tailwind CSS
- **Backend**: Python FastAPI API with comprehensive endpoints
- **Database**: Neon Serverless PostgreSQL with SQLModel ORM
- **Authentication**: JWT-based authentication with user isolation
- **Features**: Complete task management (CRUD), multi-user support, responsive UI
- **Architecture**: Clean separation of concerns with secure API design

### Running the Applications

#### Phase I: CLI Application
Navigate to the Phase I directory and run:

```bash
cd phase-I-todo-in-memory-console-app
python -m src.cli_todo_app.main

# Or using UV (recommended):
uv run cli-todo
```

#### Phase II: Web Application
Navigate to the Phase II directory and run:

```bash
# Backend (FastAPI):
cd phase-II-todo-full-stack-web-app/backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
python run.py

# Frontend (Next.js):
cd phase-II-todo-full-stack-web-app/frontend
npm install
npm run dev
```

## Project Goals

This hackathon project demonstrates:
- Spec-Driven Development using Claude Code and Spec-Kit Plus
- Progressive evolution from CLI to cloud-native AI systems
- Clean architecture and separation of concerns
- Comprehensive testing and documentation