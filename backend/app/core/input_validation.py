"""Input validation and sanitization utilities."""
import re
import html
from typing import Any, Optional, Callable
from functools import wraps
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException, status, Request
import logging
from app.core.error_handlers import ValidationError as AppValidationError

logger = logging.getLogger(__name__)


def sanitize_string(
    value: str,
    max_length: Optional[int] = None,
    allow_html: bool = False,
    strip_whitespace: bool = True,
) -> str:
    """
    Sanitize user input string.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML (if False, escapes HTML)
        strip_whitespace: Whether to strip leading/trailing whitespace
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # Strip whitespace
    if strip_whitespace:
        value = value.strip()
    
    # Escape HTML if not allowed
    if not allow_html:
        value = html.escape(value)
    
    # Limit length
    if max_length and len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value


def sanitize_email(email: str) -> str:
    """Sanitize and normalize email address."""
    email = sanitize_string(email, max_length=255, allow_html=False)
    email = email.lower().strip()
    
    # Basic email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise AppValidationError("Invalid email format")
    
    return email


def sanitize_username(username: str) -> str:
    """Sanitize and validate username."""
    username = sanitize_string(username, max_length=50, allow_html=False)
    username = username.strip()
    
    if len(username) < 3:
        raise AppValidationError("Username must be at least 3 characters")
    
    if len(username) > 50:
        raise AppValidationError("Username must be less than 50 characters")
    
    # Only allow alphanumeric, underscore, and hyphen
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        raise AppValidationError(
            "Username can only contain letters, numbers, underscores, and hyphens"
        )
    
    return username.lower()


def sanitize_url(url: str) -> str:
    """Sanitize and validate URL."""
    url = sanitize_string(url, max_length=2048, allow_html=False)
    url = url.strip()
    
    # Basic URL validation
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    if not re.match(pattern, url):
        raise AppValidationError("Invalid URL format")
    
    return url


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    filename = sanitize_string(filename, max_length=255, allow_html=False)
    
    # Remove path components
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"|?*]', "", filename)
    
    return filename.strip()


def validate_uuid(value: str, field_name: str = "ID") -> str:
    """Validate UUID format."""
    from uuid import UUID
    
    value = sanitize_string(value, max_length=36)
    
    try:
        UUID(value)
        return value
    except ValueError:
        raise AppValidationError(f"Invalid {field_name} format: must be a valid UUID")


def validate_pagination_params(
    skip: int = 0,
    limit: int = 100,
    max_limit: int = 1000,
) -> tuple[int, int]:
    """Validate and sanitize pagination parameters."""
    if skip < 0:
        raise AppValidationError("Skip must be >= 0")
    
    if limit < 1:
        raise AppValidationError("Limit must be >= 1")
    
    if limit > max_limit:
        raise AppValidationError(f"Limit must be <= {max_limit}")
    
    return skip, limit


def sanitize_request_data(func: Callable) -> Callable:
    """
    Decorator to sanitize request data.
    
    Automatically sanitizes string fields in Pydantic models.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find Pydantic models in kwargs
        for key, value in kwargs.items():
            if isinstance(value, BaseModel):
                # Sanitize string fields
                for field_name, field_value in value.model_dump().items():
                    if isinstance(field_value, str):
                        # Get field info
                        field_info = value.model_fields.get(field_name)
                        if field_info:
                            # Check if it's an email field
                            if "email" in field_name.lower():
                                sanitized = sanitize_email(field_value)
                            elif "username" in field_name.lower():
                                sanitized = sanitize_username(field_value)
                            elif "url" in field_name.lower():
                                sanitized = sanitize_url(field_value)
                            else:
                                sanitized = sanitize_string(field_value)
                            
                            # Update the model
                            setattr(value, field_name, sanitized)
        
        return await func(*args, **kwargs)
    
    return wrapper


class SanitizedBaseModel(BaseModel):
    """Base model with automatic string sanitization."""
    
    def model_post_init(self, __context: Any) -> None:
        """Sanitize string fields after model initialization."""
        for field_name, field_value in self.model_dump().items():
            if isinstance(field_value, str):
                field_info = self.model_fields.get(field_name)
                if field_info:
                    # Apply appropriate sanitization based on field name
                    if "email" in field_name.lower():
                        sanitized = sanitize_email(field_value)
                    elif "username" in field_name.lower():
                        sanitized = sanitize_username(field_value)
                    elif "url" in field_name.lower():
                        sanitized = sanitize_url(field_value)
                    else:
                        sanitized = sanitize_string(field_value)
                    
                    setattr(self, field_name, sanitized)


def validate_file_upload(
    filename: str,
    max_size: int = 10 * 1024 * 1024,  # 10MB default
    allowed_extensions: Optional[list[str]] = None,
) -> tuple[str, str]:
    """
    Validate file upload.
    
    Returns:
        Tuple of (sanitized_filename, file_extension)
    
    Raises:
        ValidationError: If file is invalid
    """
    if allowed_extensions is None:
        allowed_extensions = [".pdf", ".docx", ".doc", ".txt"]
    
    filename = sanitize_filename(filename)
    
    # Check extension
    file_ext = None
    for ext in allowed_extensions:
        if filename.lower().endswith(ext.lower()):
            file_ext = ext
            break
    
    if not file_ext:
        raise AppValidationError(
            f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    return filename, file_ext
