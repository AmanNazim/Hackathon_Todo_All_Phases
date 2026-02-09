"""MCP tool for listing tasks"""

from typing import List, Dict
from src.services.task_service import TaskService


async def list_tasks(user_id: str, status: str = "all") -> List[Dict]:
    """
    Retrieve user's tasks with optional status filter.

    Args:
        user_id: User identifier
        status: Filter by status ("all", "pending", "completed")

    Returns:
        List of task dictionaries
    """
    return await TaskService.list_tasks(user_id, status)


# Tool schema for MCP
list_tasks_schema = {
    "name": "list_tasks",
    "description": "Retrieve user's tasks with optional status filter",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User identifier"
            },
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "description": "Filter by status (default: all)"
            }
        },
        "required": ["user_id"]
    }
}
