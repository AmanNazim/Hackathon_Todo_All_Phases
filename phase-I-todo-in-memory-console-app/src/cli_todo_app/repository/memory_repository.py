"""
Concrete in-memory repository implementation for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""
from typing import List, Optional, Dict
import threading
from ..domain.entities import Task
from ..domain.status import TaskStatus
from .interface import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """
    Concrete in-memory repository with thread-safe operations (T021)
    Implements all required CRUD methods (T022)
    """

    def __init__(self):
        # Use a dictionary for O(1) lookups
        self._tasks: Dict[str, Task] = {}
        # Thread lock for thread safety
        self._lock = threading.RLock()

    def add(self, task: Task) -> None:
        """
        Add a task to the repository
        Thread-safe operation with lock
        """
        with self._lock:
            # Validate that the task doesn't already exist to prevent duplicates (T024)
            if task.id in self._tasks:
                raise ValueError(f"Task with ID {task.id} already exists")

            self._tasks[task.id] = task

    def get(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID
        Thread-safe operation with lock
        """
        with self._lock:
            return self._tasks.get(task_id)

    def update(self, task: Task) -> bool:
        """
        Update an existing task
        Returns True if task was updated, False if task doesn't exist
        Thread-safe operation with lock
        """
        with self._lock:
            if task.id not in self._tasks:
                return False

            self._tasks[task.id] = task
            return True

    def delete(self, task_id: str) -> bool:
        """
        Delete a task by ID
        Returns True if task was deleted, False if task doesn't exist
        Thread-safe operation with lock
        """
        with self._lock:
            if task_id not in self._tasks:
                return False

            del self._tasks[task_id]
            return True

    def list_all(self) -> List[Task]:
        """
        List all tasks
        Thread-safe operation with lock
        """
        with self._lock:
            # Return a copy of the values to prevent external modification
            return list(self._tasks.values())

    def list_by_status(self, status: TaskStatus) -> List[Task]:
        """
        List tasks filtered by status (T023)
        Thread-safe operation with lock
        """
        with self._lock:
            return [task for task in self._tasks.values() if task.status == status]

    def exists(self, task_id: str) -> bool:
        """
        Check if a task exists by ID
        Thread-safe operation with lock
        """
        with self._lock:
            return task_id in self._tasks

    def clear(self) -> None:
        """
        Clear all tasks from the repository
        Thread-safe operation with lock
        """
        with self._lock:
            self._tasks.clear()

    def count(self) -> int:
        """
        Count the number of tasks in the repository
        Thread-safe operation with lock
        """
        with self._lock:
            return len(self._tasks)