"""
MCP Server Entry Point

Simple runner script that starts the FastMCP server from src/mcp/server.py
"""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import and run the MCP server
from src.mcp.server import mcp

if __name__ == "__main__":
    print("Starting Task Management MCP Server...", file=sys.stderr)
    print("Available tools: add_task, list_tasks, complete_task, delete_task, update_task", file=sys.stderr)
    mcp.run()

