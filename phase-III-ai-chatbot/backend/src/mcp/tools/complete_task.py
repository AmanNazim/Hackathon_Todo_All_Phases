"""MCP tool for completing tasks"""

from typing import Dict
from src.services.task_service import TaskService


async def complete_task(user_id: str, task_id: str) -> Dict:
    """
    Mark a task as completed.

    Args:
        user_id: User identifier
        task_id: Task identifier

    Returns:
        dict with task_id, status, and title
    """
    return await TaskService.complete_task(user_id, task_id)


# Tool schema for MCP
complete_task_schema = {
    "name": "complete_task",
    "description": "Mark a task as completed",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User identifier"
            },
            "task_id": {
                "type": "string",
                "description": "Task identifier"
            }
        },
        "required": ["user_id", "task_id"]
    }
}
