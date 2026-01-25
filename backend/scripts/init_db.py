"""Initialize database with pgvector extension."""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def init_db():
    """Create database and enable pgvector extension."""
    import sys
    
    # Parse database URL to get connection details
    db_url = settings.DATABASE_URL
    # Extract database name - handle any database name
    import re
    # Match database name at end of URL
    db_match = re.search(r'/([^/]+)$', db_url)
    if db_match:
        db_name = db_match.group(1)
        postgres_url = db_url.replace(f"/{db_name}", "/postgres")
    else:
        print("ERROR: Could not parse DATABASE_URL")
        sys.exit(1)
    
    # Connect to postgres database to create our database
    try:
        engine = create_async_engine(postgres_url, echo=False)
        
        async with engine.begin() as conn:
            # Get database name from URL
            db_match = re.search(r'/([^/]+)$', db_url)
            target_db_name = db_match.group(1) if db_match else "cyber_sensei"
            
            # Check if database exists
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{target_db_name}'")
            )
            exists = result.scalar() is not None
            
            if not exists:
                # Create database (note: CREATE DATABASE cannot run in transaction)
                await conn.commit()
                # Use autocommit connection for CREATE DATABASE
                async with engine.connect() as autocommit_conn:
                    await autocommit_conn.execute(text("COMMIT"))
                    await autocommit_conn.execute(text(f"CREATE DATABASE \"{target_db_name}\""))
                print("SUCCESS: Database created")
            else:
                print("INFO: Database already exists")
        
        await engine.dispose()
    except Exception as e:
        print(f"WARNING: Could not create database (it may already exist): {e}")
        print("INFO: Continuing to enable pgvector extension...")
    
    # Connect to our database and enable pgvector
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        async with engine.begin() as conn:
            # Enable pgvector extension
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        await engine.dispose()
        print("SUCCESS: pgvector extension enabled")
        print("SUCCESS: Database initialized successfully!")
    except Exception as e:
        print(f"ERROR: Error enabling pgvector extension: {e}")
        print("Make sure:")
        print("   1. PostgreSQL is running")
        print("   2. pgvector extension is installed")
        print("   3. Database credentials in .env are correct")
        print("   4. Database name matches your configured database")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_db())
