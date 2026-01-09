"""
Validation module for CLI Todo Application Domain
Phase I: In-Memory Python CLI Todo Application
"""
from typing import Any, Dict
from .entities import Task
import re


class DomainValidator:
    """Validator for domain entities and rules"""

    @staticmethod
    def validate_task_title(title: str) -> bool:
        """
        Validate task title according to spec:
        - Non-empty
        - Max 256 characters
        """
        if not title or len(title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if len(title) > 256:
            raise ValueError(f"Task title exceeds maximum length of 256 characters, got {len(title)}")
        return True

    @staticmethod
    def validate_task_description(description: str) -> bool:
        """
        Validate task description according to spec:
        - Max 1024 characters (if provided)
        """
        if description and len(description) > 1024:
            raise ValueError(f"Task description exceeds maximum length of 1024 characters, got {len(description)}")
        return True

    @staticmethod
    def validate_task_tags(tags: list) -> bool:
        """
        Validate task tags according to spec:
        - Max 10 tags per task
        - Alphanumeric with hyphens/underscores only
        """
        if tags and len(tags) > 10:
            raise ValueError(f"Task cannot have more than 10 tags, got {len(tags)}")

        for tag in tags or []:
            if not DomainValidator._is_valid_tag_format(tag):
                raise ValueError(f"Invalid tag format: {tag}. Tags must be alphanumeric with hyphens/underscores only.")
        return True

    @staticmethod
    def _is_valid_tag_format(tag: str) -> bool:
        """Validate tag format (alphanumeric with hyphens/underscores)"""
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', tag))

    @staticmethod
    def validate_task(task: Task) -> bool:
        """
        Validate a complete task entity according to domain rules
        """
        DomainValidator.validate_task_title(task.title)
        DomainValidator.validate_task_description(task.description)
        DomainValidator.validate_task_tags(task.tags)
        return True

    @staticmethod
    def validate_task_update(title: str = None, description: str = None, tags: list = None) -> bool:
        """
        Validate task update parameters
        """
        if title is not None:
            DomainValidator.validate_task_title(title)
        if description is not None:
            DomainValidator.validate_task_description(description)
        if tags is not None:
            DomainValidator.validate_task_tags(tags)
        return True