"""MCP Tools for Task Management using FastMCP"""

from src.mcp.tools.add_task import register_add_task
from src.mcp.tools.list_tasks import register_list_tasks
from src.mcp.tools.complete_task import register_complete_task
from src.mcp.tools.delete_task import register_delete_task
from src.mcp.tools.update_task import register_update_task

__all__ = [
    "register_add_task",
    "register_list_tasks",
    "register_complete_task",
    "register_delete_task",
    "register_update_task",
]

