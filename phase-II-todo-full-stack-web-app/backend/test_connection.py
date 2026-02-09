"""
Test database connection to NeonDB.

This script tests the connection to the NeonDB PostgreSQL database
and verifies that all components are working correctly.
"""

import asyncio
import sys
from sqlalchemy import text
from database import async_engine, engine, DATABASE_URL


async def test_async_connection():
    """Test async database connection."""
    print("Testing async database connection...")
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Async connection successful!")
            print(f"  PostgreSQL version: {version[:50]}...")
            return True
    except Exception as e:
        print(f"✗ Async connection failed: {e}")
        return False


def test_sync_connection():
    """Test synchronous database connection."""
    print("\nTesting synchronous database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Sync connection successful!")
            print(f"  PostgreSQL version: {version[:50]}...")
            return True
    except Exception as e:
        print(f"✗ Sync connection failed: {e}")
        return False


async def test_database_operations():
    """Test basic database operations."""
    print("\nTesting basic database operations...")
    try:
        async with async_engine.connect() as conn:
            # Test SELECT
            result = await conn.execute(text("SELECT 1 as test"))
            value = result.scalar()
            assert value == 1
            print("✓ SELECT query works")

            # Test current database
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✓ Connected to database: {db_name}")

            # Test current user
            result = await conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"✓ Connected as user: {user}")

            # Check if tables exist
            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]

            if tables:
                print(f"✓ Found {len(tables)} table(s): {', '.join(tables)}")
            else:
                print("⚠ No tables found (run init_db.py to create tables)")

            return True
    except Exception as e:
        print(f"✗ Database operations failed: {e}")
        return False


async def main():
    """Main test function."""
    print("=" * 70)
    print("NeonDB Connection Test")
    print("=" * 70)
    print(f"\nDatabase URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'N/A'}")
    print()

    # Test async connection
    async_success = await test_async_connection()

    # Test sync connection
    sync_success = test_sync_connection()

    # Test database operations
    ops_success = await test_database_operations()

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Async Connection: {'✓ PASS' if async_success else '✗ FAIL'}")
    print(f"Sync Connection:  {'✓ PASS' if sync_success else '✗ FAIL'}")
    print(f"DB Operations:    {'✓ PASS' if ops_success else '✗ FAIL'}")
    print()

    if async_success and sync_success and ops_success:
        print("✓ All tests passed! Database is ready to use.")
        return 0
    else:
        print("✗ Some tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)