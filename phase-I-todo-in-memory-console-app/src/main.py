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
            # Use domain validator for validation
            DomainValidator.validate_task_title(title)
            if description:
                DomainValidator.validate_task_description(description)
            if tags:
                DomainValidator.validate_task_tags(tags)

            # Create task using domain factory method
            task = Task.create(title=title.strip(), description=description, tags=tags)

            # Create and validate the event before storing
            event = TaskCreatedEvent(task)

            # Validate the event before storing
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store the event in the event store
            self.event_store.append(event)

            # Publish the event via the event bus
            self.event_publisher.publish_event(event)

            # Store the task using repository
            self.repository.add(task)

            # Log the command for history and potential undo
            self._log_command("add_task", {
                "title": title,
                "description": description,
                "tags": tags,
                "task_id": task.id
            })

            # Performance logging
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(f"Task added successfully", extra={
                "task_id": task.id,
                "duration_ms": duration,
                "title_length": len(title)
            })

            if duration > self.config.add_task_timeout_ms:
                self.logger.warning(f"Add task operation took longer than expected", extra={
                    "duration_ms": duration,
                    "threshold_ms": self.config.add_task_timeout_ms
                })

            return task.id

        except ValueError as e:  # Domain validation raises ValueError
            self.logger.error(f"Validation error in add_task: {str(e)}", extra={
                "title_length": len(title) if title else 0,
                "has_description": description is not None
            })
            raise ValidationError(str(e))
        except ValidationError:
            # Re-raise ValidationError as-is
            raise
        except Exception as e:
            error_info = handle_error(e, "add_task")
            raise ValidationError(f"Failed to add task: {error_info.get('message', str(e))}")


    def list_tasks(self, status_filter: Optional[str] = None) -> List[Task]:
        """List tasks with optional status filtering"""
        start_time = datetime.now()

        try:
            if status_filter:
                if status_filter.lower() == "completed":
                    tasks = self.repository.list_by_status(TaskStatus.COMPLETED)
                elif status_filter.lower() == "pending":
                    tasks = self.repository.list_by_status(TaskStatus.PENDING)
                else:
                    # If filter is "all" or any other value, return all tasks
                    tasks = self.repository.list_all()
            else:
                # No filter - return all tasks
                tasks = self.repository.list_all()

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
            # Get the task from the repository
            task = self.repository.get(task_id)
            if task is None:
                raise TaskNotFoundError(task_id)

            # Store old values for the event
            old_values = {
                'title': task.title,
                'description': task.description,
                'status': task.status.value,
                'tags': task.tags.copy() if task.tags else []
            }

            # Use domain validation for update parameters
            DomainValidator.validate_task_update(title, description, tags)

            # Perform the update using the domain method
            task.update(title=title, description=description, tags=tags)

            # Create and validate the event before storing
            event = TaskUpdatedEvent(task, old_values)

            # Validate the event before storing
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store the event in the event store
            self.event_store.append(event)

            # Publish the event via the event bus
            self.event_publisher.publish_event(event)

            # Update the task in the repository
            success = self.repository.update(task)
            if not success:
                raise TaskNotFoundError(task_id)

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

        except ValueError as e:  # Domain validation raises ValueError
            self.logger.error(f"Validation error in update_task: {str(e)}", extra={
                "task_id": task_id
            })
            raise ValidationError(str(e))
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
            # Get the task from the repository to create the event
            task_to_delete = self.repository.get(task_id)
            if task_to_delete is None:
                raise TaskNotFoundError(task_id)

            # Create and validate the event before storing
            event = TaskDeletedEvent(task_to_delete)

            # Validate the event before storing
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store the event in the event store
            self.event_store.append(event)

            # Publish the event via the event bus
            self.event_publisher.publish_event(event)

            # Remove the task from the repository
            success = self.repository.delete(task_id)
            if not success:
                raise TaskNotFoundError(task_id)

            # Log the command for history and potential undo
            self._log_command("delete_task", {
                "task_id": task_id,
                "original_task_data": task_to_delete.to_dict()
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
            # Get the task from the repository
            task = self.repository.get(task_id)
            if task is None:
                raise TaskNotFoundError(task_id)

            # Store the previous status for the event
            previous_status = task.status.value

            # Use domain method to mark as completed
            task.mark_completed()

            # Create and validate the event before storing
            event = TaskCompletedEvent(task, previous_status=previous_status)

            # Validate the event before storing
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store the event in the event store
            self.event_store.append(event)

            # Publish the event via the event bus
            self.event_publisher.publish_event(event)

            # Update the task in the repository
            success = self.repository.update(task)
            if not success:
                raise TaskNotFoundError(task_id)

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
            # Get the task from the repository
            task = self.repository.get(task_id)
            if task is None:
                raise TaskNotFoundError(task_id)

            # Store the previous status for the event
            previous_status = task.status.value

            # Use domain method to mark as pending
            task.mark_pending()

            # Create and validate the event before storing
            event = TaskReopenedEvent(task, previous_status=previous_status)

            # Validate the event before storing
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store the event in the event store
            self.event_store.append(event)

            # Publish the event via the event bus
            self.event_publisher.publish_event(event)

            # Update the task in the repository
            success = self.repository.update(task)
            if not success:
                raise TaskNotFoundError(task_id)

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