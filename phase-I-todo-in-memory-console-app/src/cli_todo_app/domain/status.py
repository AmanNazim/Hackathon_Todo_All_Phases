"""
TaskStatus enum for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""
from enum import Enum


class TaskStatus(Enum):
    """
    Task status enumeration as defined in specification section 6
    """
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"