"""
Reusable validation utilities for task validation systems.

This module provides common validation functions that can be used across
different components of a task management system.
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a single validation error"""
    code: str
    message: str
    field: str
    severity: str = "error"
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


def validate_title_length(title: str, min_length: int = 1, max_length: int = 200) -> Optional[ValidationError]:
    """Validate title length requirements"""
    if not title:
        return ValidationError(
            code="TITLE_REQUIRED",
            message="Task title cannot be empty",
            field="title"
        )

    if len(title) > max_length:
        return ValidationError(
            code="TITLE_TOO_LONG",
            message=f"Task title exceeds maximum length of {max_length} characters",
            field="title"
        )

    if len(title.strip()) == 0:
        return ValidationError(
            code="TITLE_WHITESPACE_ONLY",
            message="Task title cannot contain only whitespace",
            field="title"
        )

    if len(title) < min_length:
        return ValidationError(
            code="TITLE_TOO_SHORT",
            message=f"Task title must be at least {min_length} characters",
            field="title"
        )

    return None


def validate_task_id(task_id: Any) -> Optional[ValidationError]:
    """Validate task ID format and value"""
    if task_id is None:
        return ValidationError(
            code="TASK_ID_REQUIRED",
            message="Task ID is required",
            field="id"
        )

    if isinstance(task_id, str):
        if not task_id.strip():
            return ValidationError(
                code="TASK_ID_INVALID",
                message="Task ID cannot be empty",
                field="id"
            )
        # Check if string ID is a valid identifier (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', task_id):
            return ValidationError(
                code="TASK_ID_INVALID_FORMAT",
                message="Task ID contains invalid characters",
                field="id"
            )
    elif isinstance(task_id, int):
        if task_id <= 0:
            return ValidationError(
                code="TASK_ID_INVALID",
                message="Task ID must be a positive integer",
                field="id"
            )
    else:
        return ValidationError(
            code="TASK_ID_INVALID_TYPE",
            message="Task ID must be a string or integer",
            field="id"
        )

    return None


def validate_task_status(status: str) -> Optional[ValidationError]:
    """Validate task status value"""
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'archived']

    if status not in valid_statuses:
        return ValidationError(
            code="STATUS_INVALID",
            message=f"Task status must be one of: {', '.join(valid_statuses)}",
            field="status"
        )

    return None


def validate_datetime_string(date_string: str) -> Optional[ValidationError]:
    """Validate datetime string format"""
    try:
        # Try to parse common datetime formats
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return None
    except ValueError:
        return ValidationError(
            code="DATETIME_INVALID",
            message="Date string format is invalid",
            field="datetime"
        )


def validate_task_priority(priority: str) -> Optional[ValidationError]:
    """Validate task priority value"""
    valid_priorities = ['low', 'medium', 'high', 'critical']

    if priority not in valid_priorities:
        return ValidationError(
            code="PRIORITY_INVALID",
            message=f"Task priority must be one of: {', '.join(valid_priorities)}",
            field="priority"
        )

    return None


def validate_task_data(task_data: Dict[str, Any], required_fields: List[str] = None) -> List[ValidationError]:
    """Validate complete task data structure"""
    errors = []

    if required_fields is None:
        required_fields = ['title']  # Default required field

    # Check for required fields
    for field in required_fields:
        if field not in task_data or task_data[field] is None:
            errors.append(ValidationError(
                code="FIELD_REQUIRED",
                message=f"Required field '{field}' is missing",
                field=field
            ))

    # Validate title if present
    if 'title' in task_data:
        title_error = validate_title_length(str(task_data['title']))
        if title_error:
            errors.append(title_error)

    # Validate ID if present
    if 'id' in task_data:
        id_error = validate_task_id(task_data['id'])
        if id_error:
            errors.append(id_error)

    # Validate status if present
    if 'status' in task_data:
        status_error = validate_task_status(task_data['status'])
        if status_error:
            errors.append(status_error)

    # Validate priority if present
    if 'priority' in task_data:
        priority_error = validate_task_priority(task_data['priority'])
        if priority_error:
            errors.append(priority_error)

    # Validate due date if present
    if 'due_date' in task_data and task_data['due_date']:
        date_error = validate_datetime_string(str(task_data['due_date']))
        if date_error:
            errors.append(date_error)

    return errors


def aggregate_validation_errors(error_lists: List[List[ValidationError]]) -> List[ValidationError]:
    """Aggregate multiple lists of validation errors into a single list"""
    all_errors = []
    for error_list in error_lists:
        all_errors.extend(error_list)
    return all_errors


def has_errors(errors: List[ValidationError]) -> bool:
    """Check if there are any validation errors"""
    return len(errors) > 0


def get_error_messages(errors: List[ValidationError]) -> List[str]:
    """Extract error messages from validation errors"""
    return [error.message for error in errors]