"""Transaction management utilities."""
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging_config import logger


@asynccontextmanager
async def transaction(db: AsyncSession):
    """
    Context manager for database transactions.
    
    Automatically commits on success, rolls back on exception.
    
    Usage:
        async with transaction(db):
            # database operations
            db.add(object)
            # auto-commit on exit
    """
    try:
        yield db
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Transaction rolled back: {e}", exc_info=True)
        raise
