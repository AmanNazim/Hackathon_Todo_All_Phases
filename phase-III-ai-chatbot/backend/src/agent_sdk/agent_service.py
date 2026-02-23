"""
Agent Service

Creates and configures the main task management agent using OpenAI Agents SDK with LiteLLM.
"""

from agents import Agent, ModelSettings, SQLiteSession
from agents.extensions.models.litellm_model import LitellmModel
from typing import List, Optional
from src.config.settings import settings
from .guardrails import input_validation_guardrail, output_quality_guardrail


# Comprehensive instructions for the task management agent
TASK_AGENT_INSTRUCTIONS = """You are a helpful task management assistant. Your role is to help users manage their tasks through natural language conversation.

**Your Capabilities:**
- Create new tasks with titles and descriptions
- List tasks (all, pending, or completed)
- Mark tasks as complete
- Update task details (title or description)
- Delete tasks

**Guidelines:**
1. Be conversational and friendly in your responses
2. Understand natural language commands and extract task information
3. When creating tasks, extract clear titles and descriptions from user input
4. When listing tasks, present them in a clear, organized format
5. Confirm actions after completing them (e.g., "I've added 'Buy groceries' to your tasks")
6. If a request is ambiguous, ask clarifying questions
7. Keep responses concise but helpful

**Examples:**
- "Add a task to buy milk" → Create task with title "Buy milk"
- "Show my tasks" → List all pending tasks
- "I finished the groceries" → Mark the groceries task as complete
- "Change the meeting task to team meeting" → Update task title
- "Delete the old task" → Delete the specified task

Always be helpful, accurate, and responsive to user needs."""


def create_task_agent(
    tools: List,
    input_guardrails: Optional[List] = None,
    output_guardrails: Optional[List] = None
) -> Agent:
    """
    Create the main task management agent with LiteLLM.

    Args:
        tools: List of function tools for task operations
        input_guardrails: Optional list of input guardrails (defaults to built-in)
        output_guardrails: Optional list of output guardrails (defaults to built-in)

    Returns:
        Configured Agent instance
    """
    # Use default guardrails if not provided
    if input_guardrails is None:
        input_guardrails = [input_validation_guardrail]

    if output_guardrails is None:
        output_guardrails = [output_quality_guardrail]

    # Get model configuration
    model_name, api_key = settings.get_model_config()

    # Create LiteLLM model
    litellm_model = LitellmModel(
        model=model_name,
        api_key=api_key
    )

    # Create agent with LiteLLM configuration
    agent = Agent(
        name="Task Management Agent",
        instructions=TASK_AGENT_INSTRUCTIONS,
        model=litellm_model,
        tools=tools,
        model_settings=ModelSettings(
            temperature=0.7,
            include_usage=True
        ),
        input_guardrails=input_guardrails,
        output_guardrails=output_guardrails,
        max_iterations=10
    )

    return agent


def get_agent_config() -> dict:
    """
    Get agent configuration from settings.

    Returns:
        Dictionary with agent configuration
    """
    model_name, _ = settings.get_model_config()
    return {
        "model": model_name,
        "temperature": 0.7,
        "max_iterations": 10,
        "include_usage": True,
        "provider": "litellm"
    }
