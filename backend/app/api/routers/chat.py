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
from app.models.training import ChatMessage as ChatMessageModel, UserProgress
from app.engines.meta_learning import MetaLearningEngine
from app.core.error_handlers import handle_errors, log_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message model."""
    id: str
    role: str  # "user" or "assistant"
    content: str
    created_at: str

    class Config:
        from_attributes = True


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
    stmt = select(ChatMessageModel).where(
        ChatMessageModel.user_id == current_user.id
    ).order_by(ChatMessageModel.created_at.desc()).limit(limit)
    
    result = await db.execute(stmt)
    messages = result.scalars().all()

    # Reverse to get chronological order
    messages = list(reversed(messages))

    logger.info(f"Retrieved {len(messages)} chat messages for user {current_user.id}")

    return [
        ChatMessage(
            id=str(msg.id),
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at.isoformat(),
        )
        for msg in messages
    ]


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
        # Store user message
        user_msg_db = ChatMessageModel(
            user_id=current_user.id,
            role="user",
            content=request.message,
        )
        db.add(user_msg_db)
        await db.flush()

        # Get AI response using meta learning engine
        engine = MetaLearningEngine(db)
        ai_response = await engine.generate_response(
            user_id=str(current_user.id),
            message=request.message
        )

        # Store assistant message
        assistant_msg_db = ChatMessageModel(
            user_id=current_user.id,
            role="assistant",
            content=ai_response,
        )
        db.add(assistant_msg_db)

        # Update chat message count
        progress_stmt = select(UserProgress).where(UserProgress.user_id == current_user.id)
        progress_result = await db.execute(progress_stmt)
        progress = progress_result.scalar_one_or_none()

        if not progress:
            progress = UserProgress(user_id=current_user.id)
            db.add(progress)

        progress.total_chat_messages += 1

        await db.commit()
        await db.refresh(user_msg_db)
        await db.refresh(assistant_msg_db)

        logger.info(f"Message sent by user {current_user.id}: {len(request.message)} chars")

        return SendMessageResponse(
            user_message=ChatMessage(
                id=str(user_msg_db.id),
                role=user_msg_db.role,
                content=user_msg_db.content,
                created_at=user_msg_db.created_at.isoformat(),
            ),
            assistant_message=ChatMessage(
                id=str(assistant_msg_db.id),
                role=assistant_msg_db.role,
                content=assistant_msg_db.content,
                created_at=assistant_msg_db.created_at.isoformat(),
            ),
        )

    except Exception as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )