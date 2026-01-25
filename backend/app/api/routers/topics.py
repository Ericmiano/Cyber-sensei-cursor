"""Topics and concepts endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
import logging
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.models.topics import Topic, Concept, ConceptEdge, ContentItem
from app.services.cache_service import cache_service
from app.core.transaction_manager import transaction
from app.core.error_handlers import (
    handle_database_errors,
    handle_errors,
    log_request,
    NotFoundError,
    ValidationError as AppValidationError,
)
from app.core.input_validation import (
    sanitize_string,
    validate_uuid,
    validate_pagination_params,
    SanitizedBaseModel,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/topics", tags=["topics"])


class TopicCreate(SanitizedBaseModel):
    name: str
    description: Optional[str] = None
    parent_topic_id: Optional[str] = None


class ConceptCreate(SanitizedBaseModel):
    topic_id: str
    name: str
    description: Optional[str] = None
    bloom_level: int = 1
    difficulty: float = 0.5
    estimated_time_minutes: int = 30


class ConceptEdgeCreate(SanitizedBaseModel):
    concept_id: str
    prerequisite_id: str
    strength: float = 1.0


@router.get("/")
@log_request
@handle_errors(default_message="Failed to list topics")
async def list_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """List all topics with pagination."""
    # Validate pagination
    skip, limit = validate_pagination_params(skip, limit)
    
    # Check cache
    cache_key = f"topics:list:{skip}:{limit}"
    cached = cache_service.get(cache_key)
    if cached:
        logger.debug(f"Cache hit for {cache_key}")
        return cached
    
    try:
        stmt = select(Topic).offset(skip).limit(limit)
        result = await db.execute(stmt)
        topics = result.scalars().all()
        
        response = {
            "topics": [
                {
                    "id": str(t.id),
                    "name": t.name,
                    "description": t.description,
                    "parent_topic_id": str(t.parent_topic_id) if t.parent_topic_id else None,
                }
                for t in topics
            ],
            "skip": skip,
            "limit": limit,
            "total": len(topics),
        }
        
        # Cache for 1 hour
        cache_service.set(cache_key, response, ttl=3600)
        logger.info(f"Listed {len(topics)} topics (skip={skip}, limit={limit})")
        return response
    except Exception as e:
        logger.error(f"Error listing topics: {e}", exc_info=True)
        raise


@router.post("/", status_code=status.HTTP_201_CREATED)
@log_request
@handle_database_errors
@handle_errors(default_message="Failed to create topic")
async def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Create a new topic with proper validation and transaction management."""
    # Validate and sanitize input
    name = sanitize_string(topic_data.name, max_length=255)
    description = sanitize_string(topic_data.description, max_length=1000) if topic_data.description else None
    
    # Validate parent_topic_id if provided
    parent_topic_id = None
    if topic_data.parent_topic_id:
        parent_topic_id = validate_uuid(topic_data.parent_topic_id, "Parent topic ID")
        # Verify parent exists
        parent_stmt = select(Topic).where(Topic.id == UUID(parent_topic_id))
        parent_result = await db.execute(parent_stmt)
        if not parent_result.scalar_one_or_none():
            raise NotFoundError("Parent topic", parent_topic_id)
    
    try:
        async with transaction(db):
            topic = Topic(
                name=name,
                description=description,
                parent_topic_id=UUID(parent_topic_id) if parent_topic_id else None,
            )
            db.add(topic)
            await db.flush()
            await db.refresh(topic)
        
        # Invalidate cache
        cache_service.delete_pattern("topics:*")
        
        logger.info(f"Topic created: {topic.name} (ID: {topic.id}) by user {current_user.id}")
        
        return {
            "id": str(topic.id),
            "name": topic.name,
            "description": topic.description,
        }
    except ValueError as e:
        raise AppValidationError(f"Invalid UUID format: {str(e)}")


@router.get("/{topic_id}/concepts")
@log_request
@handle_errors(default_message="Failed to list concepts")
async def list_concepts(
    topic_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """List concepts for a topic with validation."""
    # Validate topic_id
    topic_uuid = validate_uuid(topic_id, "Topic ID")
    
    # Validate pagination
    skip, limit = validate_pagination_params(skip, limit)
    
    # Verify topic exists
    topic_stmt = select(Topic).where(Topic.id == UUID(topic_uuid))
    topic_result = await db.execute(topic_stmt)
    if not topic_result.scalar_one_or_none():
        raise NotFoundError("Topic", topic_id)
    
    try:
        stmt = select(Concept).where(Concept.topic_id == UUID(topic_uuid)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        concepts = result.scalars().all()
        
        logger.debug(f"Listed {len(concepts)} concepts for topic {topic_id}")
        
        return {
            "concepts": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "description": c.description,
                    "bloom_level": c.bloom_level,
                    "difficulty": c.difficulty,
                }
                for c in concepts
            ],
            "skip": skip,
            "limit": limit,
            "total": len(concepts),
        }
    except Exception as e:
        logger.error(f"Error listing concepts for topic {topic_id}: {e}", exc_info=True)
        raise


