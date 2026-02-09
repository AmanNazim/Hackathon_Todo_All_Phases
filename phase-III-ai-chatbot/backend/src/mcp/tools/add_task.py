"""MCP tool for adding tasks using FastMCP"""

import sys
import logging
from typing import Optional, Dict
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)


def register_add_task(mcp):
    """Register the add_task tool with FastMCP server"""

    @mcp.tool()
    async def add_task(user_id: str, title: str, description: str = "") -> Dict:
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
            result = await TaskService.create_task(
                user_id,
                title,
                description if description else None
            )
            logger.info(f"Task created: {result}")
            return result
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise

