"""Chat endpoints for AI assistant conversations."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.engines.meta_learning import MetaLearningEngine
from app.core.error_handlers import handle_errors, log_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message model."""
    id: str
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""
    message: str


class SendMessageResponse(BaseModel):
    """Response model for sending a message."""
    user_message: ChatMessage
    assistant_message: ChatMessage


@router.get("/history", response_model=List[ChatMessage])
@log_request
@handle_errors(default_message="Failed to get chat history")
async def get_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's chat history."""
    # For now, we'll store chat history in a simple table
    # In a real implementation, you'd have a ChatMessage model
    # Since we don't have one yet, let's return an empty list
    # TODO: Create ChatMessage model and table

    logger.info(f"Chat history requested for user {current_user.id}")

    # Placeholder - return empty list until we implement chat storage
    return []


@router.post("/send", response_model=SendMessageResponse)
@log_request
@handle_errors(default_message="Failed to send message")
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get AI response."""
    try:
        # Create user message
        user_message = ChatMessage(
            id=f"user_{datetime.utcnow().timestamp()}",
            role="user",
            content=request.message,
            created_at=datetime.utcnow()
        )

        # Get AI response using meta learning engine
        engine = MetaLearningEngine(db)
        ai_response = await engine.generate_response(
            user_id=str(current_user.id),
            message=request.message
        )

        # Create assistant message
        assistant_message = ChatMessage(
            id=f"assistant_{datetime.utcnow().timestamp()}",
            role="assistant",
            content=ai_response,
            created_at=datetime.utcnow()
        )

        # TODO: Store messages in database

        logger.info(f"Message sent by user {current_user.id}: {len(request.message)} chars")

        return SendMessageResponse(
            user_message=user_message,
            assistant_message=assistant_message
        )

    except Exception as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )