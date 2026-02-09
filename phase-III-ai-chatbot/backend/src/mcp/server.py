"""
MCP Server for Task Management Tools using FastMCP

This server exposes task management capabilities to AI agents through
the Model Context Protocol.
"""

import sys
import logging
from fastmcp import FastMCP

# Configure logging to stderr only (STDIO constraint)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Task Management Server")

# Import and register tools
from src.mcp.tools.add_task import register_add_task
from src.mcp.tools.list_tasks import register_list_tasks
from src.mcp.tools.complete_task import register_complete_task
from src.mcp.tools.delete_task import register_delete_task
from src.mcp.tools.update_task import register_update_task

# Register all tools with the MCP server
register_add_task(mcp)
register_list_tasks(mcp)
register_complete_task(mcp)
register_delete_task(mcp)
register_update_task(mcp)


def get_mcp_server():
    """
    Get the FastMCP server instance.

    Returns:
        FastMCP server instance
    """
    return mcp


if __name__ == "__main__":
    logger.info("Starting Task Management MCP Server")
    logger.info("Available tools: add_task, list_tasks, complete_task, delete_task, update_task")

    # Run the MCP server with STDIO transport
    mcp.run()

