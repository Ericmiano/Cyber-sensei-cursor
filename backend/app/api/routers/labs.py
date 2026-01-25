"""Lab orchestrator endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, field_validator
from typing import Dict, Optional
import logging
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.engines.lab_orchestrator import LabOrchestrator
from app.core.transaction_manager import transaction
from app.core.error_handlers import (
    handle_database_errors,
    handle_errors,
    log_request,
    NotFoundError,
    ValidationError as AppValidationError,
)
from app.core.input_validation import validate_uuid, sanitize_string, SanitizedBaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/labs", tags=["labs"])


class LabProvisionRequest(SanitizedBaseModel):
    content_item_id: str
    docker_image: str
    port_mappings: Dict[str, str]
    environment_variables: Dict[str, str] = {}
    
    @field_validator("docker_image")
    @classmethod
    def validate_docker_image(cls, v: str) -> str:
        v = sanitize_string(v, max_length=255)
        # Basic validation for docker image format
        if ":" not in v and "/" not in v:
            raise ValueError("Invalid docker image format")
        return v


class LabGradeRequest(SanitizedBaseModel):
    lab_session_id: str
    rubric_id: str


@router.post("/provision")
@log_request
@handle_database_errors
@handle_errors(default_message="Failed to provision lab")
async def provision_lab(
    request: LabProvisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    """Provision a new lab environment with validation."""
    # Validate UUIDs
    content_item_id = validate_uuid(request.content_item_id, "Content item ID")
    
    # Sanitize docker image
    docker_image = sanitize_string(request.docker_image, max_length=255)
    
    # Validate port mappings
    if not request.port_mappings:
        raise AppValidationError("At least one port mapping is required")
    
    # Sanitize environment variables
    sanitized_env = {
        sanitize_string(k, max_length=255): sanitize_string(v, max_length=1024)
        for k, v in request.environment_variables.items()
    }
    
    try:
        orchestrator = LabOrchestrator(db)
        lab_session = await orchestrator.provision_lab(
            user_id=str(current_user.id),
            content_item_id=content_item_id,
            docker_image=docker_image,
            port_mappings=request.port_mappings,
            environment_variables=sanitized_env,
        )
        
        logger.info(
            f"Lab provisioned: {lab_session.id} for user {current_user.id}, "
            f"image: {docker_image}"
        )
        
        return {
            "lab_session_id": str(lab_session.id),
            "status": lab_session.status.value,
            "container_id": lab_session.docker_container_id,
        }
    except Exception as e:
        logger.error(f"Error provisioning lab: {e}", exc_info=True)
        raise


@router.post("/grade")
@log_request
@handle_database_errors
@handle_errors(default_message="Failed to grade lab")
async def grade_lab(
    request: LabGradeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    """Grade a lab session against a rubric with validation."""
    # Validate UUIDs
    lab_session_id = validate_uuid(request.lab_session_id, "Lab session ID")
    rubric_id = validate_uuid(request.rubric_id, "Rubric ID")
    
    try:
        orchestrator = LabOrchestrator(db)
        result = await orchestrator.grade_lab(
            lab_session_id=lab_session_id,
            rubric_id=rubric_id,
        )
        
        logger.info(
            f"Lab graded: {lab_session_id} by user {current_user.id}, "
            f"score: {result.get('score', 'N/A')}"
        )
        
        return result
    except Exception as e:
        logger.error(f"Error grading lab: {e}", exc_info=True)
        raise


@router.post("/terminate/{lab_session_id}")
@log_request
@handle_errors(default_message="Failed to terminate lab")
async def terminate_lab(
    lab_session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Terminate a lab session with validation."""
    # Validate UUID
    session_uuid = validate_uuid(lab_session_id, "Lab session ID")
    
    try:
        orchestrator = LabOrchestrator(db)
        success = await orchestrator.terminate_lab(session_uuid)
        
        if not success:
            raise NotFoundError("Lab session", lab_session_id)
        
        logger.info(f"Lab terminated: {lab_session_id} by user {current_user.id}")
        
        return {"message": "Lab session terminated", "lab_session_id": lab_session_id}
    except Exception as e:
        logger.error(f"Error terminating lab: {e}", exc_info=True)
        raise
