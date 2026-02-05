# Phase I: In-Memory Python CLI Todo Application

A sophisticated command-line todo application that provides complete task management through an intelligent CLI interface with hybrid interaction modes. The application implements in-memory event sourcing for all operations, supporting advanced features like undo, macros, and session management while maintaining strict in-memory only data storage with zero persistence.

## Features

- **Hybrid Interaction Modes**: Support for both menu-driven and natural language commands
- **Intelligent Command Processing**: Fuzzy command understanding and smart suggestions
- **Premium Task Rendering**: Multiple theme options (minimal, emoji, hacker, professional)
- **Advanced Command System**: Command history, undo functionality, and macro recording
- **Event Sourcing**: Complete in-memory event tracking for all operations
- **Plugin Architecture**: Extensible system with renderer, validator, command, and theme plugins
- **Session Management**: Snapshots, session summaries, and metadata tracking
- **Test Mode**: Machine-readable output for automated testing

## Prerequisites

- Python 3.13+
- UV package manager

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install dependencies using UV:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   # Direct Python execution
   python -m src.cli_todo_app.main

   # Or using UV run (recommended)
   uv run cli-todo
   ```

4. For test mode (machine-readable JSON output):
   ```bash
   python -m src.cli_todo_app.main --test-mode
   ```

## Usage

### Initial Selection
When starting the application, you'll be prompted to choose an interface mode:
```
==================================================
CLI Todo Application - Phase I
==================================================

Choose interface mode:
1. Command-based (type commands directly)
2. Menu-based (select options from numbered menu)
Type '1' or '2', or press Enter for command-based (default)
```

### Menu Mode
Start the application in menu mode for guided interaction:
```
-------------------------
         MENU
-------------------------
1. Add Task
2. List Tasks
3. Update Task
4. Delete Task
5. Complete Task
6. Mark Task Incomplete
7. Help
8. Exit
-------------------------
Select option (1-8):
```

### Command-Based Mode
Use command-based interface for quick task management:
```
========================================
Command-based mode activated
Type 'help' for available commands or 'exit' to quit
========================================
>
```

Example commands:
```
> add Buy groceries
> add Buy groceries | Need to buy milk, bread, eggs
> list
> list completed
> update 1 Buy organic groceries
> complete 1
> delete 2
> help
> exit
```

### Quick Actions
Single-character shortcuts for common operations:
- `a` for add
- `l` for list
- `c` for complete
- `d` for delete

### Advanced Features
- **Undo**: Reverse the last command with `undo` or `revert`
- **Themes**: Switch between display themes with `theme minimal|emoji|hacker|professional`
- **Macros**: Record command sequences with `macro record` and play back with `macro play <name>`
- **Snapshots**: Save and restore application state with `snapshot save|load`
- **Test Mode**: Use `--test-mode` for machine-readable JSON output

## Command Reference

### Task Management
- `add <title> [ | description]` - Add a new task (use ' | ' to separate title and description)
- `list [completed|pending|all]` - View tasks with filters
- `update <number_or_id> <new_title> [ | new_description]` - Update a task by number or ID
- `delete <number_or_id>` - Remove a task by number or ID
- `complete <number_or_id>` - Mark task as complete by number or ID
- `incomplete <number_or_id>` - Mark task as incomplete by number or ID

### System Features
- `help` - Show available commands
- `exit` or `quit` - Exit the application

## Architecture

The application follows a clean architecture with separation of concerns:

- **Domain Layer**: Task entities and business logic
- **Event System**: In-memory event sourcing for all operations
- **Command Processing**: BNF grammar-based command parsing
- **State Machine**: CLI state management
- **Middleware Pipeline**: Command processing pipeline with multiple stages
- **Rendering Engine**: Themeable UI output

## Development

This project follows the Spec-Driven Development methodology:
1. Specification → Plan → Tasks → Implementation
2. All code is generated using Claude Code
3. Strict adherence to the Phase I constitution

## Contributing

This project is built using Spec-Kit Plus methodology. All changes must follow the specification → plan → tasks → implementation flow. See the documentation in the `specs/` directory for details on the architecture and extension points.