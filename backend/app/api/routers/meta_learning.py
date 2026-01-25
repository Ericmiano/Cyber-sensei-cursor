"""Meta-learning and feedback endpoints."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, field_validator
import logging
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.engines.meta_learning import MetaLearningEngine
from app.core.error_handlers import (
    handle_errors,
    log_request,
    NotFoundError,
    ValidationError as AppValidationError,
)
from app.core.input_validation import validate_uuid, SanitizedBaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/meta-learning", tags=["meta-learning"])


class EfficacyRequest(SanitizedBaseModel):
    content_item_id: str
    user_satisfaction: float  # 0.0-1.0
    
    @field_validator("user_satisfaction")
    @classmethod
    def validate_satisfaction(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("User satisfaction must be between 0.0 and 1.0")
        return v


@router.post("/calculate-efficacy")
@log_request
@handle_errors(default_message="Failed to calculate efficacy")
async def calculate_efficacy(
    request: EfficacyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    """Calculate teaching efficacy score for a content item with validation."""
    # Validate UUID
    content_item_id = validate_uuid(request.content_item_id, "Content item ID")
    
    try:
        engine = MetaLearningEngine(db)
        result = await engine.calculate_efficacy_score(
            user_id=str(current_user.id),
            content_item_id=content_item_id,
            user_satisfaction=request.user_satisfaction,
        )
        
        logger.info(
            f"Efficacy calculated for content {content_item_id} "
            f"by user {current_user.id}: {result.get('efficacy_score', 'N/A')}"
        )
        
        return result
    except Exception as e:
        logger.error(f"Error calculating efficacy: {e}", exc_info=True)
        raise


@router.get("/shortcomings/{content_item_id}")
@log_request
@handle_errors(default_message="Failed to get shortcomings")
async def get_shortcomings(
    content_item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Get identified shortcomings for a content item with validation."""
    # Validate UUID
    item_uuid = validate_uuid(content_item_id, "Content item ID")
    
    try:
        engine = MetaLearningEngine(db)
        shortcomings = await engine.identify_content_shortcomings(item_uuid)
        
        logger.debug(
            f"Shortcomings retrieved for content {content_item_id} "
            f"by user {current_user.id}: {len(shortcomings)} items"
        )
        
        return {"shortcomings": shortcomings, "count": len(shortcomings)}
    except Exception as e:
        logger.error(f"Error getting shortcomings: {e}", exc_info=True)
        raise


@router.post("/trigger-revision/{content_item_id}")
@log_request
@handle_errors(default_message="Failed to trigger revision")
async def trigger_revision(
    content_item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Trigger content revision based on shortcomings with validation."""
    # Validate UUID
    item_uuid = validate_uuid(content_item_id, "Content item ID")
    
    try:
        engine = MetaLearningEngine(db)
        shortcomings = await engine.identify_content_shortcomings(item_uuid)
        result = await engine.trigger_content_revision(item_uuid, shortcomings)
        
        logger.info(
            f"Content revision triggered for {content_item_id} "
            f"by user {current_user.id}, {len(shortcomings)} shortcomings identified"
        )
        
        return result
    except Exception as e:
        logger.error(f"Error triggering revision: {e}", exc_info=True)
        raise
