"""Training modules and lessons endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.models.training import TrainingModule, Lesson, LessonCompletion
from app.core.error_handlers import handle_errors, log_request

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/training", tags=["training"])


# Pydantic models
class ModuleResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    difficulty: Optional[str]
    icon: Optional[str]
    order_index: Optional[int]
    duration_minutes: Optional[int]
    total_lessons: int
    completed_lessons: int
    status: str  # 'locked', 'in-progress', 'completed'

    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    id: str
    module_id: str
    title: str
    content: Optional[str]
    order_index: Optional[int]
    duration_minutes: Optional[int]
    xp_reward: int
    difficulty: Optional[str]
    completed: bool
    completed_at: Optional[str]
    quiz_score: Optional[int]

    class Config:
        from_attributes = True


@router.get("/modules", response_model=List[ModuleResponse])
@log_request
@handle_errors(default_message="Failed to get training modules")
async def get_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all training modules with user progress."""
    # Get all modules
    stmt = select(TrainingModule).order_by(TrainingModule.order_index)
    result = await db.execute(stmt)
    modules = result.scalars().all()

    # Get user's completed lessons
    completion_stmt = select(LessonCompletion).where(
        LessonCompletion.user_id == current_user.id
    )
    completion_result = await db.execute(completion_stmt)
    completions = completion_result.scalars().all()
    
    # Create a map of module_id -> completed_count
    completion_map = {}
    for completion in completions:
        module_id = str(completion.module_id)
        completion_map[module_id] = completion_map.get(module_id, 0) + 1

    # Build response
    response = []
    for module in modules:
        module_id = str(module.id)
        completed_lessons = completion_map.get(module_id, 0)
        total_lessons = module.total_lessons or 0
        
        # Determine status
        if completed_lessons == 0:
            status = "locked" if module.order_index and module.order_index > 1 else "in-progress"
        elif completed_lessons >= total_lessons:
            status = "completed"
        else:
            status = "in-progress"

        response.append(ModuleResponse(
            id=module_id,
            title=module.title,
            description=module.description,
            category=module.category,
            difficulty=module.difficulty,
            icon=module.icon,
            order_index=module.order_index,
            duration_minutes=module.duration_minutes,
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            status=status,
        ))

    logger.info(f"Retrieved {len(response)} modules for user {current_user.id}")
    return response


@router.get("/modules/{module_id}", response_model=ModuleResponse)
@log_request
@handle_errors(default_message="Failed to get module")
async def get_module(
    module_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get module details."""
    # Get module
    module = await db.get(TrainingModule, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    # Get completed lessons count
    completion_stmt = select(func.count(LessonCompletion.id)).where(
        LessonCompletion.user_id == current_user.id,
        LessonCompletion.module_id == module_id
    )
    result = await db.execute(completion_stmt)
    completed_lessons = result.scalar() or 0

    # Determine status
    total_lessons = module.total_lessons or 0
    if completed_lessons == 0:
        status = "in-progress"
    elif completed_lessons >= total_lessons:
        status = "completed"
    else:
        status = "in-progress"

    return ModuleResponse(
        id=str(module.id),
        title=module.title,
        description=module.description,
        category=module.category,
        difficulty=module.difficulty,
        icon=module.icon,
        order_index=module.order_index,
        duration_minutes=module.duration_minutes,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        status=status,
    )


@router.get("/modules/{module_id}/lessons", response_model=List[LessonResponse])
@log_request
@handle_errors(default_message="Failed to get lessons")
async def get_module_lessons(
    module_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all lessons for a module."""
    # Get lessons
    stmt = select(Lesson).where(
        Lesson.module_id == module_id
    ).order_by(Lesson.order_index)
    result = await db.execute(stmt)
    lessons = result.scalars().all()

    # Get completions
    completion_stmt = select(LessonCompletion).where(
        LessonCompletion.user_id == current_user.id,
        LessonCompletion.module_id == module_id
    )
    completion_result = await db.execute(completion_stmt)
    completions = completion_result.scalars().all()
    
    # Create completion map
    completion_map = {str(c.lesson_id): c for c in completions}

    # Build response
    response = []
    for lesson in lessons:
        lesson_id = str(lesson.id)
        completion = completion_map.get(lesson_id)
        
        response.append(LessonResponse(
            id=lesson_id,
            module_id=str(lesson.module_id),
            title=lesson.title,
            content=lesson.content,
            order_index=lesson.order_index,
            duration_minutes=lesson.duration_minutes,
            xp_reward=lesson.xp_reward or 50,
            difficulty=lesson.difficulty,
            completed=completion is not None,
            completed_at=completion.completed_at.isoformat() if completion else None,
            quiz_score=completion.quiz_score if completion else None,
        ))

    logger.info(f"Retrieved {len(response)} lessons for module {module_id}")
    return response


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
@log_request
@handle_errors(default_message="Failed to get lesson")
async def get_lesson(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get lesson details."""
    # Get lesson
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    # Get completion
    completion_stmt = select(LessonCompletion).where(
        LessonCompletion.user_id == current_user.id,
        LessonCompletion.lesson_id == lesson_id
    )
    result = await db.execute(completion_stmt)
    completion = result.scalar_one_or_none()

    return LessonResponse(
        id=str(lesson.id),
        module_id=str(lesson.module_id),
        title=lesson.title,
        content=lesson.content,
        order_index=lesson.order_index,
        duration_minutes=lesson.duration_minutes,
        xp_reward=lesson.xp_reward or 50,
        difficulty=lesson.difficulty,
        completed=completion is not None,
        completed_at=completion.completed_at.isoformat() if completion else None,
        quiz_score=completion.quiz_score if completion else None,
    )


class CompleteLessonRequest(BaseModel):
    time_spent_minutes: Optional[int] = None


class CompleteLessonResponse(BaseModel):
    message: str
    xp_earned: int
    new_xp: int
    new_level: int


@router.post("/lessons/{lesson_id}/complete", response_model=CompleteLessonResponse)
@log_request
@handle_errors(default_message="Failed to complete lesson")
async def complete_lesson(
    lesson_id: UUID,
    request: CompleteLessonRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark lesson as complete and award XP."""
    # Get lesson
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    # Check if already completed
    completion_stmt = select(LessonCompletion).where(
        LessonCompletion.user_id == current_user.id,
        LessonCompletion.lesson_id == lesson_id
    )
    result = await db.execute(completion_stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lesson already completed"
        )

    # Create completion
    completion = LessonCompletion(
        user_id=current_user.id,
        lesson_id=lesson_id,
        module_id=lesson.module_id,
        time_spent_minutes=request.time_spent_minutes,
    )
    db.add(completion)

    # Update user progress (import here to avoid circular import)
    from app.models.training import UserProgress as TrainingProgress
    
    progress_stmt = select(TrainingProgress).where(TrainingProgress.user_id == current_user.id)
    progress_result = await db.execute(progress_stmt)
    progress = progress_result.scalar_one_or_none()

    xp_earned = lesson.xp_reward or 50
    
    if not progress:
        # Create progress if doesn't exist
        progress = TrainingProgress(
            user_id=current_user.id,
            xp=xp_earned,
            level=1,
        )
        db.add(progress)
    else:
        # Update progress
        progress.xp += xp_earned
        progress.level = (progress.xp // 500) + 1  # 500 XP per level

    await db.commit()
    await db.refresh(progress)

    logger.info(f"Lesson {lesson_id} completed by user {current_user.id}, earned {xp_earned} XP")

    return CompleteLessonResponse(
        message="Lesson completed successfully",
        xp_earned=xp_earned,
        new_xp=progress.xp,
        new_level=progress.level,
    )
