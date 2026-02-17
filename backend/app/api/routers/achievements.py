"""Achievements endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.models.training import Achievement, UserAchievement, UserProgress as TrainingProgress, ActivityLog
from app.core.error_handlers import handle_errors, log_request

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/achievements", tags=["achievements"])


# Pydantic models
class AchievementResponse(BaseModel):
    id: str
    achievement_key: str
    title: str
    description: Optional[str]
    icon: Optional[str]
    requirement_type: Optional[str]
    requirement_value: Optional[int]
    xp_reward: int
    earned: bool
    earned_at: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AchievementResponse])
@log_request
@handle_errors(default_message="Failed to get achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all achievements with earned status."""
    # Get all achievements
    stmt = select(Achievement)
    result = await db.execute(stmt)
    achievements = result.scalars().all()

    # Get user's earned achievements
    user_achievements_stmt = select(UserAchievement).where(
        UserAchievement.user_id == current_user.id
    )
    user_achievements_result = await db.execute(user_achievements_stmt)
    user_achievements = user_achievements_result.scalars().all()

    # Create map of earned achievements
    earned_map = {
        str(ua.achievement_id): ua.earned_at
        for ua in user_achievements
    }

    # Build response
    response = []
    for achievement in achievements:
        achievement_id = str(achievement.id)
        earned_at = earned_map.get(achievement_id)

        response.append(AchievementResponse(
            id=achievement_id,
            achievement_key=achievement.achievement_key,
            title=achievement.title,
            description=achievement.description,
            icon=achievement.icon,
            requirement_type=achievement.requirement_type,
            requirement_value=achievement.requirement_value,
            xp_reward=achievement.xp_reward or 0,
            earned=earned_at is not None,
            earned_at=earned_at.isoformat() if earned_at else None,
        ))

    logger.info(f"Retrieved {len(response)} achievements for user {current_user.id}")
    return response


class UnlockAchievementResponse(BaseModel):
    message: str
    achievement: AchievementResponse
    xp_earned: int


@router.post("/{achievement_id}/unlock", response_model=UnlockAchievementResponse)
@log_request
@handle_errors(default_message="Failed to unlock achievement")
async def unlock_achievement(
    achievement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unlock an achievement."""
    # Get achievement
    achievement = await db.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Achievement not found"
        )

    # Check if already unlocked
    check_stmt = select(UserAchievement).where(
        UserAchievement.user_id == current_user.id,
        UserAchievement.achievement_id == achievement_id
    )
    result = await db.execute(check_stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Achievement already unlocked"
        )

    # Create user achievement
    user_achievement = UserAchievement(
        user_id=current_user.id,
        achievement_id=achievement_id,
    )
    db.add(user_achievement)

    # Award XP if applicable
    xp_earned = achievement.xp_reward or 0
    if xp_earned > 0:
        # Get or create progress
        progress_stmt = select(TrainingProgress).where(TrainingProgress.user_id == current_user.id)
        progress_result = await db.execute(progress_stmt)
        progress = progress_result.scalar_one_or_none()

        if not progress:
            progress = TrainingProgress(user_id=current_user.id)
            db.add(progress)

        progress.xp += xp_earned
        progress.level = (progress.xp // 500) + 1

    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        activity_type="achievement",
        title=f"Achievement Unlocked: {achievement.title}",
        description=achievement.description,
        xp_earned=xp_earned,
    )
    db.add(activity)

    await db.commit()
    await db.refresh(user_achievement)

    logger.info(f"Achievement {achievement_id} unlocked by user {current_user.id}")

    return UnlockAchievementResponse(
        message="Achievement unlocked successfully",
        achievement=AchievementResponse(
            id=str(achievement.id),
            achievement_key=achievement.achievement_key,
            title=achievement.title,
            description=achievement.description,
            icon=achievement.icon,
            requirement_type=achievement.requirement_type,
            requirement_value=achievement.requirement_value,
            xp_reward=xp_earned,
            earned=True,
            earned_at=user_achievement.earned_at.isoformat(),
        ),
        xp_earned=xp_earned,
    )
