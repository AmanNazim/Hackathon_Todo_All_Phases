"""MCP tool for deleting tasks using FastMCP"""

import sys
import logging
from typing import Dict
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)


def register_delete_task(mcp):
    """Register the delete_task tool with FastMCP server"""

    @mcp.tool()
    async def delete_task(user_id: str, task_id: int) -> Dict:
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

