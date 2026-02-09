"""Agent package for OpenAI Agent configuration"""

from .config import SYSTEM_PROMPT
from .runner import run_agent

__all__ = ["SYSTEM_PROMPT", "run_agent"]
