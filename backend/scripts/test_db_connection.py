"""Test database connection with different configurations."""
import asyncio
import asyncpg
import sys

async def test_connection(connection_string, description):
    """Test a database connection string."""
    try:
        conn = await asyncpg.connect(connection_string)
        print(f"SUCCESS: {description}")
        await conn.close()
        return True
    except Exception as e:
        print(f"FAILED: {description} - {e}")
        return False

async def main():
    """Test various connection configurations."""
    password = "Mkiruga25"
    
    # Test connections
    configs = [
        (f"postgresql://postgres:{password}@localhost:5432/postgres", "Default postgres database"),
        (f"postgresql://postgres:{password}@localhost:5432/Cyber-SenseiDB", "Cyber-SenseiDB database"),
        (f"postgresql://postgres:{password}@127.0.0.1:5432/postgres", "Using 127.0.0.1 instead of localhost"),
    ]
    
    print("Testing PostgreSQL connections...")
    print("=" * 60)
    
    success = False
    for conn_str, desc in configs:
        if await test_connection(conn_str, desc):
            success = True
            print(f"\nWorking connection string: {conn_str}")
            break
    
    if not success:
        print("\n" + "=" * 60)
        print("All connection attempts failed.")
        print("\nPossible issues:")
        print("1. PostgreSQL is not running")
        print("2. Password is incorrect")
        print("3. PostgreSQL is on a different port")
        print("4. Username is different (not 'postgres')")
        print("\nTo find the correct connection:")
        print("- Check pgAdmin or PostgreSQL service")
        print("- Verify the server name 'Cyber-SenseiDB'")
        print("- Check if it's a server name or database name")

if __name__ == "__main__":
    asyncio.run(main())
