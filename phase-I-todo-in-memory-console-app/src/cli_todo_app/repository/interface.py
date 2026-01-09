"""
Repository interface for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Protocol
from ..domain.entities import Task
from ..domain.status import TaskStatus


class TaskRepository(Protocol):
    """
    In-memory repository interface for Task entities (T020)
    """

    @abstractmethod
    def add(self, task: Task) -> None:
        """Add a task to the repository"""
        ...

    @abstractmethod
    def get(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        ...

    @abstractmethod
    def update(self, task: Task) -> bool:
        """Update an existing task"""
        ...

    @abstractmethod
    def delete(self, task_id: str) -> bool:
        """Delete a task by ID"""
        ...

    @abstractmethod
    def list_all(self) -> List[Task]:
        """List all tasks"""
        ...

    @abstractmethod
    def list_by_status(self, status: TaskStatus) -> List[Task]:
        """List tasks filtered by status"""
        ...

    @abstractmethod
    def exists(self, task_id: str) -> bool:
        """Check if a task exists by ID"""
        ...