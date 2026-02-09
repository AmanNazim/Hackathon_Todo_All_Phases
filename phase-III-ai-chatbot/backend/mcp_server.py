"""
MCP Server for Task Management Tools

This server exposes task management capabilities to AI agents through
the Model Context Protocol using FastMCP.
"""

import sys
import logging
from typing import Optional, List, Dict
from fastmcp import FastMCP

# Configure logging to stderr only (STDIO constraint)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

# Import TaskService for data operations
from src.services.task_service import TaskService

# Initialize FastMCP server
mcp = FastMCP("Task Management Server")


@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """
    Create a new task for the user.

    Args:
        user_id: User identifier
        title: Task title
        description: Optional task description

    Returns:
        dict with task_id (integer), status, and title
    """
    logger.info(f"add_task called: user_id={user_id}, title={title}")

    try:
        result = await TaskService.create_task(user_id, title, description if description else None)
        logger.info(f"Task created: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise


@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> List[Dict]:
    """
    Retrieve user's tasks with optional status filter.

    Args:
        user_id: User identifier
        status: Filter by status ("all", "pending", "completed")

    Returns:
        List of task dictionaries with id, title, completed fields
    """
    logger.info(f"list_tasks called: user_id={user_id}, status={status}")

    # Validate status parameter
    if status not in ["all", "pending", "completed"]:
        raise ValueError(f"Invalid status: {status}. Must be 'all', 'pending', or 'completed'")

    try:
        result = await TaskService.list_tasks(user_id, status)
        logger.info(f"Listed {len(result)} tasks")
        return result
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise


@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> dict:
    """
    Mark a task as completed.

    Args:
        user_id: User identifier
        task_id: Task identifier (integer)

    Returns:
        dict with task_id, status, and title
    """
    logger.info(f"complete_task called: user_id={user_id}, task_id={task_id}")

    try:
        result = await TaskService.complete_task(user_id, task_id)
        logger.info(f"Task completed: {result}")
        return result
    except ValueError as e:
        logger.error(f"Task not found or permission error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        raise


@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """
    Delete a task from the user's list.

    Args:
        user_id: User identifier
        task_id: Task identifier (integer)

    Returns:
        dict with task_id, status, and title (before deletion)
    """
    logger.info(f"delete_task called: user_id={user_id}, task_id={task_id}")

    try:
        result = await TaskService.delete_task(user_id, task_id)
        logger.info(f"Task deleted: {result}")
        return result
    except ValueError as e:
        logger.error(f"Task not found or permission error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise


@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """
    Update task title or description.

    Args:
        user_id: User identifier
        task_id: Task identifier (integer)
        title: New task title (optional)
        description: New task description (optional)

    Returns:
        dict with task_id, status, and updated title
    """
    logger.info(f"update_task called: user_id={user_id}, task_id={task_id}")

    # Validate at least one field is provided
    if title is None and description is None:
        raise ValueError("At least one of 'title' or 'description' must be provided")

    try:
        result = await TaskService.update_task(user_id, task_id, title, description)
        logger.info(f"Task updated: {result}")
        return result
    except ValueError as e:
        logger.error(f"Task not found or permission error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting Task Management MCP Server")
    logger.info("Available tools: add_task, list_tasks, complete_task, delete_task, update_task")

    # Run the MCP server with STDIO transport
    mcp.run()
