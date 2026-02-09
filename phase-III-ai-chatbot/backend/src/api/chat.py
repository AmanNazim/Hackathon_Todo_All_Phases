"""Chat API endpoint"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService
from src.api.dependencies import get_current_user
from src.agent_sdk import (
    create_task_agent,
    get_or_create_session,
    create_function_tools,
    run_agent_streamed
)
from datetime import datetime
import json

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Chat endpoint for natural language task management.

    This endpoint accepts a user message and optional conversation ID,
    processes it through the AI agent with MCP tools, and returns
    the AI's response.

    Requires authentication via Bearer token.

    Args:
        request: Chat request with optional conversation_id and message
        user_id: Authenticated user ID (injected from token)

    Returns:
        Chat response with conversation_id, AI response, and timestamp

    Raises:
        HTTPException: 401 if unauthorized, 404 if conversation not found, 500 for server errors
    """
    try:
        # Handle chat through service with authenticated user
        result = await ChatService.handle_chat(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )

        return ChatResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            created_at=result["created_at"]
        )

    except ValueError as e:
        # Conversation not found or access denied
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Internal server error
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again."
        )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Streaming chat endpoint for real-time responses.

    This endpoint streams AI responses as Server-Sent Events (SSE),
    allowing clients to receive partial responses as they're generated.

    Requires authentication via Bearer token.

    Args:
        request: Chat request with optional conversation_id and message
        user_id: Authenticated user ID (injected from token)

    Returns:
        StreamingResponse with text/event-stream media type

    Raises:
        HTTPException: 401 if unauthorized, 404 if conversation not found
    """
    async def event_generator():
        """Generate SSE events from agent stream"""
        try:
            # Get or create session
            session, conv_id = get_or_create_session(request.conversation_id)

            # Create tools with user_id context
            tools = create_function_tools(user_id)

            # Create agent
            agent = create_task_agent(tools)

            # Stream agent responses
            async for event in run_agent_streamed(agent, request.message, session, user_id):
                # Handle different event types
                if hasattr(event, 'type') and event.type == 'error':
                    # Error event
                    yield f"event: error\n"
                    yield f"data: {json.dumps({'error': event.get('error', 'Unknown error')})}\n\n"
                    break

                elif hasattr(event, 'text') and event.text:
                    # Text delta event
                    yield f"event: text\n"
                    yield f"data: {json.dumps({'text': event.text})}\n\n"

                elif hasattr(event, 'tool_name'):
                    # Tool call event
                    yield f"event: tool_call\n"
                    yield f"data: {json.dumps({'tool': event.tool_name, 'status': 'running'})}\n\n"

            # Send completion event
            yield f"event: complete\n"
            yield f"data: {json.dumps({'conversation_id': str(conv_id), 'created_at': datetime.utcnow().isoformat()})}\n\n"

        except ValueError as e:
            # Conversation not found or access denied
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        except Exception as e:
            # Internal server error
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': 'Internal server error'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
