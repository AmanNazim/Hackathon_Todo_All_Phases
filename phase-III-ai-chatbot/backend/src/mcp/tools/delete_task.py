"""MCP tool for deleting tasks"""

from typing import Dict
from src.services.task_service import TaskService


async def delete_task(user_id: str, task_id: str) -> Dict:
    """
    Delete a task.

    Args:
        user_id: User identifier
        task_id: Task identifier

    Returns:
        dict with task_id, status, and title
    """
    return await TaskService.delete_task(user_id, task_id)


# Tool schema for MCP
delete_task_schema = {
    "name": "delete_task",
    "description": "Delete a task from the user's list",
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
