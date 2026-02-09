"""MCP tool for updating tasks"""

from typing import Optional, Dict
from src.services.task_service import TaskService


async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict:
    """
    Update task title or description.

    Args:
        user_id: User identifier
        task_id: Task identifier (integer)
        title: New task title (optional)
        description: New task description (optional)

    Returns:
        dict with task_id, status, and title
    """
    return await TaskService.update_task(user_id, task_id, title, description)


# Tool schema for MCP
update_task_schema = {
    "name": "update_task",
    "description": "Update task title or description",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User identifier"
            },
            "task_id": {
                "type": "integer",
                "description": "Task identifier"
            },
            "title": {
                "type": "string",
                "description": "New task title (optional)"
            },
            "description": {
                "type": "string",
                "description": "New task description (optional)"
            }
        },
        "required": ["user_id", "task_id"]
    }
}
