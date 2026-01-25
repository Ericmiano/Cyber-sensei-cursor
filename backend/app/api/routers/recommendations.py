"""Recommendation endpoints."""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.engines.recommendation import RecommendationEngine
from app.core.error_handlers import handle_errors, log_request
from app.core.input_validation import validate_pagination_params

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/")
@log_request
@handle_errors(default_message="Failed to get recommendations")
async def get_recommendations(
    limit: int = Query(5, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Get personalized learning recommendations with validation."""
    # Validate limit
    _, validated_limit = validate_pagination_params(0, limit, max_limit=50)
    
    try:
        engine = RecommendationEngine(db)
        recommendations = await engine.get_recommendations(
            user_id=str(current_user.id),
            limit=validated_limit,
        )
        
        logger.info(
            f"Recommendations retrieved for user {current_user.id}: "
            f"{len(recommendations)} recommendations"
        )
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
        }
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise
