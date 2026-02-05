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

# Import plugin architecture
from .plugin_architecture import PluginLoader, PluginValidator


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

        # Initialize plugin architecture
        self.plugin_loader = PluginLoader()
        self.plugin_validator = PluginValidator()

        # Load and validate plugins
        try:
            loaded_plugins = self.plugin_loader.load_all_plugins()
            self.logger.info(f"Loaded {len(loaded_plugins)} plugins successfully")

            # Check for failed plugins
            failed_plugins = self.plugin_loader.get_failed_plugins()
            if failed_plugins:
                self.logger.warning(f"Failed to load {len(failed_plugins)} plugins")
                for plugin_info in failed_plugins:
                    self.logger.warning(f"Failed plugin: {plugin_info.name} - {plugin_info.error_message}")
        except Exception as e:
            self.logger.error(f"Error initializing plugin system: {str(e)}")

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

        # Include plugin information in session summary
        loaded_plugins_count = len(self.plugin_loader.get_loaded_plugins())
        failed_plugins_count = len(self.plugin_loader.get_failed_plugins())

        return {
            "total_tasks_created": created_tasks,
            "net_tasks": net_tasks,
            "deleted_tasks_count": deleted_tasks,
            "completed_tasks_count": completed_tasks,
            "commands_executed": commands_executed,
            "total_events_stored": len(all_events),
            "event_store_memory_usage": memory_stats,
            "loaded_plugins_count": loaded_plugins_count,
            "failed_plugins_count": failed_plugins_count,
            "session_duration": str(datetime.now() - self.session_start_time)
        }

    def get_plugins(self):
        """Get all loaded plugins"""
        return self.plugin_loader.get_loaded_plugins()

    def get_plugin_info(self):
        """Get information about all plugins (both loaded and failed)"""
        return {
            "loaded_plugins": self.plugin_loader.get_loaded_plugins(),
            "failed_plugins": self.plugin_loader.get_failed_plugins()
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

    print("\n" + "="*50)
    print("CLI Todo Application - Phase I")
    print("="*50)
    print("\nChoose interface mode:")
    print("1. Command-based (type commands directly)")
    print("2. Menu-based (select options from numbered menu)")
    print("Type '1' or '2', or press Enter for command-based (default)\n")

    mode_choice = input("> ").strip().lower()

    if mode_choice == '2':
        # Menu-based interface
        menu_based_interface(app)
    else:
        # Command-based interface (default)
        command_based_interface(app)


def menu_based_interface(app):
    """Menu-based interface for the CLI Todo Application"""
    while True:
        try:
            print("\n" + "-"*25)
            print("         MENU")
            print("-"*25)
            print("1. Add Task")
            print("2. List Tasks")
            print("3. Update Task")
            print("4. Delete Task")
            print("5. Complete Task")
            print("6. Mark Task Incomplete")
            print("7. Help")
            print("8. Exit")
            print("-"*25)

            choice = input("Select option (1-8): ").strip()

            if choice == '1':
                title = input("Enter task title: ").strip()
                if title:
                    description_input = input("Enter description (optional, press Enter to skip): ").strip()
                    description = description_input if description_input else None

                    task_id = app.add_task(title, description)
                    print(f"Task added with ID: {task_id}")
                else:
                    print("Title cannot be empty.")

            elif choice == '2':
                print("Filter options: 1. All, 2. Pending, 3. Completed (press Enter for All)")
                filter_choice = input("Select filter: ").strip()

                filter_map = {'1': None, '2': 'pending', '3': 'completed'}
                filter_status = filter_map.get(filter_choice, None)

                tasks = app.list_tasks(filter_status)

                if not tasks:
                    print("No tasks found.\n")
                else:
                    print("\n" + "-" * 58)
                    print(f"{'#':<3} {'Title':<40} {'Status':<10}")
                    print("-" * 58)
                    for i, task in enumerate(tasks, 1):
                        status_str = "COMPLETED" if task.status == TaskStatus.COMPLETED else "PENDING"
                        print(f"{i:<3} {task.title[:40]:<40} {status_str:<10}")
                    print("-" * 58)
                    print(f"Total: {len(tasks)} tasks\n")

            elif choice == '3':
                tasks = app.list_tasks()
                if not tasks:
                    print("No tasks available to update.")
                    continue

                print(f"{'#':<3} {'Title':<40} {'Status':<10}")
                print("-" * 58)
                for i, task in enumerate(tasks, 1):
                    status_str = "COMPLETED" if task.status == TaskStatus.COMPLETED else "PENDING"
                    print(f"{i:<3} {task.title[:40]:<40} {status_str:<10}")

                task_num = input("Enter task number to update: ").strip()
                if task_num.isdigit():
                    index = int(task_num) - 1
                    if 0 <= index < len(tasks):
                        task = tasks[index]

                        new_title = input(f"Enter new title (current: {task.title}): ").strip()
                        new_title = new_title if new_title else task.title

                        new_desc = input(f"Enter new description (current: {task.description or 'None'}): ").strip()
                        new_desc = new_desc if new_desc else task.description

                        app.update_task(task.id, new_title, new_desc)
                        print("Task updated successfully")
                    else:
                        print("Invalid task number.")
                else:
                    print("Invalid input. Please enter a number.")

            elif choice == '4':
                tasks = app.list_tasks()
                if not tasks:
                    print("No tasks available to delete.")
                    continue

                print(f"{'#':<3} {'Title':<40} {'Status':<10}")
                print("-" * 58)
                for i, task in enumerate(tasks, 1):
                    status_str = "COMPLETED" if task.status == TaskStatus.COMPLETED else "PENDING"
                    print(f"{i:<3} {task.title[:40]:<40} {status_str:<10}")

                task_num = input("Enter task number to delete: ").strip()
                if task_num.isdigit():
                    index = int(task_num) - 1
                    if 0 <= index < len(tasks):
                        task = tasks[index]
                        confirm = input(f"Are you sure you want to delete '{task.title}'? (y/N): ").strip().lower()
                        if confirm in ['y', 'yes']:
                            app.delete_task(task.id)
                            print("Task deleted successfully")
                        else:
                            print("Deletion cancelled.")
                    else:
                        print("Invalid task number.")
                else:
                    print("Invalid input. Please enter a number.")

            elif choice == '5':
                tasks = app.list_tasks()
                pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
                if not pending_tasks:
                    print("No pending tasks to complete.")
                    continue

                print(f"{'#':<3} {'Title':<40} {'Status':<10}")
                print("-" * 58)
                for i, task in enumerate(pending_tasks, 1):
                    print(f"{i:<3} {task.title[:40]:<40} {'PENDING':<10}")

                task_num = input("Enter task number to complete: ").strip()
                if task_num.isdigit():
                    index = int(task_num) - 1
                    if 0 <= index < len(pending_tasks):
                        task = pending_tasks[index]
                        app.complete_task(task.id)
                        print("Task marked as complete")
                    else:
                        print("Invalid task number.")
                else:
                    print("Invalid input. Please enter a number.")

            elif choice == '6':
                tasks = app.list_tasks()
                completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
                if not completed_tasks:
                    print("No completed tasks to mark incomplete.")
                    continue

                print(f"{'#':<3} {'Title':<40} {'Status':<10}")
                print("-" * 58)
                for i, task in enumerate(completed_tasks, 1):
                    print(f"{i:<3} {task.title[:40]:<40} {'COMPLETED':<10}")

                task_num = input("Enter task number to mark incomplete: ").strip()
                if task_num.isdigit():
                    index = int(task_num) - 1
                    if 0 <= index < len(completed_tasks):
                        task = completed_tasks[index]
                        app.incomplete_task(task.id)
                        print("Task marked as incomplete")
                    else:
                        print("Invalid task number.")
                else:
                    print("Invalid input. Please enter a number.")

            elif choice == '7':
                print("\n" + "="*50)
                print("Help Information:")
                print("1. Add Task - Add a new task with title and optional description")
                print("2. List Tasks - Display all tasks with their status")
                print("3. Update Task - Modify an existing task's title or description")
                print("4. Delete Task - Remove a task from the list")
                print("5. Complete Task - Mark a pending task as completed")
                print("6. Mark Task Incomplete - Reopen a completed task")
                print("7. Help - Show this help information")
                print("8. Exit - Close the application")
                print("="*50)

            elif choice == '8':
                # Show session summary before exiting
                summary = app.get_session_summary()
                print("\n" + "="*30)
                print("Session Summary:")
                print(f"  Total tasks: {summary['total_tasks_created']}")
                print(f"  Completed: {summary['completed_tasks_count']}")
                print(f"  Commands executed: {summary['commands_executed']}")
                print("="*30)
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please select a number between 1-8.")

        except KeyboardInterrupt:
            print("\nReceived interrupt signal. Exiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def command_based_interface(app):
    """Command-based interface for the CLI Todo Application"""
    print("\n" + "="*40)
    print("Command-based mode activated")
    print("Type 'help' for available commands or 'exit' to quit")
    print("="*40)

    while True:
        try:
            user_input = input("> ").strip()

            if user_input.lower() in ['exit', 'quit']:
                # Show session summary before exiting
                summary = app.get_session_summary()
                print("\n" + "="*30)
                print("Session Summary:")
                print(f"  Total tasks: {summary['total_tasks_created']}")
                print(f"  Completed: {summary['completed_tasks_count']}")
                print(f"  Commands executed: {summary['commands_executed']}")
                print("="*30)
                print("Goodbye!")
                break

            elif user_input.lower() == 'help':
                print("\n" + "="*60)
                print("Available commands:")
                print("  add <title> [ | description] - Add a new task (use ' | ' to separate title and description)")
                print("  list [completed|pending|all] - List tasks with numbering")
                print("  update <number_or_id> <new_title> [ | new_description] - Update a task by number or ID")
                print("  delete <number_or_id> - Delete a task by number or ID")
                print("  complete <number_or_id> - Mark task as complete by number or ID")
                print("  incomplete <number_or_id> - Mark task as incomplete by number or ID")
                print("  exit - Exit the application")
                print("-"*60)
                print("Examples:")
                print("  add Buy groceries")
                print("  add Buy groceries | Need to buy milk, bread, eggs")
                print("  list")
                print("  update 1 New task title | Updated description")
                print("  delete 1")
                print("="*60)

            elif user_input.startswith('add '):
                # Improved parsing: treat everything after 'add ' as the title, and allow description after a delimiter
                content = user_input[4:].strip()

                # Split by special delimiter (e.g., ' | ') for title/description
                if ' | ' in content:
                    title, description = content.split(' | ', 1)
                else:
                    title = content
                    description = None

                task_id = app.add_task(title, description)
                print(f"Task added with ID: {task_id}")

            elif user_input.startswith('list'):
                parts = user_input.split(' ', 1)
                filter_status = parts[1] if len(parts) > 1 else None

                tasks = app.list_tasks(filter_status)

                if not tasks:
                    print("No tasks found.\n")
                else:
                    print("\n" + "-" * 58)
                    print(f"{'#':<3} {'Title':<40} {'Status':<10}")
                    print("-" * 58)
                    for i, task in enumerate(tasks, 1):
                        status_str = "COMPLETED" if task.status == TaskStatus.COMPLETED else "PENDING"
                        print(f"{i:<3} {task.title[:40]:<40} {status_str:<10}")
                    print("-" * 58)
                    print(f"Total: {len(tasks)} tasks\n")

            elif user_input.startswith('update '):
                # Allow updating by number or by ID
                parts = user_input[7:].split(' ', 1)
                if len(parts) < 1:
                    print("Usage: update <task_number_or_id> [new_title | new_title | new_description]")
                    continue

                identifier = parts[0]
                new_content = parts[1] if len(parts) > 1 else ""

                # Check if the identifier is a number (list index)
                if identifier.isdigit():
                    tasks = app.list_tasks()
                    index = int(identifier) - 1
                    if 0 <= index < len(tasks):
                        task = tasks[index]
                        task_id = task.id
                    else:
                        print(f"Invalid task number: {identifier}")
                        continue
                else:
                    # Assume it's a task ID
                    task_id = identifier

                # Parse new content for title/description
                if ' | ' in new_content:
                    new_title, new_description = new_content.split(' | ', 1)
                elif new_content:
                    new_title = new_content
                    new_description = None
                else:
                    print("Please provide new title for the task")
                    continue

                app.update_task(task_id, new_title, new_description)
                print(f"Task updated successfully")

            elif user_input.startswith('delete '):
                identifier = user_input[7:].strip()

                # Check if the identifier is a number (list index)
                if identifier.isdigit():
                    tasks = app.list_tasks()
                    index = int(identifier) - 1
                    if 0 <= index < len(tasks):
                        task = tasks[index]
                        task_id = task.id
                    else:
                        print(f"Invalid task number: {identifier}")
                        continue
                else:
                    # Assume it's a task ID
                    task_id = identifier

                app.delete_task(task_id)
                print(f"Task deleted successfully")

            elif user_input.startswith('complete '):
                identifier = user_input[9:].strip()

                # Check if the identifier is a number (list index)
                if identifier.isdigit():
                    tasks = app.list_tasks()
                    index = int(identifier) - 1
                    if 0 <= index < len(tasks):
                        task = tasks[index]
                        task_id = task.id
                    else:
                        print(f"Invalid task number: {identifier}")
                        continue
                else:
                    # Assume it's a task ID
                    task_id = identifier

                app.complete_task(task_id)
                print(f"Task marked as complete")

            elif user_input.startswith('incomplete '):
                identifier = user_input[11:].strip()

                # Check if the identifier is a number (list index)
                if identifier.isdigit():
                    tasks = app.list_tasks()
                    index = int(identifier) - 1
                    if 0 <= index < len(tasks):
                        task = tasks[index]
                        task_id = task.id
                    else:
                        print(f"Invalid task number: {identifier}")
                        continue
                else:
                    # Assume it's a task ID
                    task_id = identifier

                app.incomplete_task(task_id)
                print(f"Task marked as incomplete")

            else:
                print(f"Unknown command: {user_input}. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\nReceived interrupt signal. Exiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()