"""MCP tool for updating tasks using FastMCP"""

import sys
import logging
from typing import Optional, Dict
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)


def register_update_task(mcp):
    """Register the update_task tool with FastMCP server"""

    @mcp.tool()
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

