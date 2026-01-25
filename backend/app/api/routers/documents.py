"""Document ingestion endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID
import logging
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.users import User
from app.models.sources import Source, Document, DocumentStatus, SourceType
from app.tasks.ingestion import process_document
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
    sanitize_filename,
    validate_file_upload,
    validate_uuid,
    SanitizedBaseModel,
)
import aiofiles
import os
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


class SourceCreate(BaseModel):
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    source_type: str
    url: Optional[HttpUrl] = None
    domain: Optional[str] = None
    peer_reviewed: bool = False


@router.post("/upload", status_code=status.HTTP_201_CREATED)
@log_request
@handle_database_errors
@handle_errors(default_message="Failed to upload document")
async def upload_document(
    file: UploadFile = File(...),
    source_title: str = Form(...),
    source_author: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Upload a document for processing with validation and proper error handling."""
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Validate and sanitize filename
    if not file.filename:
        raise AppValidationError("Filename is required")
    
    sanitized_filename, file_ext = validate_file_upload(
        file.filename,
        max_size=MAX_FILE_SIZE,
        allowed_extensions=[".pdf", ".docx", ".doc", ".txt"],
    )
    
    # Sanitize input
    source_title = sanitize_string(source_title, max_length=500)
    source_author = sanitize_string(source_author, max_length=255) if source_author else None
    
    # Determine file type
    source_type_map = {
        ".pdf": SourceType.PDF,
        ".docx": SourceType.MANUAL,
        ".doc": SourceType.MANUAL,
        ".txt": SourceType.MANUAL,
    }
    source_type = source_type_map.get(file_ext, SourceType.MANUAL)
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise AppValidationError(f"File size exceeds maximum of {MAX_FILE_SIZE / 1024 / 1024}MB")
        
        if len(content) == 0:
            raise AppValidationError("File is empty")
        
        # Create source and document in transaction
        async with transaction(db):
            source = Source(
                title=source_title,
                author=source_author,
                source_type=source_type,
                domain="uploaded",
            )
            db.add(source)
            await db.flush()
            
            # Save file
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            file_path = upload_dir / f"{source.id}_{sanitized_filename}"
            
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)
            
            # Create document record
            document = Document(
                source_id=source.id,
                title=sanitized_filename,
                file_path=str(file_path),
                file_size=len(content),
                mime_type=file.content_type,
                status=DocumentStatus.PENDING,
            )
            db.add(document)
            await db.flush()
            await db.refresh(document)
        
        # Queue processing task (outside transaction)
        try:
            process_document.delay(str(document.id))
        except Exception as e:
            logger.warning(f"Failed to queue processing task: {e}")
            # Don't fail the upload if task queueing fails
        
        logger.info(
            f"Document uploaded: {sanitized_filename} (ID: {document.id}) "
            f"by user {current_user.id}, size: {len(content)} bytes"
        )
        
        return {
            "document_id": str(document.id),
            "source_id": str(source.id),
            "status": "pending",
            "message": "Document uploaded and queued for processing",
            "file_size": len(content),
        }
    except aiofiles.IOError as e:
        logger.error(f"File I/O error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file",
        )


@router.post("/url", status_code=status.HTTP_201_CREATED)
@log_request
@handle_database_errors
@handle_errors(default_message="Failed to add URL document")
async def add_url_document(
    source_data: SourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Add a URL document for processing with validation."""
    if not source_data.url:
        raise AppValidationError("URL is required")
    
    # Sanitize input
    title = sanitize_string(source_data.title, max_length=500)
    author = sanitize_string(source_data.author, max_length=255) if source_data.author else None
    publisher = sanitize_string(source_data.publisher, max_length=255) if source_data.publisher else None
    url = str(source_data.url)
    domain = sanitize_string(source_data.domain, max_length=255) if source_data.domain else None
    
    # Extract domain from URL if not provided
    if not domain and url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
        except Exception:
            pass
    
    # Validate source type
    try:
        source_type = SourceType(source_data.source_type)
    except ValueError:
        raise AppValidationError(f"Invalid source type: {source_data.source_type}")
    
    try:
        async with transaction(db):
            source = Source(
                title=title,
                author=author,
                publisher=publisher,
                source_type=source_type,
                url=url,
                domain=domain,
                peer_reviewed=source_data.peer_reviewed,
            )
            db.add(source)
            await db.flush()
            
            # Create document record
            document = Document(
                source_id=source.id,
                title=title,
                status=DocumentStatus.PENDING,
            )
            db.add(document)
            await db.flush()
            await db.refresh(document)
        
        # Queue processing task
        try:
            process_document.delay(str(document.id))
        except Exception as e:
            logger.warning(f"Failed to queue processing task: {e}")
        
        logger.info(f"URL document added: {url} (ID: {document.id}) by user {current_user.id}")
        
        return {
            "document_id": str(document.id),
            "source_id": str(source.id),
            "status": "pending",
            "message": "URL document queued for processing",
        }
    except Exception as e:
        logger.error(f"Error adding URL document: {e}", exc_info=True)
        raise


@router.get("/{document_id}")
@log_request
@handle_errors(default_message="Failed to get document")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Get document status and metadata with validation."""
    # Validate UUID
    doc_uuid = validate_uuid(document_id, "Document ID")
    
    try:
        document = await db.get(Document, UUID(doc_uuid))
        if not document:
            raise NotFoundError("Document", document_id)
        
        logger.debug(f"Document retrieved: {document_id} by user {current_user.id}")
        
        return {
            "id": str(document.id),
            "title": document.title,
            "status": document.status.value,
            "source_id": str(document.source_id),
            "chunk_count": document.meta_data.get("chunk_count", 0) if document.meta_data else 0,
            "error": document.processing_error,
            "file_size": document.file_size,
            "mime_type": document.mime_type,
        }
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}", exc_info=True)
        raise
