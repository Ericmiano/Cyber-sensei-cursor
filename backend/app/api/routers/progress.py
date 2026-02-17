"""User progress endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.models.training import UserProgress as TrainingProgress, ActivityLog, LessonCompletion
from app.core.error_handlers import handle_errors, log_request

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/progress", tags=["progress"])


# Pydantic models
class ProgressResponse(BaseModel):
    xp: int
    level: int
    current_streak: int
    longest_streak: int
    last_active_date: Optional[str]
    total_quizzes_passed: int
    total_exercises_completed: int
    total_chat_messages: int
    lessons_completed: int

    class Config:
        from_attributes = True


class ActivityLogResponse(BaseModel):
    id: str
    activity_type: str
    title: str
    description: Optional[str]
    xp_earned: Optional[int]
    created_at: str

    class Config:
        from_attributes = True


class AddXPRequest(BaseModel):
    amount: int
    reason: str


class AddXPResponse(BaseModel):
    message: str
    xp_earned: int
    new_xp: int
    new_level: int
    level_up: bool


@router.get("/", response_model=ProgressResponse)
@log_request
@handle_errors(default_message="Failed to get progress")
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user progress."""
    # Get or create progress
    stmt = select(TrainingProgress).where(TrainingProgress.user_id == current_user.id)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        # Create default progress
        progress = TrainingProgress(user_id=current_user.id)
        db.add(progress)
        await db.commit()
        await db.refresh(progress)

    # Get lessons completed count
    lessons_stmt = select(func.count(LessonCompletion.id)).where(
        LessonCompletion.user_id == current_user.id
    )
    lessons_result = await db.execute(lessons_stmt)
    lessons_completed = lessons_result.scalar() or 0

    return ProgressResponse(
        xp=progress.xp,
        level=progress.level,
        current_streak=progress.current_streak,
        longest_streak=progress.longest_streak,
        last_active_date=progress.last_active_date.isoformat() if progress.last_active_date else None,
        total_quizzes_passed=progress.total_quizzes_passed,
        total_exercises_completed=progress.total_exercises_completed,
        total_chat_messages=progress.total_chat_messages,
        lessons_completed=lessons_completed,
    )


@router.post("/xp", response_model=AddXPResponse)
@log_request
@handle_errors(default_message="Failed to add XP")
async def add_xp(
    request: AddXPRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add XP to user."""
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="XP amount must be positive"
        )

    # Get or create progress
    stmt = select(TrainingProgress).where(TrainingProgress.user_id == current_user.id)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        progress = TrainingProgress(user_id=current_user.id)
        db.add(progress)

    old_level = progress.level
    progress.xp += request.amount
    progress.level = (progress.xp // 500) + 1  # 500 XP per level
    level_up = progress.level > old_level

    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        activity_type="xp",
        title=f"+{request.amount} XP",
        description=request.reason,
        xp_earned=request.amount,
    )
    db.add(activity)

    await db.commit()
    await db.refresh(progress)

    logger.info(f"Added {request.amount} XP to user {current_user.id}, new total: {progress.xp}")

    return AddXPResponse(
        message="XP added successfully",
        xp_earned=request.amount,
        new_xp=progress.xp,
        new_level=progress.level,
        level_up=level_up,
    )


@router.post("/streak")
@log_request
@handle_errors(default_message="Failed to update streak")
async def update_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user's daily streak."""
    # Get or create progress
    stmt = select(TrainingProgress).where(TrainingProgress.user_id == current_user.id)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        progress = TrainingProgress(user_id=current_user.id)
        db.add(progress)

    today = date.today()
    yesterday = date.fromordinal(today.toordinal() - 1)

    if progress.last_active_date == today:
        # Already updated today
        return {
            "message": "Streak already updated today",
            "current_streak": progress.current_streak,
            "longest_streak": progress.longest_streak,
        }

    if progress.last_active_date == yesterday:
        # Continue streak
        progress.current_streak += 1
    elif progress.last_active_date != today:
        # Streak broken, start new
        progress.current_streak = 1

    progress.longest_streak = max(progress.longest_streak, progress.current_streak)
    progress.last_active_date = today

    await db.commit()
    await db.refresh(progress)

    logger.info(f"Updated streak for user {current_user.id}: {progress.current_streak} days")

    return {
        "message": "Streak updated successfully",
        "current_streak": progress.current_streak,
        "longest_streak": progress.longest_streak,
    }


@router.post("/quiz-complete")
@log_request
@handle_errors(default_message="Failed to record quiz completion")
async def quiz_complete(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record quiz completion."""
    # Get or create progress
    stmt = select(TrainingProgress).where(TrainingProgress.user_id == current_user.id)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        progress = TrainingProgress(user_id=current_user.id)
        db.add(progress)

    progress.total_quizzes_passed += 1

    await db.commit()

    logger.info(f"Quiz completed by user {current_user.id}")

    return {
        "message": "Quiz completion recorded",
        "total_quizzes_passed": progress.total_quizzes_passed,
    }


@router.post("/exercise-complete")
@log_request
@handle_errors(default_message="Failed to record exercise completion")
async def exercise_complete(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record exercise completion."""
    # Get or create progress
    stmt = select(TrainingProgress).where(TrainingProgress.user_id == current_user.id)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        progress = TrainingProgress(user_id=current_user.id)
        db.add(progress)

    progress.total_exercises_completed += 1

    await db.commit()

    logger.info(f"Exercise completed by user {current_user.id}")

    return {
        "message": "Exercise completion recorded",
        "total_exercises_completed": progress.total_exercises_completed,
    }


@router.post("/chat-message")
@log_request
@handle_errors(default_message="Failed to record chat message")
async def chat_message(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record chat message."""
    # Get or create progress
    stmt = select(TrainingProgress).where(TrainingProgress.user_id == current_user.id)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        progress = TrainingProgress(user_id=current_user.id)
        db.add(progress)

    progress.total_chat_messages += 1

    await db.commit()

    return {
        "message": "Chat message recorded",
        "total_chat_messages": progress.total_chat_messages,
    }


@router.get("/activity", response_model=List[ActivityLogResponse])
@log_request
@handle_errors(default_message="Failed to get activity log")
async def get_activity_log(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's activity log."""
    stmt = select(ActivityLog).where(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(limit)
    
    result = await db.execute(stmt)
    activities = result.scalars().all()

    return [
        ActivityLogResponse(
            id=str(activity.id),
            activity_type=activity.activity_type,
            title=activity.title,
            description=activity.description,
            xp_earned=activity.xp_earned,
            created_at=activity.created_at.isoformat(),
        )
        for activity in activities
    ]
