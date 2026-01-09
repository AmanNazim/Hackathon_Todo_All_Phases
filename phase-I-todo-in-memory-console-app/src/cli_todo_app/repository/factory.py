"""
Repository factory for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""
from .memory_repository import InMemoryTaskRepository
from .interface import TaskRepository


class RepositoryFactory:
    """
    Factory class for creating repository instances
    """

    @staticmethod
    def create_task_repository() -> TaskRepository:
        """
        Create and return an instance of the task repository
        """
        return InMemoryTaskRepository()