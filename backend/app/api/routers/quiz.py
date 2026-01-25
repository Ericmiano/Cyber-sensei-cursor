"""Quiz endpoints."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, field_validator
from typing import List, Optional
import logging
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.engines.quiz import QuizEngine
from app.core.transaction_manager import transaction
from app.core.error_handlers import (
    handle_database_errors,
    handle_errors,
    log_request,
    ValidationError as AppValidationError,
)
from app.core.input_validation import validate_uuid, SanitizedBaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/quiz", tags=["quiz"])


class QuestionAnswer(SanitizedBaseModel):
    question_id: str
    answer: str
    correct: bool


class QuizSubmit(SanitizedBaseModel):
    concept_id: str
    answers: List[QuestionAnswer]
    quality_rating: int = 3  # 0-5 for SM-2
    
    @field_validator("quality_rating")
    @classmethod
    def validate_quality(cls, v: int) -> int:
        if not 0 <= v <= 5:
            raise ValueError("Quality rating must be between 0 and 5")
        return v
    
    @field_validator("answers")
    @classmethod
    def validate_answers(cls, v: List[QuestionAnswer]) -> List[QuestionAnswer]:
        if not v:
            raise ValueError("At least one answer is required")
        if len(v) > 100:
            raise ValueError("Maximum 100 answers allowed")
        return v


@router.post("/submit")
@log_request
@handle_database_errors
@handle_errors(default_message="Failed to submit quiz")
async def submit_quiz(
    quiz_data: QuizSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Submit quiz answers and update mastery with validation."""
    # Validate concept_id
    concept_id = validate_uuid(quiz_data.concept_id, "Concept ID")
    
    # Validate answers
    if not quiz_data.answers:
        raise AppValidationError("At least one answer is required")
    
    try:
        engine = QuizEngine(db)
        
        # Update mastery for each answer
        mastery_updates = []
        for answer in quiz_data.answers:
            try:
                mastery = await engine.update_mastery_bkt(
                    user_id=str(current_user.id),
                    concept_id=concept_id,
                    is_correct=answer.correct,
                )
                mastery_updates.append({
                    "question_id": answer.question_id,
                    "mastery_after": mastery,
                })
            except Exception as e:
                logger.warning(f"Failed to update mastery for question {answer.question_id}: {e}")
                # Continue with other answers
        
        # Update spaced repetition schedule
        try:
            sm2_result = await engine.update_spaced_repetition_sm2(
                user_id=str(current_user.id),
                concept_id=concept_id,
                quality=quiz_data.quality_rating,
            )
        except Exception as e:
            logger.warning(f"Failed to update spaced repetition: {e}")
            sm2_result = None
        
        logger.info(
            f"Quiz submitted: {len(quiz_data.answers)} answers for concept {concept_id} "
            f"by user {current_user.id}"
        )
        
        return {
            "mastery_updates": mastery_updates,
            "spaced_repetition": sm2_result,
            "total_answers": len(quiz_data.answers),
        }
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}", exc_info=True)
        raise
