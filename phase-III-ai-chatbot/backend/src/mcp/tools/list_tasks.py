"""MCP tool for listing tasks using FastMCP"""

import sys
import logging
from typing import List, Dict
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)


def register_list_tasks(mcp):
    """Register the list_tasks tool with FastMCP server"""

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

