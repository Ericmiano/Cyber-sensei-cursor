"""Input validation utilities."""
import re
from typing import Optional
from pydantic import validator, ValidationError
from fastapi import HTTPException, status


def validate_password_strength(password: str) -> str:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    
    return password


def validate_email(email: str) -> str:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()


def validate_uuid(value: str, field_name: str = "ID") -> str:
    """Validate UUID format."""
    from uuid import UUID
    try:
        UUID(value)
        return value
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format: must be a valid UUID"
        )


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize user input string."""
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # Trim whitespace
    value = value.strip()
    
    # Limit length
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value
