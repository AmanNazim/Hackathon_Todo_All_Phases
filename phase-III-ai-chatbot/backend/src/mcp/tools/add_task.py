"""MCP tool for adding tasks"""

from typing import Optional, Dict
from src.services.task_service import TaskService


async def add_task(user_id: str, title: str, description: Optional[str] = None) -> Dict:
    """
    Create a new task for the user.

    Args:
        user_id: User identifier
        title: Task title
        description: Optional task description

    Returns:
        dict with task_id, status, and title
    """
    return await TaskService.create_task(user_id, title, description)


# Tool schema for MCP
add_task_schema = {
    "name": "add_task",
    "description": "Create a new task for the user",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User identifier"
            },
            "title": {
                "type": "string",
                "description": "Task title"
            },
            "description": {
                "type": "string",
                "description": "Optional task description"
            }
        },
        "required": ["user_id", "title"]
    }
}
