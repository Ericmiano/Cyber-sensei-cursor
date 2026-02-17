#!/usr/bin/env python
"""Reset the database - drop and recreate."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def reset_database():
    """Drop and recreate the database."""
    print("=" * 60)
    print("Resetting Cyber-SenseiDB Database")
    print("=" * 60)
    print()
    
    # Load config
    from app.core.config import settings
    db_url = settings.DATABASE_URL
    
    # Extract connection details
    parts = db_url.replace("postgresql+asyncpg://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    
    username = user_pass[0]
    password = user_pass[1]
    host_port = host_db[0]
    database = host_db[1]
    
    # Connect to postgres database
    postgres_url = f"postgresql+asyncpg://{username}:{password}@{host_port}/postgres"
    
    print(f"Dropping database '{database}'...")
    
    try:
        engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")
        
        async with engine.connect() as conn:
            # Terminate existing connections
            await conn.execute(text(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{database}'
                AND pid <> pg_backend_pid()
            """))
            
            # Drop database
            await conn.execute(text(f'DROP DATABASE IF EXISTS "{database}"'))
            print(f"✓ Database '{database}' dropped")
            
            # Recreate database
            await conn.execute(text(f'CREATE DATABASE "{database}"'))
            print(f"✓ Database '{database}' created")
            
        await engine.dispose()
        
        print()
        print("=" * 60)
        print("Database reset complete!")
        print("=" * 60)
        print()
        print("Next step: Run migrations")
        print("  alembic upgrade head")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to reset database: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(reset_database())
    sys.exit(0 if success else 1)
