---
name: task-validation-skill
description: A centralized, rule-based validation system for task operations that ensures correctness, consistency, and safety across Python CLI applications, FastAPI services, chat agents, event-driven systems, and MCP tools. Enforces explicit validation rules before any state mutation occurs, preventing invalid operations, detecting invalid inputs early, and stopping propagation of corrupted state.
---

# Task Validation Skill

## 1. Purpose & Scope

### What the skill validates
The Task Validation Skill provides a centralized, rule-based validation system that ensures correctness, consistency, and safety of task-related operations. It validates:
- Task titles and descriptions for proper format and content
- Task identities and existence before operations
- Operation parameters and state transitions
- Input data integrity and business rule compliance

### Why centralized validation is required
Centralized validation eliminates duplicate validation logic across different interfaces and ensures consistent enforcement of business rules. Without centralized validation, inconsistencies emerge between CLI, API, and event-driven interfaces, leading to invalid states and unpredictable behavior. This skill ensures that all task operations meet predefined quality standards before any state mutation occurs, preventing corruption of the task management system.

## 2. Validation Responsibilities

### What this skill enforces
- **Input validation**: Verifies that all incoming task data meets defined criteria
- **Identity validation**: Ensures referenced task IDs exist before operations
- **State safety**: Prevents partial mutations and ensures atomic validation
- **Business rule compliance**: Enforces domain-specific constraints
- **Error reporting**: Provides clear, descriptive validation failures

### What it explicitly does NOT do
- **State mutation**: Validation does not modify task data or persist changes
- **UI rendering**: Validation does not handle display or user interface concerns
- **Persistence logic**: Validation does not interact with databases or storage systems
- **Authentication/authorization**: Validation does not handle access control
- **Business logic execution**: Validation only verifies inputs, not performs operations

## 3. Core Validation Rules

### Task Title Validation
- **Rule**: Title must be present, between 1-200 characters, and not whitespace-only
- **Rationale**: Prevents empty or meaningless tasks while allowing reasonable title lengths
- **Implementation**: String length check, whitespace trimming, character count validation

### Task Identity Validation
- **Rule**: Task IDs must be valid identifiers; non-existing IDs block operations
- **Rationale**: Prevents operations on non-existent tasks, maintaining data integrity
- **Implementation**: ID format validation, existence verification against task registry

### State Safety Rules
- **Rule**: No partial state mutations; validation failures block execution completely
- **Rationale**: Maintains system consistency and prevents corrupted intermediate states
- **Implementation**: Atomic validation checks that must pass entirely before operation proceeds

## 4. Edge Case Handling

### Empty title input
- **Expected behavior**: Validation fails with descriptive error message
- **Response**: "Task title cannot be empty"

### Title exceeding maximum length
- **Expected behavior**: Validation fails when title exceeds 200 characters
- **Response**: "Task title exceeds maximum length of 200 characters"

### Title with only whitespace
- **Expected behavior**: Validation fails after trimming whitespace
- **Response**: "Task title cannot contain only whitespace"

### Non-integer or malformed task IDs
- **Expected behavior**: Validation fails for non-numeric or invalid ID formats
- **Response**: "Invalid task ID format"

### Negative or zero task IDs (if IDs are numeric)
- **Expected behavior**: Validation fails for non-positive numeric IDs
- **Response**: "Task ID must be a positive integer"

### Duplicate operations (e.g., marking an already-completed task as complete)
- **Expected behavior**: Validation passes but operation may be idempotent
- **Response**: Operation proceeds but may return unchanged state

### Concurrent-like repeated commands within the same session
- **Expected behavior**: Each operation is validated independently
- **Response**: Sequential validation ensures each operation meets criteria

### Invalid command sequences (e.g., update before add)
- **Expected behavior**: Individual operations are validated without sequence enforcement
- **Response**: Each command is validated in isolation

### Null or missing fields in task data structures
- **Expected behavior**: Required fields trigger validation failures
- **Response**: Specific error indicating which field is missing

## 5. Validation Architecture

### Validation Engine Class
Central orchestrator that manages validation rule execution and error aggregation.

### Rule Objects/Policies
Individual validation units that encapsulate specific business rules and can be composed together.

### Validation Entry Points
Standardized interfaces for different task operations (create, update, delete, mark complete).

### Error Factory
Standardized error object creation that provides consistent validation failure reporting.

### Task Repository Interface
Abstraction for checking task existence without coupling to specific persistence implementations.

## 6. Validation Flow

### Create Task Validation Lifecycle
1. Receive task creation request with title/description
2. Validate title meets length and content requirements
3. Validate all required fields are present
4. Aggregate validation errors if any fail
5. Return validation result (pass/fail with errors)
6. Proceed with creation only if validation passes

