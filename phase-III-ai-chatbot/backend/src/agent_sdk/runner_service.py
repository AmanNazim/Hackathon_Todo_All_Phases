"""
Runner Service

Executes agents using OpenAI Agents SDK Runner.
"""

from agents import Agent, Runner, SQLiteSession
from agents.exceptions import MaxTurnsExceeded
from typing import AsyncIterator, Dict, Any


async def run_agent(
    agent: Agent,
    message: str,
    session: SQLiteSession,
    user_id: str
) -> str:
    """
    Run agent and return final output.

    Args:
        agent: Configured Agent instance
        message: User message to process
        session: SQLiteSession for conversation history
        user_id: User identifier for context

    Returns:
        Final output string from agent

    Raises:
        RuntimeError: If agent execution fails
    """
    try:
        # Run agent with context variables
        result = await Runner.run(
            agent,
            message,
            session=session,
            context_variables={"user_id": user_id}
        )

        # Return final output
        return result.final_output

    except MaxTurnsExceeded:
        # Handle max turns exceeded gracefully
        return (
            "I apologize, but I've reached the maximum number of steps for this request. "
            "Please try rephrasing your request or breaking it into smaller parts."
        )

    except Exception as e:
        # Log error and raise with context
        error_msg = f"Agent execution failed: {str(e)}"
        raise RuntimeError(error_msg)


async def run_agent_streamed(
    agent: Agent,
    message: str,
    session: SQLiteSession,
    user_id: str
) -> AsyncIterator[Any]:
    """
    Run agent with streaming and yield events.

    Args:
        agent: Configured Agent instance
        message: User message to process
        session: SQLiteSession for conversation history
        user_id: User identifier for context

    Yields:
        Stream events from agent execution
    """
    try:
        # Run agent with streaming
        async for event in Runner.run_streamed(
            agent,
            message,
            session=session,
            context_variables={"user_id": user_id}
        ):
            yield event

    except MaxTurnsExceeded:
        # Yield error event
        yield {
            "type": "error",
            "error": "Maximum turns exceeded",
            "message": "Please try rephrasing your request."
        }

    except Exception as e:
        # Yield error event
        yield {
            "type": "error",
            "error": str(e),
            "message": "An error occurred during processing."
        }


async def run_agent_with_retry(
    agent: Agent,
    message: str,
    session: SQLiteSession,
    user_id: str,
    max_retries: int = 2
) -> str:
    """
    Run agent with automatic retry on failure.

    Args:
        agent: Configured Agent instance
        message: User message to process
        session: SQLiteSession for conversation history
        user_id: User identifier for context
        max_retries: Maximum number of retry attempts

    Returns:
        Final output string from agent

    Raises:
        RuntimeError: If all retry attempts fail
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            return await run_agent(agent, message, session, user_id)
        except RuntimeError as e:
            last_error = e
            if attempt < max_retries:
                # Wait before retry (could add exponential backoff)
                continue

    # All retries failed
    raise RuntimeError(f"Agent execution failed after {max_retries} retries: {last_error}")
