"""MCP tool for completing tasks using FastMCP"""

import sys
import logging
from typing import Dict
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)


def register_complete_task(mcp):
    """Register the complete_task tool with FastMCP server"""

    @mcp.tool()
    async def complete_task(user_id: str, task_id: int) -> Dict:
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

