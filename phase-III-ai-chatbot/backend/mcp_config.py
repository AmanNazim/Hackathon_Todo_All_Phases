"""
Configuration for MCP Server

Handles logging configuration and environment setup.
"""

import sys
import logging
from pathlib import Path


def setup_logging(level: str = "INFO"):
    """
    Configure logging to stderr only (STDIO constraint).

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


# MCP Server Configuration
MCP_SERVER_NAME = "Task Management Server"
MCP_SERVER_VERSION = "1.0.0"

# Tool Configuration
TOOL_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
