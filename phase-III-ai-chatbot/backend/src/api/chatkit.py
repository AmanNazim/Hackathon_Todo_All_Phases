"""ChatKit API endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from src.api.dependencies import get_current_user
from src.chatkit.server import TaskChatKitServer
import json

router = APIRouter()
chatkit_server = TaskChatKitServer()


class GenerateRequest(BaseModel):
    """Request model for generate endpoint"""
    message: str
    conversation_id: Optional[UUID] = None


class ActionRequest(BaseModel):
    """Request model for action endpoint"""
    type: str
    payload: Dict[str, Any]
    conversation_id: Optional[UUID] = None


@router.post("/chatkit/generate")
async def generate(
    request: GenerateRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Generate AI response with streaming.

    This endpoint streams ChatKit-compatible events for real-time response display.
    """
    async def event_generator():
        try:
            async for event in chatkit_server.generate(
                user_id=user_id,
                message=request.message,
                conversation_id=request.conversation_id
            ):
                # Send as Server-Sent Event
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            error_event = {
                "type": "error",
                "error": str(e),
                "message": "Generation failed"
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chatkit/action")
async def action(
    request: ActionRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Handle widget action with streaming response.

    This endpoint handles actions from ChatKit widgets and streams the response.
    """
    async def event_generator():
        try:
            async for event in chatkit_server.handle_action(
                action_type=request.type,
                payload=request.payload,
                user_id=user_id,
                conversation_id=request.conversation_id
            ):
                # Send as Server-Sent Event
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            error_event = {
                "type": "error",
                "error": str(e),
                "message": "Action failed"
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/chatkit/tasks")
async def get_tasks(
    status: str = "all",
    user_id: str = Depends(get_current_user)
):
    """
    Get tasks widget.

    Returns a ChatKit widget displaying the user's tasks.
    """
    try:
        widget = await chatkit_server.get_tasks_widget(user_id, status)
        return {"widget": widget}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tasks: {str(e)}"
        )
