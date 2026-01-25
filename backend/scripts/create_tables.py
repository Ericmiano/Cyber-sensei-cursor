"""Create all database tables from models."""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base
from app.models import *  # noqa: F401, F403

async def create_tables():
    """Create all tables from SQLAlchemy models."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("SUCCESS: All tables created")
    
    await engine.dispose()
    print("SUCCESS: Database tables initialized!")

if __name__ == "__main__":
    asyncio.run(create_tables())
