"""Authorization and permission checking utilities."""
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.users import User, Role
from app.models.sources import Document
from app.models.topics import ContentItem
from app.models.learning import UserProgress, UserConceptMastery
from app.models.performance import LabSession, TeachingFeedback
import logging

logger = logging.getLogger(__name__)


class PermissionDenied(HTTPException):
    """Permission denied exception."""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
        logger.warning(f"Permission denied: {detail}")


def require_roles(allowed_roles: List[Role]):
    """
    Decorator to require specific roles.
    
    Usage:
        @require_roles([Role.ADMIN, Role.INSTRUCTOR])
        async def admin_endpoint(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find current_user in kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise PermissionDenied("User not authenticated")
            
            if current_user.role not in allowed_roles:
                raise PermissionDenied(
                    f"Requires one of roles: {[r.value for r in allowed_roles]}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def check_document_ownership(
    document_id: str,
    user: User,
    db: AsyncSession,
) -> bool:
    """Check if user owns or has access to a document."""
    try:
        doc_uuid = UUID(document_id)
    except ValueError:
        return False
    
    # Admins and instructors can access all documents
    if user.role in [Role.ADMIN, Role.INSTRUCTOR, Role.MODERATOR]:
        return True
    
    # For students, check if they uploaded it
    # Note: Current schema doesn't track uploader, so we'll allow access for now
    # TODO: Add uploaded_by_user_id to documents table
    document = await db.get(Document, doc_uuid)
    if not document:
        return False
    
    # For now, allow all authenticated users to access documents
    # This should be restricted once we add ownership tracking
    return True


async def check_content_ownership(
    content_item_id: str,
    user: User,
    db: AsyncSession,
) -> bool:
    """Check if user has access to content item."""
    try:
        content_uuid = UUID(content_item_id)
    except ValueError:
        return False
    
    # Admins and instructors can access all content
    if user.role in [Role.ADMIN, Role.INSTRUCTOR, Role.MODERATOR]:
        return True
    
    # Students can access published content
    content = await db.get(ContentItem, content_uuid)
    if not content:
        return False
    
    return content.is_published


async def check_progress_ownership(
    progress_id: str,
    user: User,
    db: AsyncSession,
) -> bool:
    """Check if user owns progress record."""
    try:
        progress_uuid = UUID(progress_id)
    except ValueError:
        return False
    
    # Admins and instructors can view all progress
    if user.role in [Role.ADMIN, Role.INSTRUCTOR]:
        return True
    
    # Students can only view their own progress
    progress = await db.get(UserProgress, progress_uuid)
    if not progress:
        return False
    
    return progress.user_id == user.id


async def check_mastery_ownership(
    user_id: str,
    current_user: User,
    db: AsyncSession,
) -> bool:
    """Check if user can access mastery data."""
    try:
        target_user_uuid = UUID(user_id)
    except ValueError:
        return False
    
    # Admins and instructors can view all mastery data
    if current_user.role in [Role.ADMIN, Role.INSTRUCTOR]:
        return True
    
    # Students can only view their own mastery
    return target_user_uuid == current_user.id


async def check_lab_ownership(
    lab_session_id: str,
    user: User,
    db: AsyncSession,
) -> bool:
    """Check if user owns lab session."""
    try:
        lab_uuid = UUID(lab_session_id)
    except ValueError:
        return False
    
    # Admins and instructors can access all labs
    if user.role in [Role.ADMIN, Role.INSTRUCTOR]:
        return True
    
    # Students can only access their own labs
    lab = await db.get(LabSession, lab_uuid)
    if not lab:
        return False
    
    return lab.user_id == user.id


async def require_document_access(
    document_id: str,
    user: User,
    db: AsyncSession,
) -> None:
    """Require document access or raise PermissionDenied."""
    if not await check_document_ownership(document_id, user, db):
        raise PermissionDenied("You don't have access to this document")


async def require_content_access(
    content_item_id: str,
    user: User,
    db: AsyncSession,
) -> None:
    """Require content access or raise PermissionDenied."""
    if not await check_content_ownership(content_item_id, user, db):
        raise PermissionDenied("You don't have access to this content")


async def require_progress_access(
    progress_id: str,
    user: User,
    db: AsyncSession,
) -> None:
    """Require progress access or raise PermissionDenied."""
    if not await check_progress_ownership(progress_id, user, db):
        raise PermissionDenied("You don't have access to this progress record")


async def require_mastery_access(
    user_id: str,
    current_user: User,
    db: AsyncSession,
) -> None:
    """Require mastery access or raise PermissionDenied."""
    if not await check_mastery_ownership(user_id, current_user, db):
        raise PermissionDenied("You don't have access to this user's mastery data")


async def require_lab_access(
    lab_session_id: str,
    user: User,
    db: AsyncSession,
) -> None:
    """Require lab access or raise PermissionDenied."""
    if not await check_lab_ownership(lab_session_id, user, db):
        raise PermissionDenied("You don't have access to this lab session")


def is_admin(user: User) -> bool:
    """Check if user is admin."""
    return user.role == Role.ADMIN


def is_instructor(user: User) -> bool:
    """Check if user is instructor or admin."""
    return user.role in [Role.ADMIN, Role.INSTRUCTOR]


def is_moderator(user: User) -> bool:
    """Check if user is moderator, instructor, or admin."""
    return user.role in [Role.ADMIN, Role.INSTRUCTOR, Role.MODERATOR]


def require_admin(user: User) -> None:
    """Require admin role or raise PermissionDenied."""
    if not is_admin(user):
        raise PermissionDenied("Admin role required")


def require_instructor(user: User) -> None:
    """Require instructor or admin role or raise PermissionDenied."""
    if not is_instructor(user):
        raise PermissionDenied("Instructor or admin role required")


def require_moderator(user: User) -> None:
    """Require moderator, instructor, or admin role or raise PermissionDenied."""
    if not is_moderator(user):
        raise PermissionDenied("Moderator, instructor, or admin role required")
