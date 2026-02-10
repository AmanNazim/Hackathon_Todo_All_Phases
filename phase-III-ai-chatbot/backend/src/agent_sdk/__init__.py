"""
Agent SDK Integration Module

This module provides OpenAI Agents SDK integration for the Phase III AI Chatbot.
It includes agent configuration, session management, tool adapters, guardrails,
and runner services.

Import directly from submodules to avoid circular imports:
    from src.agent_sdk.agent_service import create_task_agent
    from src.agent_sdk.tool_adapter import create_function_tools
    from src.agent_sdk.session_service import get_or_create_session
    from src.agent_sdk.runner_service import run_agent, run_agent_streamed
"""

# Note: Imports removed to avoid circular dependency issues
# Import directly from submodules instead

__all__ = [
    "create_task_agent",
    "get_or_create_session",
    "create_function_tools",
    "run_agent",
    "run_agent_streamed",
]

