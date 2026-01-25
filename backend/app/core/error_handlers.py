"""Comprehensive error handling utilities."""
from functools import wraps
from typing import Callable, Any, Optional
from fastapi import HTTPException, status, Request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class AppException(HTTPException):
    """Base application exception with logging."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        log_message: Optional[str] = None,
        log_level: str = "error",
        exc_info: bool = False,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.log_message = log_message or detail
        
        # Log based on level
        log_func = getattr(logger, log_level.lower(), logger.error)
        if exc_info:
            log_func(self.log_message, exc_info=True)
        else:
            log_func(self.log_message)


class DatabaseError(AppException):
    """Database operation error."""
    def __init__(self, detail: str, original_error: Optional[Exception] = None):
        log_msg = f"Database error: {detail}"
        if original_error:
            log_msg += f" (Original: {str(original_error)})"
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed" if settings.ENVIRONMENT == "production" else detail,
            log_message=log_msg,
            log_level="error",
            exc_info=original_error is not None,
        )


class ValidationError(AppException):
    """Input validation error."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            log_message=f"Validation error: {detail}",
            log_level="warning",
        )


class NotFoundError(AppException):
    """Resource not found error."""
    def __init__(self, resource: str, identifier: Optional[str] = None):
        detail = f"{resource} not found"
        if identifier:
            detail += f": {identifier}"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            log_message=f"Resource not found: {resource}",
            log_level="info",
        )


class UnauthorizedError(AppException):
    """Unauthorized access error."""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            log_message=f"Unauthorized access attempt: {detail}",
            log_level="warning",
        )


def handle_database_errors(func: Callable) -> Callable:
    """
    Decorator to handle database errors consistently.
    
    Usage:
        @handle_database_errors
        async def my_endpoint(...):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            error_str = str(e).lower()
            if "unique" in error_str or "duplicate" in error_str:
                if "email" in error_str:
                    raise ValidationError("Email already registered")
                elif "username" in error_str:
                    raise ValidationError("Username already taken")
                raise ValidationError("Duplicate entry detected")
            raise DatabaseError("Database integrity constraint violated", e)
        except OperationalError as e:
            raise DatabaseError("Database connection error", e)
        except SQLAlchemyError as e:
            raise DatabaseError("Database operation failed", e)
    
    return wrapper


def handle_errors(
    default_message: str = "An error occurred",
    log_errors: bool = True,
    reraise: bool = False,
):
    """
    Generic error handling decorator.
    
    Args:
        default_message: Default error message for unhandled exceptions
        log_errors: Whether to log errors
        reraise: Whether to re-raise exceptions after handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AppException:
                # Re-raise application exceptions
                raise
            except HTTPException:
                # Re-raise FastAPI HTTP exceptions
                raise
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Unhandled error in {func.__name__}: {str(e)}",
                        exc_info=True,
                        extra={
                            "function": func.__name__,
                            "module": func.__module__,
                        }
                    )
                
                if reraise:
                    raise
                
                # Create generic error response
                if settings.ENVIRONMENT == "production":
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=default_message,
                    )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"{default_message}: {str(e)}",
                )
        
        return wrapper
    return decorator


def log_request(func: Callable) -> Callable:
    """Decorator to log request details."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request if present
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        if not request:
            request = kwargs.get("request")
        
        if request:
            logger.info(
                f"Request: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else None,
                }
            )
        
        result = await func(*args, **kwargs)
        
        if request:
            logger.info(
                f"Response: {request.method} {request.url.path} - Success",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                }
            )
        
        return result
    
    return wrapper
