# Task Validation Examples and Patterns

## Validation Engine Implementation

### Complete Validation Engine Class
```python
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class ValidationError:
    code: str
    message: str
    field: str
    severity: str = "error"
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ValidationRule:
    def __init__(self, name: str, validate_func: Callable):
        self.name = name
        self.validate_func = validate_func

    def validate(self, data: Dict[str, Any]) -> List[ValidationError]:
        return self.validate_func(data)

class TaskValidationEngine:
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Initialize with default task validation rules"""
        self.add_rule(ValidationRule("task_title", validate_task_title))
        self.add_rule(ValidationRule("task_id", validate_task_id))
        self.add_rule(ValidationRule("task_status", validate_task_status))

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule to the engine"""
        self.rules.append(rule)

    def validate(self, data: Dict[str, Any], operation: str = "create") -> List[ValidationError]:
        """Validate data against all registered rules"""
        all_errors = []

        for rule in self.rules:
            try:
                rule_errors = rule.validate(data)
                if rule_errors:
                    # Filter errors based on operation if needed
                    filtered_errors = self._filter_errors_by_operation(rule_errors, operation)
                    all_errors.extend(filtered_errors)
            except Exception as e:
                all_errors.append(ValidationError(
                    code="VALIDATION_ERROR",
                    message=f"Error in validation rule {rule.name}: {str(e)}",
                    field="system"
                ))

        return all_errors

    def _filter_errors_by_operation(self, errors: List[ValidationError], operation: str) -> List[ValidationError]:
        """Filter errors based on the operation being performed"""
        # For now, return all errors - can be extended for operation-specific filtering
        return errors

    def validate_create_task(self, task_data: Dict[str, Any]) -> List[ValidationError]:
        """Validate task creation data"""
        return self.validate(task_data, "create")

    def validate_update_task(self, task_data: Dict[str, Any]) -> List[ValidationError]:
        """Validate task update data"""
        return self.validate(task_data, "update")

    def validate_task_id(self, task_id: Any) -> List[ValidationError]:
        """Validate a single task ID"""
        errors = []
        if task_id is None:
            errors.append(ValidationError(
                code="TASK_ID_REQUIRED",
                message="Task ID is required",
                field="id"
            ))
        elif not isinstance(task_id, (int, str)) or str(task_id).strip() == "":
            errors.append(ValidationError(
                code="TASK_ID_INVALID",
                message="Task ID must be a valid identifier",
                field="id"
            ))
        elif isinstance(task_id, int) and task_id <= 0:
            errors.append(ValidationError(
                code="TASK_ID_INVALID",
                message="Task ID must be a positive integer",
                field="id"
            ))
        return errors

def validate_task_title(data: Dict[str, Any]) -> List[ValidationError]:
    """Validate task title requirements"""
    errors = []
    title = data.get('title', '')

    if 'title' not in data:
        # Title is not required for all operations (like delete)
        return errors

    if not title:
        errors.append(ValidationError(
            code="TITLE_REQUIRED",
            message="Task title cannot be empty",
            field="title"
        ))
    elif isinstance(title, str) and len(title.strip()) == 0:
        errors.append(ValidationError(
            code="TITLE_WHITESPACE_ONLY",
            message="Task title cannot contain only whitespace",
            field="title"
        ))
    elif isinstance(title, str) and len(title) > 200:
        errors.append(ValidationError(
            code="TITLE_TOO_LONG",
            message="Task title exceeds maximum length of 200 characters",
            field="title"
        ))

    return errors

def validate_task_id(data: Dict[str, Any]) -> List[ValidationError]:
    """Validate task ID requirements"""
    errors = []
    task_id = data.get('id')

    if 'id' in data:  # Only validate if ID is provided
        if task_id is None:
            errors.append(ValidationError(
                code="TASK_ID_REQUIRED",
                message="Task ID cannot be null",
                field="id"
            ))
        elif not isinstance(task_id, (int, str)) or str(task_id).strip() == "":
            errors.append(ValidationError(
                code="TASK_ID_INVALID",
                message="Task ID must be a valid identifier",
                field="id"
            ))
        elif isinstance(task_id, int) and task_id <= 0:
            errors.append(ValidationError(
                code="TASK_ID_INVALID",
                message="Task ID must be a positive integer",
                field="id"
            ))

    return errors

def validate_task_status(data: Dict[str, Any]) -> List[ValidationError]:
    """Validate task status values"""
    errors = []
    status = data.get('status')

    if 'status' in data and status is not None:  # Only validate if status is provided
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            errors.append(ValidationError(
                code="STATUS_INVALID",
                message=f"Task status must be one of: {', '.join(valid_statuses)}",
                field="status"
            ))

    return errors
```

## Usage Examples

### CLI Application Integration
```python
import sys
from typing import Dict, Any

def cli_create_task(title: str, description: str = None) -> bool:
    """CLI command to create a task with validation"""
    task_data = {
        'title': title,
        'description': description
    }

    validator = TaskValidationEngine()
    errors = validator.validate_create_task(task_data)

    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error.message}")
        return False

    # Proceed with task creation
    print(f"Task created successfully: {title}")
    return True

def cli_update_task(task_id: int, title: str = None, status: str = None) -> bool:
    """CLI command to update a task with validation"""
    task_data = {
        'id': task_id,
        'title': title,
        'status': status
    }

    validator = TaskValidationEngine()
    errors = validator.validate_update_task(task_data)

    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error.message}")
        return False

    # Proceed with task update
    print(f"Task {task_id} updated successfully")
    return True
```

### FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None

app = FastAPI()
validator = TaskValidationEngine()

@app.post("/tasks/")
def create_task(request: TaskCreateRequest):
    task_data = request.dict()
    errors = validator.validate_create_task(task_data)

    if errors:
        raise HTTPException(
            status_code=400,
            detail=[{"field": e.field, "message": e.message} for e in errors]
        )

    # Proceed with task creation
    return {"message": "Task created successfully", "data": task_data}
```

### Event-Driven System Integration
```python
def process_task_created_event(event_data: Dict[str, Any]) -> bool:
    """Process a task created event with validation"""
    validator = TaskValidationEngine()
    errors = validator.validate_create_task(event_data)

    if errors:
        # Log validation errors and reject the event
        for error in errors:
            print(f"Event validation failed: {error.message}")
        return False

    # Process the valid event
    print(f"Processing valid task creation: {event_data.get('title')}")
    return True
```