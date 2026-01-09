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
from typing import List, Optional, Dict, Any

# Import configuration and logging infrastructure
from .config import get_config
from .logging_infrastructure import get_logger, handle_error, ValidationError, TaskNotFoundError

# Import domain model components
from .domain.entities import Task, TaskStatus
from .domain.events import (
    TaskCreatedEvent, TaskUpdatedEvent, TaskDeletedEvent,
    TaskCompletedEvent, TaskReopenedEvent, EventType, TaskEvent
)
from .domain.validation import DomainValidator

# Import repository components
from .repository.factory import RepositoryFactory
from .repository.interface import TaskRepository

# Import event sourcing components
from .events import EventStore, EventValidator, EventBus, EventPublisher, EventReplayService

# Import core operations
from .core_operations.core_task_operations import CoreTaskOperations, TaskConfirmation


class TodoApp:
    """Main CLI Todo Application class"""

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()
        self.repository: TaskRepository = RepositoryFactory.create_task_repository()
        self.command_history: List[Dict[str, Any]] = []

        # Initialize event sourcing components
        self.event_store = EventStore()
        self.event_bus = EventBus()
        self.event_publisher = EventPublisher(self.event_bus)
        self.event_validator = EventValidator()
        self.event_replay_service = EventReplayService(self.event_store)

        # Initialize core operations
        self.core_operations = CoreTaskOperations(
            repository=self.repository,
            event_store=self.event_store,
            event_publisher=self.event_publisher,
            event_validator=self.event_validator
        )

        self.session_start_time = datetime.now()

        self.logger.info("TodoApp initialized", extra={
            "max_title_length": self.config.max_title_length,
            "max_description_length": self.config.max_description_length,
            "pagination_threshold": self.config.pagination_threshold
        })

    def add_task(self, title: str, description: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
        """Add a new task to the application"""
        result = self.core_operations.add_task(title, description, tags)

        if result.success:
            # Log the command for history and potential undo
            self._log_command("add_task", {
                "title": title,
                "description": description,
                "tags": tags,
                "task_id": result.task_id
            })

            self.logger.info(f"Task added successfully", extra={
                "task_id": result.task_id,
                "title_length": len(title)
            })

            return result.task_id
        else:
            self.logger.error(f"Failed to add task: {result.message}", extra={
                "title_length": len(title) if title else 0,
                "has_description": description is not None
            })
            raise ValidationError(result.message)

    def list_tasks(self, status_filter: Optional[str] = None) -> List[Task]:
        """List tasks with optional status filtering"""
        result = self.core_operations.list_tasks(status_filter)

        if result.success:
            # Convert dict back to Task objects if needed
            tasks = []
            for task_data in result.task_data or []:
                # Create a temporary task object from the data
                # Note: In a real scenario, we'd want to deserialize properly
                task = Task(
                    id=task_data['id'],
                    title=task_data['title'],
                    description=task_data['description'],
                    created_at=task_data['created_at'],
                    updated_at=task_data['updated_at'],
                    status=TaskStatus(task_data['status']),
                    tags=task_data['tags']
                )
                tasks.append(task)

            self.logger.info(f"Tasks listed successfully", extra={
                "task_count": len(tasks),
                "filter": status_filter
            })

            return tasks
        else:
            self.logger.error(f"Failed to list tasks: {result.message}")
            raise ValidationError(result.message)

    def update_task(self, task_id: str, title: Optional[str] = None, description: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
        """Update an existing task"""
        result = self.core_operations.update_task(task_id, title, description, tags)

        if result.success:
            # Log the command for history and potential undo
            self._log_command("update_task", {
                "task_id": task_id,
                "title": title,
                "description": description,
                "tags": tags
            })

            self.logger.info(f"Task updated successfully", extra={
                "task_id": task_id
            })

            return True
        else:
            self.logger.error(f"Failed to update task: {result.message}", extra={
                "task_id": task_id
            })
            raise ValidationError(result.message)

    def delete_task(self, task_id: str) -> bool:
        """Delete a task from the application"""
        result = self.core_operations.delete_task(task_id)

        if result.success:
            # Log the command for history and potential undo
            self._log_command("delete_task", {
                "task_id": task_id,
                "original_task_data": result.task_data
            })

            self.logger.info(f"Task deleted successfully", extra={
                "task_id": task_id
            })

            return True
        else:
            self.logger.error(f"Failed to delete task: {result.message}", extra={
                "task_id": task_id
            })
            raise ValidationError(result.message)

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed"""
        result = self.core_operations.complete_task(task_id)

        if result.success:
            # Log the command for history and potential undo
            self._log_command("complete_task", {
                "task_id": task_id
            })

            self.logger.info(f"Task completed successfully", extra={
                "task_id": task_id
            })

            return True
        else:
            self.logger.error(f"Failed to complete task: {result.message}", extra={
                "task_id": task_id
            })
            raise ValidationError(result.message)

    def incomplete_task(self, task_id: str) -> bool:
        """Mark a task as incomplete"""
        result = self.core_operations.incomplete_task(task_id)

        if result.success:
            # Log the command for history and potential undo
            self._log_command("incomplete_task", {
                "task_id": task_id
            })

            self.logger.info(f"Task marked incomplete successfully", extra={
                "task_id": task_id
            })

            return True
        else:
            self.logger.error(f"Failed to mark task as incomplete: {result.message}", extra={
                "task_id": task_id
            })
            raise ValidationError(result.message)

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
        # Use the event store to get accurate task counts from events
        all_events = self.event_store.get_events()

        # Count tasks based on events
        created_tasks = len([e for e in all_events if e.type == EventType.TASK_CREATED])
        deleted_tasks = len([e for e in all_events if e.type == EventType.TASK_DELETED])
        completed_tasks = len([e for e in all_events if e.type == EventType.TASK_COMPLETED])

        # Calculate net tasks (created - deleted)
        net_tasks = created_tasks - deleted_tasks
        commands_executed = len(self.command_history)

        # Get memory usage stats from event store
        memory_stats = self.event_store.get_memory_usage_stats()

        return {
            "total_tasks_created": created_tasks,
            "net_tasks": net_tasks,
            "deleted_tasks_count": deleted_tasks,
            "completed_tasks_count": completed_tasks,
            "commands_executed": commands_executed,
            "total_events_stored": len(all_events),
            "event_store_memory_usage": memory_stats,
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