### Update Task Validation Lifecycle
1. Validate target task ID format and validity
2. Verify target task exists in repository
3. Validate new title/description if provided
4. Aggregate validation errors if any fail
5. Return validation result (pass/fail with errors)
6. Proceed with update only if validation passes

### Delete Task Validation Lifecycle
1. Validate target task ID format and validity
2. Verify target task exists in repository
3. Aggregate validation errors if any fail
4. Return validation result (pass/fail with errors)
5. Proceed with deletion only if validation passes

### Mark Complete/Incomplete Validation Lifecycle
1. Validate target task ID format and validity
2. Verify target task exists in repository
3. Aggregate validation errors if any fail
4. Return validation result (pass/fail with errors)
5. Proceed with state change only if validation passes

## 7. Error Modeling & Reporting

### Validation Error Object Structure
```python
class ValidationError:
    code: str          # Machine-readable error identifier
    message: str       # Human-readable error description
    field: str         # Field that failed validation
    severity: str      # Error level (error, warning)
    timestamp: datetime # When validation occurred
```

### Error Categories
- **INPUT_ERROR**: Invalid format, length, or content
- **IDENTITY_ERROR**: Non-existent or invalid task ID
- **STATE_ERROR**: Invalid state transitions or operations
- **BUSINESS_RULE_ERROR**: Violation of domain-specific constraints

### Error Aggregation
Validation failures are collected in a comprehensive error object that includes all validation violations from a single operation, enabling clients to address multiple issues simultaneously.

## 8. Reusability Across Systems

### CLI Applications
Validation logic integrates as a service layer that CLI commands call before performing operations. Command handlers receive validation results and format errors appropriately for terminal output.

### FastAPI Endpoints
Validation operates as a dependency or middleware that validates request bodies and path parameters before controller methods execute. Validation errors translate to appropriate HTTP status codes and response formats.

### Chat Agents
Validation ensures user inputs meet criteria before processing agent responses. Failed validations return clear feedback to users about required corrections.

### Event-Driven Systems
Validation applies to incoming events before processing, ensuring only valid task operations enter the event stream. Invalid events are rejected with appropriate logging.

### MCP Tools
Validation operates as a pre-execution check that ensures all required parameters meet criteria before tool execution proceeds, preventing invalid operations from occurring.

## 9. Extensibility Strategy

### Rule Registration Pattern
New validation rules register with the validation engine without modifying existing logic, maintaining backward compatibility while enabling new constraints.

### Plugin Architecture
Validation rules can be implemented as pluggable components that extend base functionality without changing core validation logic.

### Configuration-Driven Rules
Rules can accept configuration parameters that modify their behavior without code changes, allowing for environment-specific validation criteria.

### Decorator Pattern
Validation can be applied to methods or functions using decorators that wrap existing operations with validation checks.

### Interface Abstraction
Validation interfaces remain stable while implementation details evolve, ensuring consuming code doesn't break when validation logic updates.

## 10. Non-Goals & Constraints

### Explicitly Forbidden Behaviors
- **State modification**: Validation must not alter any task data or system state
- **Persistence operations**: Validation must not save, update, or delete data
- **UI rendering**: Validation must not generate user interface elements
- **Authentication**: Validation must not handle user permissions or access control
- **External service calls**: Validation must not make network requests or external API calls

### What this skill intentionally avoids
- **Complex business logic**: Focus remains on input validation, not operational logic
- **Performance optimization**: Validation prioritizes correctness over speed
- **Speculative features**: Only implements currently required validation rules
- **Deep integration**: Maintains loose coupling with other system components
- **Custom serialization**: Uses standard data formats and error representations

## Implementation Examples

### Basic Validation Engine
```python
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ValidationError:
    code: str
    message: str
    field: str
    severity: str = "error"

class ValidationEngine:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule_func):
        self.rules.append(rule_func)

    def validate(self, data) -> List[ValidationError]:
        errors = []
        for rule in self.rules:
            rule_errors = rule(data)
            if rule_errors:
                errors.extend(rule_errors)
        return errors

def validate_task_title(task_data) -> List[ValidationError]:
    errors = []
    title = task_data.get('title', '')

    if not title:
        errors.append(ValidationError(
            code="TITLE_REQUIRED",
            message="Task title cannot be empty",
            field="title"
        ))
    elif len(title.strip()) == 0:
        errors.append(ValidationError(
            code="TITLE_WHITESPACE_ONLY",
            message="Task title cannot contain only whitespace",
            field="title"
        ))
    elif len(title) > 200:
        errors.append(ValidationError(
            code="TITLE_TOO_LONG",
            message="Task title exceeds maximum length of 200 characters",
            field="title"
        ))

    return errors
```

### Usage in Different Contexts

For implementation examples and reference materials, see:
- `references/validation-examples.md` - Detailed implementation patterns
- `scripts/validation-tools.py` - Reusable validation utilities
- `assets/validation-config.json` - Configuration templates