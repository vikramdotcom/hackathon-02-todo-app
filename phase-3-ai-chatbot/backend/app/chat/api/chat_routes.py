"""Chat API routes for conversational todo management.

This module provides REST API endpoints for the chat functionality,
including message handling with streaming responses and session management.
"""

import json
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.api.deps import get_current_user
from app.chat.services.conversation_manager import get_conversation_manager
from app.chat.services.function_executor import FunctionExecutor
from app.chat.services.llm_service import LLMService
from app.chat.services.phase2_client import Phase2Client
from app.models.user import User

logger = logging.getLogger(__name__)

# Initialize router (no prefix here, it's added in main.py)
router = APIRouter(tags=["chat"])

# Initialize services
phase2_client = Phase2Client(
    base_url=os.getenv("PHASE2_API_BASE_URL", "http://localhost:8000/api/v1")
)
llm_service = LLMService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
    temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
)
function_executor = FunctionExecutor(phase2_client)




@router.get("/health")
async def chat_health_check():
    """Health check endpoint for chat service.
    
    Returns:
        Dictionary with service status and statistics
    """
    try:
        conv_manager = get_conversation_manager()
        stats = conv_manager.get_stats() if hasattr(conv_manager, 'get_stats') else {}
        
        return {
            "status": "healthy",
            "service": "chat",
            "llm_configured": bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your-openai-api-key-here"),
            "phase2_api_url": os.getenv("PHASE2_API_BASE_URL", "http://localhost:8000/api/v1"),
            "session_stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Request/Response Models
class ChatMessageRequest(BaseModel):
    """Request model for sending a chat message."""

    session_id: Optional[str] = Field(
        None,
        description="Session ID (omit for first message)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's message text"
    )


class SessionSummary(BaseModel):
    """Summary of a conversation session."""

    session_id: str
    created_at: str
    last_activity_at: str
    message_count: int
    last_message_preview: Optional[str] = None


@router.post("/message")
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Send a chat message and receive a streaming response.

    This endpoint handles user messages, maintains conversation context,
    calls the LLM for response generation, executes function calls,
    and streams the response back to the client.

    Args:
        request: Chat message request with optional session_id and message
        current_user: Authenticated user from JWT token
        authorization: Authorization header with JWT token

    Returns:
        StreamingResponse with Server-Sent Events format

    Raises:
        HTTPException: If session not found or other errors occur
    """
    # Input validation
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    if len(request.message) > 10000:
        raise HTTPException(
            status_code=400,
            detail="Message is too long (max 10,000 characters)"
        )
    
    
    # Sanitize message (remove control characters except newlines and tabs)
    sanitized_message = "".join(
        char for char in request.message
        if char.isprintable() or char in ["\n", "\t", "\r"]
    )
    request.message = sanitized_message.strip()
    
    try:
        # Extract JWT token from Authorization header
        jwt_token = authorization.replace("Bearer ", "")

        # Get conversation manager
        conv_manager = get_conversation_manager()

        # Get or create session
        if request.session_id:
            session = conv_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(
                    status_code=404,
                    detail="Session not found or expired"
                )
            if session.user_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied to this session"
                )
        else:
            # Create new session
            session_id = conv_manager.create_session(current_user.id)
            session = conv_manager.get_session(session_id)

        # Add user message to session
        session.add_message("user", request.message)

        # Get message history for LLM
        message_history = session.get_message_history()

        # Get recent todos from context for system prompt
        recent_todos = [
            {
                "id": ref.todo_id,
                "title": ref.title,
                "completed": ref.completed
            }
            for ref in session.context.referenced_todos.values()
        ]

        logger.info(
            f"Processing message for user {current_user.id}, "
            f"session {session.session_id}"
        )

        # Define streaming response generator
        async def generate_stream():
            """Generate Server-Sent Events stream."""
            try:
                # Send session_id in first event
                yield f"data: {json.dumps({'type': 'session_id', 'session_id': session.session_id})}\n\n"

                assistant_message_content = ""
                function_calls_made = []

                # Generate response from LLM
                async for chunk in llm_service.generate_response(
                    messages=message_history,
                    user_id=current_user.id,
                    username=current_user.username,
                    recent_todos=recent_todos,
                    stream=True
                ):
                    chunk_type = chunk.get("type")

                    if chunk_type == "token":
                        # Stream text token to client
                        content = chunk.get("content", "")
                        assistant_message_content += content
                        yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

                    elif chunk_type == "function_call":
                        # Execute function call
                        function_name = chunk.get("function_name")
                        arguments = chunk.get("arguments")

                        logger.info(f"Executing function: {function_name}")

                        # Execute function
                        result = await function_executor.execute_function(
                            function_name=function_name,
                            arguments=arguments,
                            jwt_token=jwt_token,
                            context=session.context
                        )

                        function_calls_made.append({
                            "function_name": function_name,
                            "arguments": arguments,
                            "result": result
                        })

                        # Check if function needs confirmation
                        if result.get("needs_confirmation"):
                            # Store pending confirmation in context
                            from datetime import datetime, timedelta
                            from app.chat.models.chat_models import PendingConfirmation

                            session.context.pending_confirmation = PendingConfirmation(
                                operation="delete",
                                target_todo_ids=result.get("todo_ids", []),
                                created_at=datetime.utcnow(),
                                expires_at=datetime.utcnow() + timedelta(minutes=2)
                            )

                            # Send confirmation request to user
                            confirmation_message = result.get("message")
                            assistant_message_content = confirmation_message
                            yield f"data: {json.dumps({'type': 'token', 'content': confirmation_message})}\n\n"

                        elif result.get("success"):
                            # Send todos if present
                            if "todos" in result:
                                todos = result["todos"]
                                if isinstance(todos, list):
                                    for todo in todos:
                                        # Add to context
                                        session.context.add_todo_reference(
                                            todo_id=todo["id"],
                                            title=todo["title"],
                                            completed=todo["completed"]
                                        )
                                        # Stream todo card
                                        yield f"data: {json.dumps({'type': 'todo', 'todo': todo})}\n\n"

                                    # Update last_query_results
                                    session.context.last_query_results = [t["id"] for t in todos]

                            elif "todo" in result:
                                todo = result["todo"]
                                # Add to context
                                session.context.add_todo_reference(
                                    todo_id=todo["id"],
                                    title=todo["title"],
                                    completed=todo["completed"]
                                )
                                # Stream todo card
                                yield f"data: {json.dumps({'type': 'todo', 'todo': todo})}\n\n"

                            # Send success message
                            success_message = result.get("message", "Operation completed successfully")
                            assistant_message_content = success_message
                            yield f"data: {json.dumps({'type': 'token', 'content': success_message})}\n\n"

                        else:
                            # Send error message
                            error_message = result.get("error", "Operation failed")
                            assistant_message_content = f"I encountered an error: {error_message}"
                            yield f"data: {json.dumps({'type': 'token', 'content': assistant_message_content})}\n\n"

                    elif chunk_type == "error":
                        # Send error to client
                        error = chunk.get("error", "Unknown error")
                        yield f"data: {json.dumps({'type': 'error', 'error': error})}\n\n"
                        return

                    elif chunk_type == "done":
                        # Response complete
                        break

                # Add assistant message to session
                if assistant_message_content:
                    session.add_message("assistant", assistant_message_content)

                # Update session in manager
                conv_manager.update_session(session.session_id, session)

                # Send completion event
                yield f"data: {json.dumps({'type': 'done', 'message_id': session.messages[-1].message_id})}\n\n"

            except Exception as e:
                logger.error(f"Error in stream generation: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        # Return streaming response
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "X-Session-Id": session.session_id
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get conversation session details.

    Args:
        session_id: Session identifier
        current_user: Authenticated user from JWT token

    Returns:
        ConversationSession object

    Raises:
        HTTPException: If session not found or access denied
    """
    try:
        conv_manager = get_conversation_manager()
        session = conv_manager.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )

        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this session"
            )

        return session

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation session.

    Args:
        session_id: Session identifier
        current_user: Authenticated user from JWT token

    Returns:
        Success message

    Raises:
        HTTPException: If session not found or access denied
    """
    try:
        conv_manager = get_conversation_manager()
        session = conv_manager.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this session"
            )

        conv_manager.delete_session(session_id)

        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user)
):
    """List all active sessions for the current user.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        Dictionary with sessions list and total count
    """
    try:
        conv_manager = get_conversation_manager()
        sessions = conv_manager.get_user_sessions(current_user.id)

        # Convert to summaries
        summaries = [
            SessionSummary(
                session_id=session.session_id,
                created_at=session.created_at.isoformat(),
                last_activity_at=session.last_activity_at.isoformat(),
                message_count=session.message_count,
                last_message_preview=(
                    session.messages[-1].content[:50] + "..."
                    if session.messages and len(session.messages[-1].content) > 50
                    else session.messages[-1].content if session.messages else None
                )
            )
            for session in sessions
        ]

        return {
            "sessions": summaries,
            "total": len(summaries)
        }

    except Exception as e:
        logger.error(f"Error listing sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )
