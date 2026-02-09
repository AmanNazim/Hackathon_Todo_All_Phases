"""MCP server for registering and managing tools"""

from src.mcp.tools.add_task import add_task, add_task_schema
from src.mcp.tools.list_tasks import list_tasks, list_tasks_schema
from src.mcp.tools.complete_task import complete_task, complete_task_schema
from src.mcp.tools.delete_task import delete_task, delete_task_schema
from src.mcp.tools.update_task import update_task, update_task_schema


# MCP tools registry
MCP_TOOLS = [
    {"function": add_task, "schema": add_task_schema},
    {"function": list_tasks, "schema": list_tasks_schema},
    {"function": complete_task, "schema": complete_task_schema},
    {"function": delete_task, "schema": delete_task_schema},
    {"function": update_task, "schema": update_task_schema},
]


def get_mcp_tools():
    """
    Get all MCP tool functions for agent registration.

    Returns:
        List of tool functions
    """
    return [tool["function"] for tool in MCP_TOOLS]


def get_mcp_schemas():
    """
    Get all MCP tool schemas for documentation.

    Returns:
        List of tool schemas
    """
    return [tool["schema"] for tool in MCP_TOOLS]


def get_tool_by_name(name: str):
    """
    Get a specific tool by name.

    Args:
        name: Tool name

    Returns:
        Tool function or None if not found
    """
    for tool in MCP_TOOLS:
        if tool["schema"]["name"] == name:
            return tool["function"]
    return None
