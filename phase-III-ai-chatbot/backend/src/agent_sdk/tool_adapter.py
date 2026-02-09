"""
Tool Adapter

Converts MCP tools to OpenAI Agents SDK function tools with user_id context injection.
"""

from agents.decorators import function_tool
from typing import List, Optional, Dict
from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task


def create_function_tools(user_id: str) -> List:
    """
    Create function tools with user_id context injected.

    Args:
        user_id: User identifier to inject into all tool calls

    Returns:
        List of function tools ready for agent use
    """

    @function_tool
    async def add_task_tool(title: str, description: Optional[str] = None) -> Dict:
        """Create a new task for the user."""
        return await add_task.add_task(user_id, title, description)

    @function_tool
    async def list_tasks_tool(status: str = "all") -> List[Dict]:
        """
        List user's tasks.

        Args:
            status: Filter by status - "all", "pending", or "completed"
        """
        return await list_tasks.list_tasks(user_id, status)

    @function_tool
    async def complete_task_tool(task_id: str) -> Dict:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to complete
        """
        return await complete_task.complete_task(user_id, task_id)

    @function_tool
    async def delete_task_tool(task_id: str) -> Dict:
        """
        Delete a task.

        Args:
            task_id: ID of the task to delete
        """
        return await delete_task.delete_task(user_id, task_id)

    @function_tool
    async def update_task_tool(
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Update task title or description.

        Args:
            task_id: ID of the task to update
            title: New task title (optional)
            description: New task description (optional)
        """
        return await update_task.update_task(user_id, task_id, title, description)

    # Return all tools
    return [
        add_task_tool,
        list_tasks_tool,
        complete_task_tool,
        delete_task_tool,
        update_task_tool
    ]


def get_tool_names() -> List[str]:
    """
    Get list of available tool names.

    Returns:
        List of tool names
    """
    return [
        "add_task_tool",
        "list_tasks_tool",
        "complete_task_tool",
        "delete_task_tool",
        "update_task_tool"
    ]
