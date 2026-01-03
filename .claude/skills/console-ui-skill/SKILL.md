---
name: console-ui-skill
description: Teaches advanced CLI UI design and implementation strategies for Python console applications, including modern color schemes, formatting standards, animated transitions, emoji indicators, interactive behaviors, accessibility considerations, and recommended libraries.
---

# Console UI Skill Documentation

## 1. Introduction
- **Purpose of the skill**: To provide comprehensive guidance for designing and implementing advanced, premium CLI user interfaces for Python console applications
- **Scope**: Focuses on CLI UI design principles, implementation techniques, and best practices for creating professional command-line interfaces
- **When to apply**: Use when creating CLI applications that require professional UI design, enhanced user experience, or complex interactive features

## 2. CLI UI Design Principles
- **Clarity, consistency, discoverability**: Ensure commands and options are clearly named and consistently formatted
- **UX best practices for CLIs**: Follow established patterns for argument order, flag naming, and command structure
- **Information hierarchy**: Organize information in a logical flow that guides users through tasks
- **Feedback timing**: Provide immediate feedback for user actions, with appropriate delays for long-running operations

## 3. Interaction Models
- **Hybrid menu + natural commands**: Combine structured menu options with natural language command parsing
- **Progressive disclosure**: Show basic options by default, with advanced options available through flags or subcommands
- **Error-aware interaction flows**: Design interactions that anticipate and gracefully handle user errors

## 4. Color Schemes & Themes
- **Color palettes and semantic meanings**: Use green for success, red for error, yellow for warning, blue for information
- **Theme strategy**: Support both light and dark terminal themes, with high contrast options for accessibility
- **Library support**: Utilize Rich, colorama, or similar libraries for consistent color rendering

## 5. Output Formatting & Layout
- **Tables, panels, lists**: Use structured layouts to organize information clearly
- **Consistent spacing**: Apply consistent indentation and whitespace throughout the interface
- **Font effects**: Use bold, underline, and other effects sparingly and consistently
- **Column alignment**: Align related information in columns for easy scanning
- **Screen size sensitivity**: Adapt layouts based on terminal width when possible

## 6. Animated Transitions & Feedback
- **Progress indicators**: Implement spinners and loading bars for long-running operations
- **Subtle timing**: Use brief delays that enhance UX without feeling sluggish
- **When NOT to animate**: Respect TTY detection and disable animations when output is piped to files

## 7. Emoji & Iconography Usage
- **When to use emojis**: Use for success, warning, info, and error indicators
- **Accessibility considerations**: Provide text alternatives when emojis aren't supported
- **Turn-off flags**: Allow users to disable emoji usage through environment variables

## 8. Interactive Prompts & Input Assistance
- **Auto-suggestions**: Provide context-aware suggestions for command completion
- **Confirmation dialogs**: Request confirmation for destructive actions
- **Intelligent error feedback**: Provide helpful error messages with suggestions for correction

## 9. Accessibility Considerations
- **Graceful degradation**: Ensure UI works when colors or Unicode aren't supported
- **Screen reader friendly output**: Use semantic structure and avoid purely visual indicators
- **Toggleable verbosity**: Allow users to control the level of detail in output

## 10. Edge Cases & CLI UI Failures
- **Terminal width limitations**: Handle narrow terminals gracefully
- **Unsupported terminals**: Detect and adapt to basic terminal capabilities
- **UI chattiness controls**: Provide quiet modes for scripting
- **JSON/text output toggles**: Support machine-readable output formats

## 11. Recommended Libraries & Tools (Python)

### Rendering & Layout
- **rich** – high level formatting and styles
- **textual** – interactive widget-based UIs

### Prompting & Interaction
- **Prompt Toolkit** – advanced input features
- **questionary / InquirerPy** – interactive prompts

### Basic UI Helpers
- `colorama`, `cli-ui`
- Animated indicators and progress libraries

## 12. Detailed Implementation Patterns
- **Theme provider pattern**: Centralize theme and color definitions
- **Centralized renderer module**: Create a single module responsible for all UI rendering
- **UI context abstraction**: Abstract terminal capabilities and user preferences
- **Output builder functions**: Create reusable functions for common UI patterns
- **Interactive flow controllers**: Separate interaction logic from rendering logic

## 13. Code Snippet Templates

### Basic Rich UI Template
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def display_task_list(tasks):
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Status", justify="center")

    for task in tasks:
        status = "[green]✓[/green]" if task.completed else "[red]✗[/red]"
        table.add_row(str(task.id), task.title, status)

    console.print(table)

def show_success(message):
    console.print(f"[green]✓ {message}[/green]")

def show_error(message):
    console.print(f"[red]✗ {message}[/red]")
```

### Theme Provider Pattern
```python
from dataclasses import dataclass
from rich.style import Style
from rich.theme import Theme

@dataclass
class UITheme:
    success: Style = Style(color="green")
    error: Style = Style(color="red", bold=True)
    warning: Style = Style(color="yellow")
    info: Style = Style(color="blue")
    primary: Style = Style(color="cyan")
    secondary: Style = Style(color="magenta")

class ThemeProvider:
    def __init__(self):
        self.theme = UITheme()
        self.rich_theme = Theme({
            "success": self.theme.success,
            "error": self.theme.error,
            "warning": self.theme.warning,
            "info": self.theme.info,
        })
```

### Interactive Flow Controller
```python
from enum import Enum
from typing import Optional

class UIState(Enum):
    MENU = "menu"
    TASK_LIST = "task_list"
    ADD_TASK = "add_task"
    DELETE_TASK = "delete_task"

class UIController:
    def __init__(self, console):
        self.console = console
        self.state = UIState.MENU

    def handle_input(self, user_input: str) -> Optional[UIState]:
        # Process user input and return next state
        pass

    def render(self):
        # Render current UI based on state
        pass
```

## 14. Learning References & Documentation

### CLI UX Guidelines
- Command Line Interface Guidelines: https://clig.dev/
- Python CLI Development Guide: https://realpython.com/command-line-interfaces-python-argparse/
- Rich Documentation: https://rich.readthedocs.io/

### Design Resources
- CLI UX Best Practices: https://www.smashingmagazine.com/2021/03/cli-ux-design-best-practices/
- Accessibility in CLI Tools: https://www.w3.org/WAI/
- ANSI Color Codes Guide: https://en.wikipedia.org/wiki/ANSI_escape_code

### Library Documentation
- Rich: Advanced formatting: https://rich.readthedocs.io/en/latest/
- Prompt Toolkit: Interactive input: https://python-prompt-toolkit.readthedocs.io/
- Textual: Widget-based UIs: https://textual.textualize.io/

## Helper Tools

The skill includes:
- `scripts/ui_tester.sh` - Command-line helper for testing UI components
- `references/ui-patterns.md` - Detailed UI patterns and examples
- `assets/ui-components.json` - Component specification schema