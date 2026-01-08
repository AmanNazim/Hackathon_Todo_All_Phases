"""
Event classes for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum
import uuid
from .entities import Task


from enum import Enum, auto

class EventType(Enum):
    """Enumeration of all possible event types"""
    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_DELETED = "TASK_DELETED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_REOPENED = "TASK_REOPENED"

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if isinstance(other, EventType):
            return self.value == other.value
        return False


@dataclass
class TaskEvent:
    """Base class for all task events"""
    id: str
    type: EventType
    timestamp: str
    aggregate_id: str  # The ID of the task this event relates to
    data: Dict[str, Any]

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    @classmethod
    def create(cls, event_type: EventType, aggregate_id: str, data: Dict[str, Any]) -> 'TaskEvent':
        """Factory method to create events"""
        return cls(
            id=str(uuid.uuid4()),
            type=event_type,
            timestamp=datetime.now().isoformat(),
            aggregate_id=aggregate_id,
            data=data
        )


@dataclass
class TaskCreatedEvent(TaskEvent):
    """Event recorded when a task is added"""
    def __init__(self, task: Task):
        super().__init__(
            id=str(uuid.uuid4()),
            type=EventType.TASK_CREATED,
            timestamp=datetime.now().isoformat(),
            aggregate_id=task.id,
            data={
                'title': task.title,
                'description': task.description,
                'created_at': task.created_at,
                'status': task.status.value,
                'tags': task.tags
            }
        )


@dataclass
class TaskUpdatedEvent(TaskEvent):
    """Event recorded when task properties change"""
    def __init__(self, task: Task, old_values: Dict[str, Any]):
        super().__init__(
            id=str(uuid.uuid4()),
            type=EventType.TASK_UPDATED,
            timestamp=datetime.now().isoformat(),
            aggregate_id=task.id,
            data={
                'new_values': {
                    'title': task.title,
                    'description': task.description,
                    'updated_at': task.updated_at,
                    'status': task.status.value,
                    'tags': task.tags
                },
                'old_values': old_values
            }
        )


@dataclass
class TaskDeletedEvent(TaskEvent):
    """Event recorded when task is removed"""
    def __init__(self, task: Task):
        super().__init__(
            id=str(uuid.uuid4()),
            type=EventType.TASK_DELETED,
            timestamp=datetime.now().isoformat(),
            aggregate_id=task.id,
            data={
                'title': task.title,
                'description': task.description,
                'created_at': task.created_at,
                'updated_at': task.updated_at,
                'status': task.status.value,
                'tags': task.tags
            }
        )


@dataclass
class TaskCompletedEvent(TaskEvent):
    """Event recorded when task status changes to completed"""
    def __init__(self, task: Task, previous_status: str = "PENDING"):
        super().__init__(
            id=str(uuid.uuid4()),
            type=EventType.TASK_COMPLETED,
            timestamp=datetime.now().isoformat(),
            aggregate_id=task.id,
            data={
                'previous_status': previous_status,
                'updated_at': task.updated_at
            }
        )


@dataclass
class TaskReopenedEvent(TaskEvent):
    """Event recorded when task status changes to pending"""
    def __init__(self, task: Task, previous_status: str = "COMPLETED"):
        super().__init__(
            id=str(uuid.uuid4()),
            type=EventType.TASK_REOPENED,
            timestamp=datetime.now().isoformat(),
            aggregate_id=task.id,
            data={
                'previous_status': previous_status,
                'updated_at': task.updated_at
            }
        )