"""
Configuration Management System for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration settings"""
    # Performance settings
    max_tasks_memory_limit: int = 100 * 1024 * 1024  # 100MB in bytes
    max_tasks_count: int = 10000
    pagination_threshold: int = 50

    # Command processing settings
    max_title_length: int = 256
    max_description_length: int = 1024
    max_tags_per_task: int = 10

    # Theme settings
    default_theme: str = "minimal"
    available_themes: list = None

    # Performance thresholds
    add_task_timeout_ms: int = 100
    view_tasks_timeout_ms: int = 200
    update_task_timeout_ms: int = 100
    delete_task_timeout_ms: int = 100
    complete_task_timeout_ms: int = 100
    list_with_filters_timeout_ms: int = 50
    undo_operation_timeout_ms: int = 100

    def __post_init__(self):
        if self.available_themes is None:
            self.available_themes = ["minimal", "emoji", "hacker", "professional"]


class ConfigManager:
    """Configuration management system"""

    def __init__(self):
        self._config = self._load_config()

    def _load_config(self) -> AppConfig:
        """Load configuration from environment variables or defaults"""
        config = AppConfig()

        # Override defaults with environment variables if present
        config.max_tasks_memory_limit = int(os.getenv('MAX_TASKS_MEMORY_LIMIT', config.max_tasks_memory_limit))
        config.max_tasks_count = int(os.getenv('MAX_TASKS_COUNT', config.max_tasks_count))
        config.pagination_threshold = int(os.getenv('PAGINATION_THRESHOLD', config.pagination_threshold))

        config.max_title_length = int(os.getenv('MAX_TITLE_LENGTH', config.max_title_length))
        config.max_description_length = int(os.getenv('MAX_DESCRIPTION_LENGTH', config.max_description_length))
        config.max_tags_per_task = int(os.getenv('MAX_TAGS_PER_TASK', config.max_tags_per_task))

        config.default_theme = os.getenv('DEFAULT_THEME', config.default_theme)

        config.add_task_timeout_ms = int(os.getenv('ADD_TASK_TIMEOUT_MS', config.add_task_timeout_ms))
        config.view_tasks_timeout_ms = int(os.getenv('VIEW_TASKS_TIMEOUT_MS', config.view_tasks_timeout_ms))
        config.update_task_timeout_ms = int(os.getenv('UPDATE_TASK_TIMEOUT_MS', config.update_task_timeout_ms))
        config.delete_task_timeout_ms = int(os.getenv('DELETE_TASK_TIMEOUT_MS', config.delete_task_timeout_ms))
        config.complete_task_timeout_ms = int(os.getenv('COMPLETE_TASK_TIMEOUT_MS', config.complete_task_timeout_ms))
        config.list_with_filters_timeout_ms = int(os.getenv('LIST_WITH_FILTERS_TIMEOUT_MS', config.list_with_filters_timeout_ms))
        config.undo_operation_timeout_ms = int(os.getenv('UNDO_OPERATION_TIMEOUT_MS', config.undo_operation_timeout_ms))

        return config

    @property
    def config(self) -> AppConfig:
        """Get the current configuration"""
        return self._config

    def get(self, key: str) -> Any:
        """Get a configuration value by key"""
        return getattr(self._config, key, None)

    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value (if it exists)"""
        if hasattr(self._config, key):
            setattr(self._config, key, value)
            return True
        return False

    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from a dictionary"""
        for key, value in config_dict.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config_manager.config