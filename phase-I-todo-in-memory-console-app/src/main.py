"""
CLI Todo Application - Main Entry Point
Phase I: In-Memory Python CLI Todo Application
"""

import sys
import argparse
from datetime import datetime
import uuid
import json
import os
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

# Import configuration and logging infrastructure
from .config import get_config
from .logging_infrastructure import get_logger, handle_error, ValidationError, TaskNotFoundError


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


@dataclass
class Task:
    """Task entity as defined in specification section 6"""
    id: str
    title: str
    description: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    status: TaskStatus = TaskStatus.PENDING
    tags: List[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if self.tags is None:
            self.tags = []


class TodoApp:
    """Main CLI Todo Application class"""

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()
        self.tasks: Dict[str, Task] = {}
        self.command_history: List[Dict[str, Any]] = []
        self.session_start_time = datetime.now()

        self.logger.info("TodoApp initialized", extra={
            "max_title_length": self.config.max_title_length,
            "max_description_length": self.config.max_description_length,
            "pagination_threshold": self.config.pagination_threshold
        })

    def add_task(self, title: str, description: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
        """Add a new task to the application"""
        start_time = datetime.now()

        try:
            # Validate input according to spec section 6 using configuration
            if not title or len(title.strip()) == 0:
                raise ValidationError("Task title cannot be empty")
            if len(title) > self.config.max_title_length:
                raise ValidationError(f"Task title exceeds maximum length of {self.config.max_title_length} characters")
            if description and len(description) > self.config.max_description_length:
                raise ValidationError(f"Task description exceeds maximum length of {self.config.max_description_length} characters")

            # Validate tags if provided
            if tags:
                if len(tags) > self.config.max_tags_per_task:
                    raise ValidationError(f"Maximum of {self.config.max_tags_per_task} tags per task allowed")
                for tag in tags:
                    if not self._is_valid_tag(tag):
                        raise ValidationError(f"Invalid tag format: {tag}. Tags must be alphanumeric with hyphens/underscores only.")

            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                title=title.strip(),
                description=description,
                status=TaskStatus.PENDING,
                tags=tags or []
            )

            self.tasks[task_id] = task

            # Log the command for history and potential undo
            self._log_command("add_task", {
                "title": title,
                "description": description,
                "tags": tags,
                "task_id": task_id
            })

            # Performance logging
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(f"Task added successfully", extra={
                "task_id": task_id,
                "duration_ms": duration,
                "title_length": len(title)
            })

            if duration > self.config.add_task_timeout_ms:
                self.logger.warning(f"Add task operation took longer than expected", extra={
                    "duration_ms": duration,
                    "threshold_ms": self.config.add_task_timeout_ms
                })

            return task_id

        except ValidationError as e:
            self.logger.error(f"Validation error in add_task: {str(e)}", extra={
                "title_length": len(title) if title else 0,
                "has_description": description is not None
            })
            raise
        except Exception as e:
            error_info = handle_error(e, "add_task")
            raise ValidationError(f"Failed to add task: {error_info.get('message', str(e))}")

    def _is_valid_tag(self, tag: str) -> bool:
        """Validate tag format according to spec section 6"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', tag))

    def list_tasks(self, status_filter: Optional[str] = None) -> List[Task]:
        """List tasks with optional status filtering"""
        start_time = datetime.now()

        try:
            tasks = list(self.tasks.values())

            if status_filter:
                if status_filter.lower() == "completed":
                    tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
                elif status_filter.lower() == "pending":
                    tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
                # If filter is "all" or any other value, return all tasks

            # Performance logging
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(f"Tasks listed successfully", extra={
                "task_count": len(tasks),
                "filter": status_filter,
                "duration_ms": duration
            })

            if duration > self.config.list_with_filters_timeout_ms:
                self.logger.warning(f"List tasks operation took longer than expected", extra={
                    "duration_ms": duration,
                    "threshold_ms": self.config.list_with_filters_timeout_ms,
                    "task_count": len(tasks)
                })

            return tasks

        except Exception as e:
            error_info = handle_error(e, "list_tasks")
            raise ValidationError(f"Failed to list tasks: {error_info.get('message', str(e))}")

    def update_task(self, task_id: str, title: Optional[str] = None, description: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
        """Update an existing task"""
        start_time = datetime.now()

        try:
            if task_id not in self.tasks:
                raise TaskNotFoundError(task_id)

            task = self.tasks[task_id]

            # Validate new values if provided
            if title is not None:
                if not title or len(title.strip()) == 0:
                    raise ValidationError("Task title cannot be empty")
                if len(title) > self.config.max_title_length:
                    raise ValidationError(f"Task title exceeds maximum length of {self.config.max_title_length} characters")
                task.title = title.strip()

            if description is not None:
                if len(description) > self.config.max_description_length:
                    raise ValidationError(f"Task description exceeds maximum length of {self.config.max_description_length} characters")
                task.description = description

            if tags is not None:
                if len(tags) > self.config.max_tags_per_task:
                    raise ValidationError(f"Maximum of {self.config.max_tags_per_task} tags per task allowed")
                for tag in tags:
                    if not self._is_valid_tag(tag):
                        raise ValidationError(f"Invalid tag format: {tag}. Tags must be alphanumeric with hyphens/underscores only.")
                task.tags = tags

            task.updated_at = datetime.now().isoformat()

            # Log the command for history and potential undo
            self._log_command("update_task", {
                "task_id": task_id,
                "title": title,
                "description": description,
                "tags": tags
            })

            # Performance logging
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(f"Task updated successfully", extra={
                "task_id": task_id,
                "duration_ms": duration
            })

            if duration > self.config.update_task_timeout_ms:
                self.logger.warning(f"Update task operation took longer than expected", extra={
                    "duration_ms": duration,
                    "threshold_ms": self.config.update_task_timeout_ms
                })

            return True

        except TaskNotFoundError as e:
            self.logger.error(f"Task not found in update_task: {str(e)}", extra={
                "task_id": task_id
            })
            raise
        except ValidationError as e:
            self.logger.error(f"Validation error in update_task: {str(e)}", extra={
                "task_id": task_id
            })
            raise
        except Exception as e:
            error_info = handle_error(e, "update_task")
            raise ValidationError(f"Failed to update task: {error_info.get('message', str(e))}")

    def delete_task(self, task_id: str) -> bool:
        """Delete a task from the application"""
        start_time = datetime.now()

        try:
            if task_id not in self.tasks:
                raise TaskNotFoundError(task_id)

            # Store the task data for potential undo
            task_data = asdict(self.tasks[task_id])

            del self.tasks[task_id]

            # Log the command for history and potential undo
            self._log_command("delete_task", {
                "task_id": task_id,
                "original_task_data": task_data
            })

            # Performance logging
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(f"Task deleted successfully", extra={
                "task_id": task_id,
                "duration_ms": duration
            })

            if duration > self.config.delete_task_timeout_ms:
                self.logger.warning(f"Delete task operation took longer than expected", extra={
                    "duration_ms": duration,
                    "threshold_ms": self.config.delete_task_timeout_ms
                })

            return True

        except TaskNotFoundError as e:
            self.logger.error(f"Task not found in delete_task: {str(e)}", extra={
                "task_id": task_id
            })
            raise
        except Exception as e:
            error_info = handle_error(e, "delete_task")
            raise ValidationError(f"Failed to delete task: {error_info.get('message', str(e))}")

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed"""
        start_time = datetime.now()

        try:
            if task_id not in self.tasks:
                raise TaskNotFoundError(task_id)

            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].updated_at = datetime.now().isoformat()

            # Log the command for history and potential undo
            self._log_command("complete_task", {
                "task_id": task_id
            })

            # Performance logging
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(f"Task completed successfully", extra={
                "task_id": task_id,
                "duration_ms": duration
            })

            if duration > self.config.complete_task_timeout_ms:
                self.logger.warning(f"Complete task operation took longer than expected", extra={
                    "duration_ms": duration,
                    "threshold_ms": self.config.complete_task_timeout_ms
                })

            return True

        except TaskNotFoundError as e:
            self.logger.error(f"Task not found in complete_task: {str(e)}", extra={
                "task_id": task_id
            })
            raise
        except Exception as e:
            error_info = handle_error(e, "complete_task")
            raise ValidationError(f"Failed to complete task: {error_info.get('message', str(e))}")

    def incomplete_task(self, task_id: str) -> bool:
        """Mark a task as incomplete"""
        start_time = datetime.now()

        try:
            if task_id not in self.tasks:
                raise TaskNotFoundError(task_id)

            self.tasks[task_id].status = TaskStatus.PENDING
            self.tasks[task_id].updated_at = datetime.now().isoformat()

            # Log the command for history and potential undo
            self._log_command("incomplete_task", {
                "task_id": task_id
            })

            # Performance logging
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(f"Task marked incomplete successfully", extra={
                "task_id": task_id,
                "duration_ms": duration
            })

            if duration > self.config.complete_task_timeout_ms:  # Using same timeout as complete
                self.logger.warning(f"Incomplete task operation took longer than expected", extra={
                    "duration_ms": duration,
                    "threshold_ms": self.config.complete_task_timeout_ms
                })

            return True

        except TaskNotFoundError as e:
            self.logger.error(f"Task not found in incomplete_task: {str(e)}", extra={
                "task_id": task_id
            })
            raise
        except Exception as e:
            error_info = handle_error(e, "incomplete_task")
            raise ValidationError(f"Failed to mark task as incomplete: {error_info.get('message', str(e))}")

    def _log_command(self, command_type: str, params: Dict[str, Any]):
        """Log command for history and potential undo functionality"""
        command_entry = {
            "id": str(uuid.uuid4()),
            "type": command_type,
            "params": params,
            "timestamp": datetime.now().isoformat()
        }
        self.command_history.append(command_entry)

    def get_session_summary(self) -> Dict[str, Any]:
        """Get session statistics for exit summary"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        commands_executed = len(self.command_history)

        return {
            "total_tasks_created": total_tasks,
            "completed_tasks_count": completed_tasks,
            "commands_executed": commands_executed,
            "session_duration": str(datetime.now() - self.session_start_time)
        }


def main():
    """Main entry point for the CLI Todo Application"""
    parser = argparse.ArgumentParser(description='CLI Todo Application')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode with JSON output')

    args = parser.parse_args()

    app = TodoApp()

    if args.test_mode:
        # Test mode - output JSON format for automation
        print(json.dumps({"status": "ready", "mode": "test"}))
        return

    print("CLI Todo Application - Phase I")
    print("Type 'help' for available commands or 'exit' to quit")

    while True:
        try:
            user_input = input("> ").strip()

            if user_input.lower() in ['exit', 'quit']:
                # Show session summary before exiting
                summary = app.get_session_summary()
                print("\nSession Summary:")
                print(f"  Total tasks: {summary['total_tasks_created']}")
                print(f"  Completed: {summary['completed_tasks_count']}")
                print(f"  Commands executed: {summary['commands_executed']}")
                print("Goodbye!")
                break

            elif user_input.lower() == 'help':
                print("Available commands:")
                print("  add <title> [description] - Add a new task")
                print("  list [completed|pending|all] - List tasks")
                print("  update <id> <title> [description] - Update a task")
                print("  delete <id> - Delete a task")
                print("  complete <id> - Mark task as complete")
                print("  incomplete <id> - Mark task as incomplete")
                print("  exit - Exit the application")

            elif user_input.startswith('add '):
                parts = user_input[4:].split(' ', 1)
                title = parts[0]
                description = parts[1] if len(parts) > 1 else None

                task_id = app.add_task(title, description)
                print(f"Task added with ID: {task_id}")

            elif user_input.startswith('list'):
                parts = user_input.split(' ')
                filter_status = parts[1] if len(parts) > 1 else None

                tasks = app.list_tasks(filter_status)

                if not tasks:
                    print("No tasks found.")
                else:
                    print(f"{'ID':<36} {'Title':<30} {'Status':<10}")
                    print("-" * 78)
                    for task in tasks:
                        status_str = "COMPLETED" if task.status == TaskStatus.COMPLETED else "PENDING"
                        print(f"{task.id:<36} {task.title[:30]:<30} {status_str:<10}")

            elif user_input.startswith('update '):
                parts = user_input[7:].split(' ', 2)
                if len(parts) >= 2:
                    task_id, title = parts[0], parts[1]
                    description = parts[2] if len(parts) > 2 else None

                    app.update_task(task_id, title, description)
                    print(f"Task {task_id} updated successfully")
                else:
                    print("Usage: update <id> <title> [description]")

            elif user_input.startswith('delete '):
                task_id = user_input[7:]
                app.delete_task(task_id)
                print(f"Task {task_id} deleted successfully")

            elif user_input.startswith('complete '):
                task_id = user_input[9:]
                app.complete_task(task_id)
                print(f"Task {task_id} marked as complete")

            elif user_input.startswith('incomplete '):
                task_id = user_input[11:]
                app.incomplete_task(task_id)
                print(f"Task {task_id} marked as incomplete")

            else:
                print(f"Unknown command: {user_input}. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\nReceived interrupt signal. Exiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()