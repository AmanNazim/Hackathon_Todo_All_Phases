"""
Rendering & Themes System for CLI Todo Application
Implements rendering engine and theme management as specified in spec section 13
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Protocol
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import textwrap
import time


class ThemeType(Enum):
    """Available theme types"""
    MINIMAL = "minimal"
    EMOJI = "emoji"
    HACKER = "hacker"
    PROFESSIONAL = "professional"


@dataclass
class TaskItem:
    """Represents a task item for rendering"""
    id: str
    title: str
    description: str = ""
    status: str = "PENDING"
    created_at: datetime = None
    updated_at: datetime = None
    tags: List[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.tags is None:
            self.tags = []


class BaseRenderer(ABC):
    """
    Create base renderer interface for output formatting (T080)
    """

    @abstractmethod
    def render_task_list(self, tasks: List[TaskItem]) -> str:
        """Render a list of tasks"""
        pass

    @abstractmethod
    def render_single_task(self, task: TaskItem) -> str:
        """Render a single task"""
        pass

    @abstractmethod
    def render_success_message(self, message: str) -> str:
        """Render a success message"""
        pass

    @abstractmethod
    def render_error_message(self, message: str) -> str:
        """Render an error message"""
        pass

    @abstractmethod
    def render_status_indicator(self, status: str) -> str:
        """Render a status indicator"""
        pass

    @abstractmethod
    def render_header(self, title: str) -> str:
        """Render a header"""
        pass

    @abstractmethod
    def render_footer(self) -> str:
        """Render a footer"""
        pass


class MinimalTheme(BaseRenderer):
    """
    Implement minimal theme with plain text formatting (T081)
    """

    def render_task_list(self, tasks: List[TaskItem]) -> str:
        """Render task list in minimal theme format"""
        if not tasks:
            return "No tasks found."

        # Header
        header = "ID  Title                           Status\n"
        separator = "--- --------------------------------------- ------\n"

        # Task rows
        rows = []
        for task in tasks:
            status_indicator = self.render_status_indicator(task.status)
            title_truncated = task.title[:30] + "..." if len(task.title) > 30 else task.title
            row = f"{task.id:<3} {title_truncated:<30} {status_indicator}"
            rows.append(row)

        return header + separator + "\n".join(rows)

    def render_single_task(self, task: TaskItem) -> str:
        """Render a single task in minimal format"""
        status_indicator = self.render_status_indicator(task.status)
        result = f"Task #{task.id}: {task.title}\n"
        result += f"Status: {status_indicator}\n"
        if task.description:
            result += f"Description: {task.description}\n"
        if task.tags:
            result += f"Tags: {', '.join(task.tags)}\n"
        return result.rstrip()

    def render_success_message(self, message: str) -> str:
        """Render success message in minimal format"""
        return f"[SUCCESS] {message}"

    def render_error_message(self, message: str) -> str:
        """Render error message in minimal format"""
        return f"[ERROR] {message}"

    def render_status_indicator(self, status: str) -> str:
        """Render status indicator for minimal theme"""
        status_upper = status.upper()
        if status_upper == "COMPLETED":
            return "[x]"
        else:
            return "[ ]"

    def render_header(self, title: str) -> str:
        """Render header in minimal format"""
        return f"\n{title}\n{'=' * len(title)}"

    def render_footer(self) -> str:
        """Render footer in minimal format"""
        return "-" * 20


class EmojiTheme(BaseRenderer):
    """
    Implement emoji theme with visual indicators (T082)
    """

    def render_task_list(self, tasks: List[TaskItem]) -> str:
        """Render task list in emoji theme format"""
        if not tasks:
            return "📭 No tasks found."

        # Header
        header = "🔢  Title                           📊\n"
        separator = "--- --------------------------------------- -----\n"

        # Task rows
        rows = []
        for task in tasks:
            status_indicator = self.render_status_indicator(task.status)
            title_truncated = task.title[:30] + "…" if len(task.title) > 30 else task.title
            row = f"{task.id:<3} {title_truncated:<30} {status_indicator}"
            rows.append(row)

        return f"📋 Task List\n{header}{separator}" + "\n".join(rows)

    def render_single_task(self, task: TaskItem) -> str:
        """Render a single task in emoji format"""
        status_indicator = self.render_status_indicator(task.status)
        result = f"📝 Task #{task.id}: {task.title}\n"
        result += f"📊 Status: {status_indicator}\n"
        if task.description:
            result += f"💬 Description: {task.description}\n"
        if task.tags:
            result += f"🏷️  Tags: {', '.join(task.tags)}\n"
        return result.rstrip()

    def render_success_message(self, message: str) -> str:
        """Render success message in emoji format"""
        return f"✅ {message}"

    def render_error_message(self, message: str) -> str:
        """Render error message in emoji format"""
        return f"❌ {message}"

    def render_status_indicator(self, status: str) -> str:
        """Render status indicator for emoji theme"""
        status_upper = status.upper()
        if status_upper == "COMPLETED":
            return "✅"
        else:
            return "⏳"

    def render_header(self, title: str) -> str:
        """Render header in emoji format"""
        return f"\n🎯 {title}\n{'=' * (len(title) + 2)}"

    def render_footer(self) -> str:
        """Render footer in emoji format"""
        return "🔚" * 10


class HackerTheme(BaseRenderer):
    """
    Implement hacker theme with monochrome styling (T083)
    """

    def render_task_list(self, tasks: List[TaskItem]) -> str:
        """Render task list in hacker theme format"""
        if not tasks:
            return "[0x00] No tasks found."

        # Header with hacker-style formatting
        header = "IDX  TITLE                          STATUS\n"
        separator = "---- ---------------------------------------- ------\n"

        # Task rows with hacker styling
        rows = []
        for task in tasks:
            status_indicator = self.render_status_indicator(task.status)
            title_truncated = task.title[:30] + "..." if len(task.title) > 30 else task.title
            row = f"0x{int(task.id):02x} {title_truncated:<30} {status_indicator}"
            rows.append(row)

        return f"┌─ SYSTEM TASKS ──────────────────────────────────────┐\n{header}{separator}" + "\n".join(rows) + "\n└─────────────────────────────────────────────────────┘"

    def render_single_task(self, task: TaskItem) -> str:
        """Render a single task in hacker format"""
        status_indicator = self.render_status_indicator(task.status)
        result = f"┌─ TASK 0x{int(task.id):02x} ──────────────────────────────────────┐\n"
        result += f"│ Title: {task.title:<40} │\n"
        result += f"│ Status: {status_indicator:<40} │\n"
        if task.description:
            desc_lines = textwrap.wrap(task.description, width=40)
            result += f"│ Desc: {desc_lines[0]:<40} │\n"
            for line in desc_lines[1:]:
                result += f"│      {line:<40} │\n"
        if task.tags:
            result += f"│ Tags: {', '.join(task.tags):<40} │\n"
        result += "└─────────────────────────────────────────────────────┘"
        return result

    def render_success_message(self, message: str) -> str:
        """Render success message in hacker format"""
        return f"[✓] {message}"

    def render_error_message(self, message: str) -> str:
        """Render error message in hacker format"""
        return f"[✗] {message}"

    def render_status_indicator(self, status: str) -> str:
        """Render status indicator for hacker theme"""
        status_upper = status.upper()
        if status_upper == "COMPLETED":
            return "[✓]"
        else:
            return "[○]"

    def render_header(self, title: str) -> str:
        """Render header in hacker format"""
        return f"\n┌─ {title.upper()} ──────────────────────────────────────┐\n{'│':<50} │"

    def render_footer(self) -> str:
        """Render footer in hacker format"""
        return "└─────────────────────────────────────────────────────┘"


class ProfessionalTheme(BaseRenderer):
    """
    Implement professional theme with clean appearance (T084)
    """

    def render_task_list(self, tasks: List[TaskItem]) -> str:
        """Render task list in professional theme format"""
        if not tasks:
            return "No tasks found in your list."

        # Professional table format
        result = "┌─────┬──────────────────────────────┬─────────────────┐\n"
        result += "│ ID  │ Title                        │ Status          │\n"
        result += "├─────┼──────────────────────────────┼─────────────────┤\n"

        for task in tasks:
            status_indicator = self.render_status_indicator(task.status)
            title_truncated = task.title[:26] + "..." if len(task.title) > 26 else task.title
            result += f"│ {task.id:>3} │ {title_truncated:<26} │ {status_indicator:<15} │\n"

        result += "└─────┴──────────────────────────────┴─────────────────┘"
        return result

    def render_single_task(self, task: TaskItem) -> str:
        """Render a single task in professional format"""
        status_indicator = self.render_status_indicator(task.status)
        result = "┌─────────────────────────────────────────────────────────┐\n"
        result += f"│ Task ID: {task.id:<44} │\n"
        result += f"│ Title:   {task.title:<44} │\n"
        result += f"│ Status:  {status_indicator:<44} │\n"
        if task.description:
            desc_lines = textwrap.fill(task.description, width=45).split('\n')
            result += f"│ Desc:    {desc_lines[0]:<44} │\n"
            for line in desc_lines[1:]:
                result += f"│         {line:<44} │\n"
        if task.tags:
            result += f"│ Tags:    {', '.join(task.tags):<44} │\n"
        result += "└─────────────────────────────────────────────────────────┘"
        return result

    def render_success_message(self, message: str) -> str:
        """Render success message in professional format"""
        return f"✓ Success: {message}"

    def render_error_message(self, message: str) -> str:
        """Render error message in professional format"""
        return f"✗ Error: {message}"

    def render_status_indicator(self, status: str) -> str:
        """Render status indicator for professional theme"""
        status_upper = status.upper()
        if status_upper == "COMPLETED":
            return "Completed"
        else:
            return "Pending"

    def render_header(self, title: str) -> str:
        """Render header in professional format"""
        return f"\n┌─ {title} {'─' * (50 - len(title) - 4)} ─┐\n│{' ' * 50}│"

    def render_footer(self) -> str:
        """Render footer in professional format"""
        return "└─────────────────────────────────────────────────────────┘"


class TaskListRenderer:
    """
    Create task list renderer with ID, title, status columns (T085)
    """

    def __init__(self, renderer: BaseRenderer):
        self.renderer = renderer

    def render(self, tasks: List[TaskItem], limit: int = 100) -> str:
        """
        Render task list with performance optimization
        """
        start_time = time.time()

        # Limit tasks for performance
        limited_tasks = tasks[:limit]

        result = self.renderer.render_task_list(limited_tasks)

        # Performance check
        elapsed = (time.time() - start_time) * 1000  # Convert to milliseconds

        # For now, just return the result - performance validation would happen in tests
        return result

    def render_paginated(self, tasks: List[TaskItem], page_size: int = 50, page: int = 1) -> Dict[str, Any]:
        """
        Render paginated task list for large datasets
        """
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_tasks = tasks[start_idx:end_idx]

        result = self.renderer.render_task_list(page_tasks)

        return {
            'content': result,
            'page': page,
            'page_size': page_size,
            'total_tasks': len(tasks),
            'has_next': end_idx < len(tasks),
            'has_prev': page > 1,
            'total_pages': (len(tasks) + page_size - 1) // page_size
        }


class ThemeManager:
    """
    Implement theme switching functionality (T088)
    """

    def __init__(self):
        self.themes = {
            ThemeType.MINIMAL: MinimalTheme(),
            ThemeType.EMOJI: EmojiTheme(),
            ThemeType.HACKER: HackerTheme(),
            ThemeType.PROFESSIONAL: ProfessionalTheme()
        }
        self.current_theme = ThemeType.MINIMAL
        self._last_render_time = 0.0

    def get_renderer(self) -> BaseRenderer:
        """Get the current renderer"""
        return self.themes[self.current_theme]

    def set_theme(self, theme_type: ThemeType) -> bool:
        """Switch to a different theme"""
        if theme_type in self.themes:
            self.current_theme = theme_type
            return True
        return False

    def get_available_themes(self) -> List[ThemeType]:
        """Get list of available themes"""
        return list(self.themes.keys())

    def get_current_theme(self) -> ThemeType:
        """Get the current theme"""
        return self.current_theme

    def render_with_theme(self, theme_type: ThemeType, tasks: List[TaskItem]) -> str:
        """Temporarily render with a specific theme"""
        original_theme = self.current_theme
        self.current_theme = theme_type
        result = self.get_renderer().render_task_list(tasks)
        self.current_theme = original_theme
        return result


class MessageFormatter:
    """
    Add success/failure message formatting (T087)
    """

    def __init__(self, renderer: BaseRenderer):
        self.renderer = renderer

    def format_success(self, message: str, details: str = None) -> str:
        """Format a success message"""
        result = self.renderer.render_success_message(message)
        if details:
            result += f"\n{details}"
        return result

    def format_error(self, message: str, details: str = None) -> str:
        """Format an error message"""
        result = self.renderer.render_error_message(message)
        if details:
            result += f"\nDetails: {details}"
        return result

    def format_warning(self, message: str) -> str:
        """Format a warning message"""
        return f"⚠ Warning: {message}"


class StatusRenderer:
    """
    Implement status indicator rendering (pending/completed) (T086)
    """

    def __init__(self, renderer: BaseRenderer):
        self.renderer = renderer

    def render_status(self, status: str) -> str:
        """Render status using the current renderer"""
        return self.renderer.render_status_indicator(status)

    def render_status_block(self, status: str, label: str = None) -> str:
        """Render a status block with optional label"""
        indicator = self.render_status(status)
        if label:
            return f"{label}: {indicator}"
        return indicator