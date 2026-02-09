"""
ChatKit Action Handlers

Functions to handle widget actions for task management.
"""

from typing import Dict, Any
from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task


async def handle_complete_task(task_id: str, user_id: str) -> Dict[str, Any]:
    """
    Handle complete task action.

    Args:
        task_id: ID of the task to complete
        user_id: User identifier

    Returns:
        Result dictionary
    """
    try:
        result = await complete_task.complete_task(user_id, task_id)
        return {
            "success": True,
            "message": f"Task '{result.get('title', 'Task')}' marked as complete",
            "task": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to complete task: {str(e)}"
        }


async def handle_delete_task(task_id: str, user_id: str) -> Dict[str, Any]:
    """
    Handle delete task action.

    Args:
        task_id: ID of the task to delete
        user_id: User identifier

    Returns:
        Result dictionary
    """
    try:
        result = await delete_task.delete_task(user_id, task_id)
        return {
            "success": True,
            "message": f"Task '{result.get('title', 'Task')}' deleted",
            "task": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to delete task: {str(e)}"
        }


async def handle_update_task(payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Handle update task action.

    Args:
        payload: Action payload with task_id, title, description
        user_id: User identifier

    Returns:
        Result dictionary
    """
    try:
        task_id = payload.get("task_id")
        title = payload.get("title")
        description = payload.get("description")

        result = await update_task.update_task(user_id, task_id, title, description)
        return {
            "success": True,
            "message": f"Task '{result.get('title', 'Task')}' updated",
            "task": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to update task: {str(e)}"
        }


async def handle_create_task(payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Handle create task action.

    Args:
        payload: Action payload with title, description
        user_id: User identifier

    Returns:
        Result dictionary
    """
    try:
        title = payload.get("title")
        description = payload.get("description")

        result = await add_task.add_task(user_id, title, description)
        return {
            "success": True,
            "message": f"Task '{result.get('title', 'Task')}' created",
            "task": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create task: {str(e)}"
        }


async def handle_list_tasks(status: str, user_id: str) -> Dict[str, Any]:
    """
    Handle list tasks action.

    Args:
        status: Filter by status (all, pending, completed)
        user_id: User identifier

    Returns:
        Result dictionary with tasks list
    """
    try:
        tasks = await list_tasks.list_tasks(user_id, status)
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to list tasks: {str(e)}",
            "tasks": []
        }
