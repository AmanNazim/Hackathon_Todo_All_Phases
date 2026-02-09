"""
ChatKit Integration Module

This module provides OpenAI ChatKit integration for the Phase III AI Chatbot.
It includes widget builders, event adapters, action handlers, and the ChatKitServer implementation.
"""

from .server import TaskChatKitServer
from .widgets import (
    build_task_list_widget,
    build_task_card,
    build_task_form,
    build_starter_prompts
)
from .events import convert_to_chatkit_event
from .actions import (
    handle_complete_task,
    handle_delete_task,
    handle_update_task,
    handle_create_task
)

__all__ = [
    "TaskChatKitServer",
    "build_task_list_widget",
    "build_task_card",
    "build_task_form",
    "build_starter_prompts",
    "convert_to_chatkit_event",
    "handle_complete_task",
    "handle_delete_task",
    "handle_update_task",
    "handle_create_task",
]
