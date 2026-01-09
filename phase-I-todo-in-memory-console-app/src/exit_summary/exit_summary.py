"""
Exit Summary System for CLI Todo Application
Implements T150-T154: Exit Summary functionality
"""
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class SessionStatistics:
    """Container for session statistics"""
    total_tasks_created: int = 0
    tasks_completed: int = 0
    commands_executed: int = 0
    session_start_time: Optional[datetime] = None
    session_end_time: Optional[datetime] = None
    session_duration_seconds: float = 0.0
    tasks_deleted: int = 0
    tasks_updated: int = 0
    tasks_reopened: int = 0

    def get_session_duration_formatted(self) -> str:
        """Get formatted session duration"""
        if self.session_duration_seconds > 0:
            seconds = int(self.session_duration_seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if hours > 0:
                return f"{hours}h {minutes}m {secs}s"
            elif minutes > 0:
                return f"{minutes}m {secs}s"
            else:
                return f"{secs}s"
        return "0s"


class ExitSummaryTracker:
    """Tracks session statistics for exit summary"""

    def __init__(self):
        self._stats = SessionStatistics()
        self._stats.session_start_time = datetime.now()
        self._lock = threading.RLock()

    def increment_tasks_created(self) -> None:
        """Increment the total tasks created counter (T151)"""
        with self._lock:
            self._stats.total_tasks_created += 1

    def increment_tasks_completed(self) -> None:
        """Increment the tasks completed counter (T152)"""
        with self._lock:
            self._stats.tasks_completed += 1

    def increment_commands_executed(self) -> None:
        """Increment the commands executed counter (T153)"""
        with self._lock:
            self._stats.commands_executed += 1

    def increment_tasks_deleted(self) -> None:
        """Increment the tasks deleted counter"""
        with self._lock:
            self._stats.tasks_deleted += 1

    def increment_tasks_updated(self) -> None:
        """Increment the tasks updated counter"""
        with self._lock:
            self._stats.tasks_updated += 1

    def increment_tasks_reopened(self) -> None:
        """Increment the tasks reopened counter"""
        with self._lock:
            self._stats.tasks_reopened += 1

    def get_current_statistics(self) -> SessionStatistics:
        """Get current session statistics (T150)"""
        with self._lock:
            # Calculate session duration if not already calculated
            if self._stats.session_end_time:
                duration = (self._stats.session_end_time - self._stats.session_start_time).total_seconds()
                self._stats.session_duration_seconds = duration
            elif self._stats.session_start_time:
                duration = (datetime.now() - self._stats.session_start_time).total_seconds()
                self._stats.session_duration_seconds = duration
            return SessionStatistics(
                total_tasks_created=self._stats.total_tasks_created,
                tasks_completed=self._stats.tasks_completed,
                commands_executed=self._stats.commands_executed,
                session_start_time=self._stats.session_start_time,
                session_end_time=self._stats.session_end_time,
                session_duration_seconds=self._stats.session_duration_seconds,
                tasks_deleted=self._stats.tasks_deleted,
                tasks_updated=self._stats.tasks_updated,
                tasks_reopened=self._stats.tasks_reopened
            )

    def finalize_session(self) -> SessionStatistics:
        """Finalize the session and calculate final statistics (T154)"""
        with self._lock:
            self._stats.session_end_time = datetime.now()
            duration = (self._stats.session_end_time - self._stats.session_start_time).total_seconds()
            self._stats.session_duration_seconds = duration
            return self.get_current_statistics()

    def reset_counters(self) -> None:
        """Reset all counters for a new session"""
        with self._lock:
            self._stats = SessionStatistics()
            self._stats.session_start_time = datetime.now()

    def get_summary_text(self) -> str:
        """Get formatted summary text for display (T154)"""
        stats = self.get_current_statistics()

        summary_lines = [
            "",
            "┌─────────────────────────────────────────┐",
            "│           SESSION SUMMARY               │",
            "├─────────────────────────────────────────┤",
            f"│ Tasks Created:       {stats.total_tasks_created:>16} │",
            f"│ Tasks Completed:     {stats.tasks_completed:>16} │",
            f"│ Tasks Deleted:       {stats.tasks_deleted:>16} │",
            f"│ Tasks Updated:       {stats.tasks_updated:>16} │",
            f"│ Tasks Reopened:      {stats.tasks_reopened:>16} │",
            f"│ Commands Executed:   {stats.commands_executed:>16} │",
            f"│ Session Duration:    {stats.get_session_duration_formatted():>16} │",
            "├─────────────────────────────────────────┤",
            "│ Thank you for using CLI Todo App!       │",
            "│ Have a productive day!                  │",
            "└─────────────────────────────────────────┘",
            ""
        ]

        return "\n".join(summary_lines)


class ExitSummaryDisplay:
    """Handles display of exit summary information (T154)"""

    def __init__(self, tracker: ExitSummaryTracker):
        self.tracker = tracker

    def display_exit_summary(self) -> str:
        """Display the exit summary at application termination (T154)"""
        # Finalize the session statistics
        final_stats = self.tracker.finalize_session()

        # Generate formatted summary
        summary_text = self.tracker.get_summary_text()

        return summary_text

    def display_intermediate_summary(self) -> str:
        """Display current session summary without finalizing (for debugging/testing)"""
        return self.tracker.get_summary_text()

    def register_command_execution(self) -> None:
        """Register a command execution for tracking (T153)"""
        self.tracker.increment_commands_executed()

    def register_task_creation(self) -> None:
        """Register a task creation for tracking (T151)"""
        self.tracker.increment_tasks_created()

    def register_task_completion(self) -> None:
        """Register a task completion for tracking (T152)"""
        self.tracker.increment_tasks_completed()

    def register_task_deletion(self) -> None:
        """Register a task deletion for tracking"""
        self.tracker.increment_tasks_deleted()

    def register_task_update(self) -> None:
        """Register a task update for tracking"""
        self.tracker.increment_tasks_updated()

    def register_task_reopen(self) -> None:
        """Register a task reopen for tracking"""
        self.tracker.increment_tasks_reopened()