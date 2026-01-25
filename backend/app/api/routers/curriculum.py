"""Curriculum endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, field_validator
import logging
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.engines.curriculum import CurriculumEngine
from app.core.error_handlers import (
    handle_errors,
    log_request,
    NotFoundError,
    ValidationError as AppValidationError,
)
from app.core.input_validation import validate_uuid, SanitizedBaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/curriculum", tags=["curriculum"])


class CurriculumRequest(SanitizedBaseModel):
    topic_id: str
    target_bloom_level: int = 3
    
    @field_validator("target_bloom_level")
    @classmethod
    def validate_bloom_level(cls, v: int) -> int:
        if not 1 <= v <= 6:
            raise ValueError("Target Bloom level must be between 1 and 6")
        return v


@router.post("/generate")
@log_request
@handle_errors(default_message="Failed to generate curriculum")
async def generate_curriculum(
    request: CurriculumRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    """Generate a personalized curriculum for a topic with validation."""
    # Validate topic_id
    topic_id = validate_uuid(request.topic_id, "Topic ID")
    
    try:
        engine = CurriculumEngine(db)
        curriculum = await engine.generate_curriculum(
            user_id=str(current_user.id),
            topic_id=topic_id,
            target_bloom_level=request.target_bloom_level,
        )
        
        logger.info(
            f"Curriculum generated for topic {topic_id} "
            f"(Bloom level {request.target_bloom_level}) by user {current_user.id}"
        )
        
        return {
            "curriculum": curriculum,
            "topic_id": topic_id,
            "target_bloom_level": request.target_bloom_level,
        }
    except Exception as e:
        logger.error(f"Error generating curriculum: {e}", exc_info=True)
        raise
