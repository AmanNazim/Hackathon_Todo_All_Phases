"""
Chat Service

Handles chat interactions using OpenAI Agents SDK.
"""

from typing import Dict, Optional
from uuid import UUID
from datetime import datetime
from src.agent_sdk.agent_service import create_task_agent
from src.agent_sdk.session_service import get_or_create_session
from src.agent_sdk.tool_adapter import create_function_tools
from src.agent_sdk.runner_service import run_agent


class ChatService:
    """Service for handling chat interactions with Agent SDK"""

    @staticmethod
    async def handle_chat(
        user_id: str,
        message: str,
        conversation_id: Optional[UUID] = None
    ) -> Dict:
        """
        Handle a chat message using Agent SDK.

        Args:
            user_id: User identifier
            message: User's message
            conversation_id: Optional conversation ID for continuation

        Returns:
            Dictionary with conversation_id, response, and created_at

        Raises:
            ValueError: If conversation not found or access denied
            RuntimeError: If agent execution fails
        """
        try:
            # Get or create session
            session, conv_id = get_or_create_session(conversation_id)

            # Create tools with user_id context
            tools = create_function_tools(user_id)

            # Create agent
            agent = create_task_agent(tools)

            # Run agent
            response = await run_agent(agent, message, session, user_id)

            # Return result
            return {
                "conversation_id": str(conv_id),
                "response": response,
                "created_at": datetime.utcnow().isoformat()
            }

        except RuntimeError as e:
            # Agent execution error
            raise RuntimeError(f"Failed to process message: {str(e)}")

        except Exception as e:
            # Unexpected error
            raise RuntimeError(f"Unexpected error in chat service: {str(e)}")
