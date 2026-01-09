"""
Task entity for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import re
import uuid
from .status import TaskStatus


@dataclass
class Task:
    """
    Task entity as defined in specification section 6
    - id: UUID (immutable, unique identifier)
    - title: String (required, non-empty, max 256 characters)
    - description: String (optional, nullable, max 1024 characters)
    - created_at: DateTime (timestamp of creation)
    - updated_at: DateTime (timestamp of last modification)
    - status: TaskStatus enum (PENDING, COMPLETED)
    - tags: List<String> (optional, max 10 tags per task, alphanumeric with hyphens/underscores)
    """
    id: str
    title: str
    description: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    status: TaskStatus = TaskStatus.PENDING
    tags: List[str] = None

    def __post_init__(self):
        """Initialize timestamps and validate the task"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if self.tags is None:
            self.tags = []

        # Validate the task after initialization
        self.validate()

    def validate(self):
        """Validate the task entity according to domain rules"""
        # Validate title
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 256:
            raise ValueError(f"Task title exceeds maximum length of 256 characters, got {len(self.title)}")

        # Validate description
        if self.description and len(self.description) > 1024:
            raise ValueError(f"Task description exceeds maximum length of 1024 characters, got {len(self.description)}")

        # Validate tags
        if self.tags and len(self.tags) > 10:
            raise ValueError(f"Task cannot have more than 10 tags, got {len(self.tags)}")

        for tag in self.tags or []:
            if not self._is_valid_tag(tag):
                raise ValueError(f"Invalid tag format: {tag}. Tags must be alphanumeric with hyphens/underscores only.")

    def _is_valid_tag(self, tag: str) -> bool:
        """Validate tag format according to spec section 6"""
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', tag))

    def update(self, title: Optional[str] = None, description: Optional[str] = None, tags: Optional[List[str]] = None):
        """Update task properties while preserving unchanged fields"""
        if title is not None:
            if not title or len(title.strip()) == 0:
                raise ValueError("Task title cannot be empty")
            if len(title) > 256:
                raise ValueError(f"Task title exceeds maximum length of 256 characters, got {len(title)}")
            self.title = title.strip()

        if description is not None:
            if len(description) > 1024:
                raise ValueError(f"Task description exceeds maximum length of 1024 characters, got {len(description)}")
            self.description = description

        if tags is not None:
            if len(tags) > 10:
                raise ValueError(f"Task cannot have more than 10 tags, got {len(tags)}")
            for tag in tags:
                if not self._is_valid_tag(tag):
                    raise ValueError(f"Invalid tag format: {tag}. Tags must be alphanumeric with hyphens/underscores only.")
            self.tags = tags

        # Update the updated_at timestamp
        self.updated_at = datetime.now().isoformat()
        # Re-validate the task after update
        self.validate()

    def mark_completed(self):
        """Mark the task as completed"""
        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.now().isoformat()

    def mark_pending(self):
        """Mark the task as pending"""
        self.status = TaskStatus.PENDING
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation"""
        result = asdict(self)
        # Convert enum values to their string representations
        if isinstance(result['status'], TaskStatus):
            result['status'] = result['status'].value
        return result

    @classmethod
    def create(cls, title: str, description: Optional[str] = None, tags: Optional[List[str]] = None) -> 'Task':
        """Create a new task with validation"""
        task = cls(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            tags=tags or []
        )
        return task