"""Create the Cyber-SenseiDB database."""
import asyncio
import asyncpg

async def create_database():
    """Create the Cyber-SenseiDB database."""
    password = "Mkiruga25"
    
    try:
        # Connect to default postgres database
        conn = await asyncpg.connect(
            f'postgresql://postgres:{password}@localhost:5432/postgres'
        )
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'Cyber-SenseiDB'"
        )
        
        if not exists:
            # Create database (must use autocommit)
            await conn.execute('COMMIT')
            await conn.execute('CREATE DATABASE "Cyber-SenseiDB"')
            print("SUCCESS: Database 'Cyber-SenseiDB' created")
        else:
            print("INFO: Database 'Cyber-SenseiDB' already exists")
        
        await conn.close()
        
        # Now connect to the new database and enable pgvector
        conn = await asyncpg.connect(
            f'postgresql://postgres:{password}@localhost:5432/Cyber-SenseiDB'
        )
        
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
        print("SUCCESS: pgvector extension enabled")
        
        await conn.close()
        print("SUCCESS: Database setup complete!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_database())
