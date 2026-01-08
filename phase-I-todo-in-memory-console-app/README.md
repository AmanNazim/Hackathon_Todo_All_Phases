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
   python -m src.main
   ```

## Usage

### Menu Mode
Start the application in menu mode for guided interaction:
```
CLI Todo App
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete
6. Help
7. Exit
Choose option: _
```

### Natural Language Mode
Use natural language commands for quick task management:
```
> add Buy groceries
> list
> complete 1
> update 1 Buy organic groceries
> delete 2
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
- `add "task title" [description]` - Add a new task
- `list [completed|pending|all]` - View tasks with filters
- `update <id> "new title" [new description]` - Update a task
- `delete <id>` - Remove a task
- `complete <id>` or `done <id>` - Mark task as complete
- `undo` - Reverse the last command

### System Features
- `help` - Show available commands
- `theme <name>` - Change display theme
- `macro record|play|list` - Manage command macros
- `snapshot save|load|list` - Manage application snapshots

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