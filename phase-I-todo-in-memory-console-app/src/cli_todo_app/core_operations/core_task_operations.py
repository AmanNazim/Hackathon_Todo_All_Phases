"""
Core Task Operations for CLI Todo Application
Implements T180-T186: Core Task Operations functionality
"""
import uuid
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# Import required domain models
from ..domain.entities import Task, TaskStatus
from ..domain.events import (
    TaskCreatedEvent, TaskUpdatedEvent, TaskDeletedEvent,
    TaskCompletedEvent, TaskReopenedEvent
)
from ..domain.validation import DomainValidator
from ..repository.interface import TaskRepository
from ..events import EventStore, EventValidator, EventPublisher


@dataclass
class TaskConfirmation:
    """Task confirmation message structure"""
    success: bool
    message: str
    task_id: Optional[str] = None
    task_data: Optional[Dict[str, Any]] = None


class CoreTaskOperations:
    """
    Core Task Operations implementation that provides the five core functions
    (add, view, update, delete, complete) with all required functionality
    """

    def __init__(self, repository: TaskRepository, event_store: EventStore,
                 event_publisher: EventPublisher, event_validator: EventValidator):
        self.repository = repository
        self.event_store = event_store
        self.event_publisher = event_publisher
        self.event_validator = event_validator

    def add_task(self, title: str, description: Optional[str] = None,
                 tags: Optional[List[str]] = None) -> TaskConfirmation:
        """
        Implement Add Task functionality with title validation (T180)
        """
        start_time = datetime.now()

        try:
            # Validate inputs according to specification
            DomainValidator.validate_task_title(title)
            if description:
                DomainValidator.validate_task_description(description)
            if tags:
                DomainValidator.validate_task_tags(tags)

            # Create task with domain factory method
            task = Task.create(title=title.strip(), description=description, tags=tags)

            # Create and validate event
            event = TaskCreatedEvent(task)
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store event and publish
            self.event_store.append(event)
            self.event_publisher.publish_event(event)

            # Store task in repository
            self.repository.add(task)

            # Calculate duration and validate performance
            duration = (datetime.now() - start_time).total_seconds() * 1000

            # Create confirmation message
            confirmation_msg = f"Task added successfully with ID: {task.id}"
            if duration > 100:  # Performance threshold from spec
                confirmation_msg += f" (Warning: Operation took {duration:.2f}ms)"

            return TaskConfirmation(
                success=True,
                message=confirmation_msg,
                task_id=task.id,
                task_data=task.to_dict()
            )

        except ValueError as e:
            error_msg = f"Validation error in add_task: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)
        except Exception as e:
            error_msg = f"Failed to add task: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)

    def list_tasks(self, status_filter: Optional[str] = None) -> TaskConfirmation:
        """
        Implement View/List Tasks functionality with status indicators (T181)
        """
        start_time = datetime.now()

        try:
            # Get tasks based on filter
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

            # Calculate duration and validate performance
            duration = (datetime.now() - start_time).total_seconds() * 1000

            # Prepare confirmation message
            if not tasks:
                message = "No tasks found."
            else:
                message = f"Found {len(tasks)} task(s)."

            # Performance check
            if len(tasks) <= 1000 and duration > 200:  # Performance threshold from spec
                message += f" (Warning: Operation took {duration:.2f}ms for {len(tasks)} tasks)"
            elif len(tasks) > 1000 and duration > 500:  # Higher threshold for large datasets
                message += f" (Warning: Operation took {duration:.2f}ms for {len(tasks)} tasks)"

            # Return task data for rendering
            task_data = [task.to_dict() for task in tasks]

            return TaskConfirmation(
                success=True,
                message=message,
                task_data=task_data
            )

        except Exception as e:
            error_msg = f"Failed to list tasks: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)

    def update_task(self, task_id: str, title: Optional[str] = None,
                    description: Optional[str] = None, tags: Optional[List[str]] = None) -> TaskConfirmation:
        """
        Implement Update Task functionality preserving unchanged fields (T182)
        """
        start_time = datetime.now()

        try:
            # Get existing task
            existing_task = self.repository.get(task_id)
            if not existing_task:
                return TaskConfirmation(
                    success=False,
                    message=f"Task with ID {task_id} not found"
                )

            # Store old values for event
            old_values = {
                'title': existing_task.title,
                'description': existing_task.description,
                'status': existing_task.status.value,
                'tags': existing_task.tags.copy() if existing_task.tags else []
            }

            # Validate update parameters
            DomainValidator.validate_task_update(title, description, tags)

            # Perform update while preserving unchanged fields
            existing_task.update(
                title=title,
                description=description,
                tags=tags
            )
            updated_task = existing_task

            # Create and validate event
            event = TaskUpdatedEvent(updated_task, old_values)
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store event and publish
            self.event_store.append(event)
            self.event_publisher.publish_event(event)

            # Update task in repository
            success = self.repository.update(updated_task)
            if not success:
                return TaskConfirmation(
                    success=False,
                    message=f"Failed to update task with ID {task_id}"
                )

            # Calculate duration and validate performance
            duration = (datetime.now() - start_time).total_seconds() * 1000

            # Performance check
            if duration > 100:  # Performance threshold from spec
                message = f"Task {task_id} updated successfully (Warning: Operation took {duration:.2f}ms)"
            else:
                message = f"Task {task_id} updated successfully"

            return TaskConfirmation(
                success=True,
                message=message,
                task_id=task_id,
                task_data=updated_task.to_dict()
            )

        except ValueError as e:
            error_msg = f"Validation error in update_task: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)
        except Exception as e:
            error_msg = f"Failed to update task: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)

    def delete_task(self, task_id: str) -> TaskConfirmation:
        """
        Implement Delete Task functionality with ID validation (T183)
        """
        start_time = datetime.now()

        try:
            # Validate that task exists before deletion
            task_to_delete = self.repository.get(task_id)
            if not task_to_delete:
                return TaskConfirmation(
                    success=False,
                    message=f"Task with ID {task_id} not found"
                )

            # Create and validate event
            event = TaskDeletedEvent(task_to_delete)
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store event and publish
            self.event_store.append(event)
            self.event_publisher.publish_event(event)

            # Delete task from repository
            success = self.repository.delete(task_id)
            if not success:
                return TaskConfirmation(
                    success=False,
                    message=f"Failed to delete task with ID {task_id}"
                )

            # Calculate duration and validate performance
            duration = (datetime.now() - start_time).total_seconds() * 1000

            # Performance check
            if duration > 100:  # Performance threshold from spec
                message = f"Task {task_id} deleted successfully (Warning: Operation took {duration:.2f}ms)"
            else:
                message = f"Task {task_id} deleted successfully"

            return TaskConfirmation(
                success=True,
                message=message,
                task_id=task_id
            )

        except Exception as e:
            error_msg = f"Failed to delete task: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)

    def complete_task(self, task_id: str) -> TaskConfirmation:
        """
        Implement Mark Task Complete functionality (T184)
        """
        start_time = datetime.now()

        try:
            # Validate that task exists
            task = self.repository.get(task_id)
            if not task:
                return TaskConfirmation(
                    success=False,
                    message=f"Task with ID {task_id} not found"
                )

            # Store previous status for event
            previous_status = task.status.value

            # Update task status to completed
            task.mark_completed()

            # Create and validate event
            event = TaskCompletedEvent(task, previous_status=previous_status)
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store event and publish
            self.event_store.append(event)
            self.event_publisher.publish_event(event)

            # Update task in repository
            success = self.repository.update(task)
            if not success:
                return TaskConfirmation(
                    success=False,
                    message=f"Failed to complete task with ID {task_id}"
                )

            # Calculate duration and validate performance
            duration = (datetime.now() - start_time).total_seconds() * 1000

            # Performance check
            if duration > 100:  # Performance threshold from spec
                message = f"Task {task_id} marked as complete (Warning: Operation took {duration:.2f}ms)"
            else:
                message = f"Task {task_id} marked as complete"

            return TaskConfirmation(
                success=True,
                message=message,
                task_id=task_id,
                task_data=task.to_dict()
            )

        except Exception as e:
            error_msg = f"Failed to complete task: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)

    def incomplete_task(self, task_id: str) -> TaskConfirmation:
        """
        Implement Mark Task Incomplete functionality (T184)
        """
        start_time = datetime.now()

        try:
            # Validate that task exists
            task = self.repository.get(task_id)
            if not task:
                return TaskConfirmation(
                    success=False,
                    message=f"Task with ID {task_id} not found"
                )

            # Store previous status for event
            previous_status = task.status.value

            # Update task status to pending
            task.mark_pending()

            # Create and validate event
            event = TaskReopenedEvent(task, previous_status=previous_status)
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store event and publish
            self.event_store.append(event)
            self.event_publisher.publish_event(event)

            # Update task in repository
            success = self.repository.update(task)
            if not success:
                return TaskConfirmation(
                    success=False,
                    message=f"Failed to mark task {task_id} as incomplete"
                )

            # Calculate duration and validate performance
            duration = (datetime.now() - start_time).total_seconds() * 1000

            # Performance check
            if duration > 100:  # Performance threshold from spec
                message = f"Task {task_id} marked as incomplete (Warning: Operation took {duration:.2f}ms)"
            else:
                message = f"Task {task_id} marked as incomplete"

            return TaskConfirmation(
                success=True,
                message=message,
                task_id=task_id,
                task_data=task.to_dict()
            )

        except Exception as e:
            error_msg = f"Failed to mark task as incomplete: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)

    def add_tags_to_task(self, task_id: str, tags: List[str]) -> TaskConfirmation:
        """
        Implement tags attachment to tasks functionality (T186)
        """
        try:
            # Validate tags format
            DomainValidator.validate_task_tags(tags)

            # Get existing task
            existing_task = self.repository.get(task_id)
            if not existing_task:
                return TaskConfirmation(
                    success=False,
                    message=f"Task with ID {task_id} not found"
                )

            # Store old values for event
            old_values = {
                'title': existing_task.title,
                'description': existing_task.description,
                'status': existing_task.status.value,
                'tags': existing_task.tags.copy() if existing_task.tags else []
            }

            # Add new tags to existing tags (union)
            current_tags = existing_task.tags or []
            new_tags = list(set(current_tags + tags))  # Remove duplicates

            # Update task with new tags - update() modifies the task in-place, doesn't return anything
            existing_task.update(tags=new_tags)
            updated_task = existing_task

            # Create and validate event
            event = TaskUpdatedEvent(updated_task, old_values)
            self.event_validator.validate_event(event)
            self.event_validator.validate_event_signature(event)

            # Store event and publish
            self.event_store.append(event)
            self.event_publisher.publish_event(event)

            # Update task in repository
            success = self.repository.update(updated_task)
            if not success:
                return TaskConfirmation(
                    success=False,
                    message=f"Failed to update task with ID {task_id}"
                )

            return TaskConfirmation(
                success=True,
                message=f"Tags added to task {task_id}",
                task_id=task_id,
                task_data=updated_task.to_dict()
            )

        except ValueError as e:
            error_msg = f"Validation error in add_tags_to_task: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)
        except Exception as e:
            error_msg = f"Failed to add tags to task: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)

    def get_task_by_id(self, task_id: str) -> TaskConfirmation:
        """
        Helper method to get a task by ID
        """
        try:
            task = self.repository.get(task_id)
            if not task:
                return TaskConfirmation(
                    success=False,
                    message=f"Task with ID {task_id} not found"
                )

            return TaskConfirmation(
                success=True,
                message="Task retrieved successfully",
                task_id=task_id,
                task_data=task.to_dict()
            )
        except Exception as e:
            error_msg = f"Failed to retrieve task: {str(e)}"
            return TaskConfirmation(success=False, message=error_msg)

    def confirm_operation(self, operation_type: str, result: TaskConfirmation) -> str:
        """
        Add task confirmation for successful operations (T185)
        """
        if result.success:
            # Return success confirmation message
            return result.message
        else:
            # Return error message
            return f"Error: {result.message}"