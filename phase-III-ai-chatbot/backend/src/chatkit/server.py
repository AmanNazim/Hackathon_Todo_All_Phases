"""
ChatKit Server Implementation

ChatKitServer implementation that bridges Agent SDK with ChatKit interface.
"""

from typing import AsyncIterator, Dict, Any, Optional
from uuid import UUID
from src.agent_sdk.agent_service import create_task_agent
from src.agent_sdk.session_service import get_or_create_session
from src.agent_sdk.tool_adapter import create_function_tools
from src.agent_sdk.runner_service import run_agent_streamed
from .events import convert_to_chatkit_event, convert_text_event
from .actions import (
    handle_complete_task,
    handle_delete_task,
    handle_update_task,
    handle_create_task,
    handle_list_tasks
)
from .widgets import build_task_list_widget


class TaskChatKitServer:
    """
    ChatKit server implementation for task management.

    This class bridges the Agent SDK backend with ChatKit's interface,
    handling message generation, widget actions, and streaming responses.
    """

    async def generate(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[UUID] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate AI response using Agent SDK.

        Args:
            user_id: User identifier
            message: User's message
            conversation_id: Optional conversation ID

        Yields:
            ChatKit-compatible events
        """
        try:
            # Get or create session
            session, conv_id = get_or_create_session(conversation_id)

            # Create tools with user_id context
            tools = create_function_tools(user_id)

            # Create agent
            agent = create_task_agent(tools)

            # Stream agent responses
            async for event in run_agent_streamed(agent, message, session, user_id):
                # Convert to ChatKit event format
                chatkit_event = convert_to_chatkit_event(event)
                yield chatkit_event

        except Exception as e:
            # Yield error event
            yield {
                "type": "error",
                "error": str(e),
                "message": "Failed to generate response. Please try again."
            }

    async def handle_action(
        self,
        action_type: str,
        payload: Dict[str, Any],
        user_id: str,
        conversation_id: Optional[UUID] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Handle widget action.

        Args:
            action_type: Type of action (complete_task, delete_task, etc.)
            payload: Action payload data
            user_id: User identifier
            conversation_id: Optional conversation ID

        Yields:
            ChatKit-compatible events
        """
        try:
            # Handle different action types
            if action_type == "complete_task":
                result = await handle_complete_task(payload.get("task_id"), user_id)
            elif action_type == "delete_task":
                result = await handle_delete_task(payload.get("task_id"), user_id)
            elif action_type == "update_task":
                result = await handle_update_task(payload, user_id)
            elif action_type == "create_task":
                result = await handle_create_task(payload, user_id)
            elif action_type == "list_tasks":
                result = await handle_list_tasks(payload.get("status", "all"), user_id)
            else:
                result = {
                    "success": False,
                    "message": f"Unknown action type: {action_type}"
                }

            # Send result message
            if result.get("success"):
                yield convert_text_event(result.get("message", "Action completed successfully"))
            else:
                yield {
                    "type": "error",
                    "error": "action_failed",
                    "message": result.get("message", "Action failed")
                }

            # Generate AI response about the action
            action_message = f"User performed action: {action_type}"
            async for event in self.generate(user_id, action_message, conversation_id):
                yield event

        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "message": "Failed to handle action. Please try again."
            }

    async def get_tasks_widget(self, user_id: str, status: str = "all") -> Dict[str, Any]:
        """
        Get tasks widget for display.

        Args:
            user_id: User identifier
            status: Filter by status (all, pending, completed)

        Returns:
            ChatKit widget dictionary
        """
        try:
            result = await handle_list_tasks(status, user_id)
            if result.get("success"):
                tasks = result.get("tasks", [])
                return build_task_list_widget(tasks)
            else:
                return {
                    "type": "Card",
                    "children": [
                        {
                            "type": "Text",
                            "value": "Failed to load tasks",
                            "color": "error"
                        }
                    ]
                }
        except Exception as e:
            return {
                "type": "Card",
                "children": [
                    {
                        "type": "Text",
                        "value": f"Error: {str(e)}",
                        "color": "error"
                    }
                ]
            }