@router.post("/concepts", status_code=status.HTTP_201_CREATED)
@log_request
@handle_database_errors
@handle_errors(default_message="Failed to create concept")
async def create_concept(
    concept_data: ConceptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Create a new concept with validation."""
    # Validate and sanitize
    topic_id = validate_uuid(concept_data.topic_id, "Topic ID")
    name = sanitize_string(concept_data.name, max_length=255)
    description = sanitize_string(concept_data.description, max_length=1000) if concept_data.description else None
    
    # Validate bloom level
    if not 1 <= concept_data.bloom_level <= 6:
        raise AppValidationError("Bloom level must be between 1 and 6")
    
    # Validate difficulty
    if not 0.0 <= concept_data.difficulty <= 1.0:
        raise AppValidationError("Difficulty must be between 0.0 and 1.0")
    
    # Validate estimated time
    if concept_data.estimated_time_minutes < 1:
        raise AppValidationError("Estimated time must be at least 1 minute")
    
    # Verify topic exists
    topic_stmt = select(Topic).where(Topic.id == UUID(topic_id))
    topic_result = await db.execute(topic_stmt)
    if not topic_result.scalar_one_or_none():
        raise NotFoundError("Topic", topic_id)
    
    try:
        async with transaction(db):
            concept = Concept(
                topic_id=UUID(topic_id),
                name=name,
                description=description,
                bloom_level=concept_data.bloom_level,
                difficulty=concept_data.difficulty,
                estimated_time_minutes=concept_data.estimated_time_minutes,
            )
            db.add(concept)
            await db.flush()
            await db.refresh(concept)
        
        logger.info(f"Concept created: {concept.name} (ID: {concept.id}) by user {current_user.id}")
        
        return {
            "id": str(concept.id),
            "name": concept.name,
            "bloom_level": concept.bloom_level,
        }
    except Exception as e:
        logger.error(f"Error creating concept: {e}", exc_info=True)
        raise


@router.post("/concepts/edges", status_code=status.HTTP_201_CREATED)
@log_request
@handle_database_errors
@handle_errors(default_message="Failed to create concept edge")
async def create_concept_edge(
    edge_data: ConceptEdgeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Create a prerequisite relationship between concepts with validation."""
    # Validate UUIDs
    concept_id = validate_uuid(edge_data.concept_id, "Concept ID")
    prerequisite_id = validate_uuid(edge_data.prerequisite_id, "Prerequisite ID")
    
    # Prevent self-loops
    if concept_id == prerequisite_id:
        raise AppValidationError("Concept cannot be a prerequisite of itself")
    
    # Validate strength
    if not 0.0 <= edge_data.strength <= 1.0:
        raise AppValidationError("Strength must be between 0.0 and 1.0")
    
    # Verify concepts exist
    concept_stmt = select(Concept).where(Concept.id == UUID(concept_id))
    concept_result = await db.execute(concept_stmt)
    if not concept_result.scalar_one_or_none():
        raise NotFoundError("Concept", concept_id)
    
    prereq_stmt = select(Concept).where(Concept.id == UUID(prerequisite_id))
    prereq_result = await db.execute(prereq_stmt)
    if not prereq_result.scalar_one_or_none():
        raise NotFoundError("Prerequisite concept", prerequisite_id)
    
    try:
        async with transaction(db):
            edge = ConceptEdge(
                concept_id=UUID(concept_id),
                prerequisite_id=UUID(prerequisite_id),
                strength=edge_data.strength,
            )
            db.add(edge)
            await db.flush()
            await db.refresh(edge)
        
        logger.info(f"Concept edge created: {concept_id} -> {prerequisite_id} by user {current_user.id}")
        
        return {
            "id": str(edge.id),
            "concept_id": concept_id,
            "prerequisite_id": prerequisite_id,
            "strength": edge.strength,
        }
    except Exception as e:
        logger.error(f"Error creating concept edge: {e}", exc_info=True)
        raise
