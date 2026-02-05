# Hackathon II: The Evolution of Todo – Mastering Spec-Driven Development & Cloud Native AI

This repository contains the complete implementation of the 5-phase "Evolution of Todo" project, showcasing the progression from a simple CLI app to a cloud-native AI system.

## Project Structure

- `phase-I-todo-in-memory-console-app/` - Phase I: In-Memory Python CLI Todo Application
- `phase-I-todo-in-memory-console-app/specs/` - Phase I specifications (constitution, spec, plan, tasks)
- `history/` - Prompt History Records and Architectural Decision Records
- `.specify/` - Spec-Kit Plus configuration and templates
- `.claude/` - Claude Code configuration and commands

## Phase I: CLI Todo Application

The current implementation includes:

- **CLI Interface**: Hybrid interaction modes (menu-based and command-based)
- **Improved UI**: Enhanced spacing and formatting for better readability
- **Task Management**: Add, list, update, delete, complete/incomplete tasks
- **Event Sourcing**: In-memory event tracking for all operations
- **Plugin Architecture**: Extensible system with various plugin types

### Running the Application

Navigate to the Phase I directory and run:

```bash
cd phase-I-todo-in-memory-console-app
python -m src.cli_todo_app.main

# Or using UV (recommended):
uv run cli-todo
```

## Project Goals

This hackathon project demonstrates:
- Spec-Driven Development using Claude Code and Spec-Kit Plus
- Progressive evolution from CLI to cloud-native AI systems
- Clean architecture and separation of concerns
- Comprehensive testing and documentation