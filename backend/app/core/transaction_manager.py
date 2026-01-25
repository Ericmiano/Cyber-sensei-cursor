"""Enhanced transaction management utilities."""
from contextlib import asynccontextmanager
from typing import Optional, Callable, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.core.error_handlers import DatabaseError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def transaction(
    db: AsyncSession,
    rollback_on_error: bool = True,
    log_errors: bool = True,
):
    """
    Enhanced context manager for database transactions.
    
    Automatically commits on success, rolls back on exception.
    
    Args:
        db: Database session
        rollback_on_error: Whether to rollback on error
        log_errors: Whether to log errors
    
    Usage:
        async with transaction(db):
            db.add(object)
            # auto-commit on exit
    """
    try:
        async with db.begin():
            yield db
            # Transaction commits automatically on exit
    except SQLAlchemyError as e:
        if rollback_on_error:
            try:
                await db.rollback()
            except Exception as rollback_error:
                if log_errors:
                    logger.error(
                        f"Error during rollback: {rollback_error}",
                        exc_info=True
                    )
        
        if log_errors:
            logger.error(
                f"Transaction error: {e}",
                exc_info=True,
                extra={"error_type": type(e).__name__}
            )
        
        raise DatabaseError("Transaction failed", e)
    except Exception as e:
        if rollback_on_error:
            try:
                await db.rollback()
            except Exception:
                pass
        
        if log_errors:
            logger.error(
                f"Unexpected error in transaction: {e}",
                exc_info=True
            )
        raise


@asynccontextmanager
async def nested_transaction(
    db: AsyncSession,
    savepoint_name: Optional[str] = None,
):
    """
    Create a nested transaction (savepoint).
    
    Usage:
        async with transaction(db):
            # outer transaction
            async with nested_transaction(db, "sp1"):
                # nested transaction
                db.add(object)
    """
    if savepoint_name is None:
        import uuid
        savepoint_name = f"sp_{uuid.uuid4().hex[:8]}"
    
    savepoint = await db.begin_nested()
    try:
        yield savepoint
        await savepoint.commit()
    except Exception as e:
        await savepoint.rollback()
        logger.error(f"Nested transaction {savepoint_name} rolled back: {e}")
        raise


async def safe_execute(
    db: AsyncSession,
    operation: Callable,
    *args,
    **kwargs,
) -> Any:
    """
    Safely execute a database operation with automatic transaction management.
    
    Args:
        db: Database session
        operation: Async function to execute
        *args, **kwargs: Arguments to pass to operation
    
    Returns:
        Result of the operation
    
    Raises:
        DatabaseError: If operation fails
    """
    try:
        async with transaction(db):
            result = await operation(*args, **kwargs)
            return result
    except Exception as e:
        logger.error(f"Safe execute failed: {e}", exc_info=True)
        raise


def with_transaction(func: Callable) -> Callable:
    """
    Decorator to wrap function in a transaction.
    
    Usage:
        @with_transaction
        async def my_function(db: AsyncSession, ...):
            db.add(object)
            # auto-commits
    """
    from functools import wraps
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find db session in args/kwargs
        db = None
        for arg in args:
            if isinstance(arg, AsyncSession):
                db = arg
                break
        if not db:
            db = kwargs.get("db")
        
        if not db:
            raise ValueError("No database session found in function arguments")
        
        async with transaction(db):
            return await func(*args, **kwargs)
    
    return wrapper
