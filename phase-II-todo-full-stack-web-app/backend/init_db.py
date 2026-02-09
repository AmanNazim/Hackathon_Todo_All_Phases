"""
Database initialization script for the Todo application.

This script creates all database tables and sets up the initial schema.
"""

import asyncio
from database import create_db_and_tables, create_db_and_tables_async, engine, async_engine
from models import User, Task
from sqlmodel import SQLModel, text


def init_db():
    """Initialize the database with all tables (synchronous)."""
    print("Creating database tables...")

    # Create all tables
    create_db_and_tables()

    print("Database tables created successfully!")
    print("\nCreated tables:")
    print("- users")
    print("- tasks")

    # Print connection info
    print(f"\nDatabase URL: {engine.url}")


async def init_db_async():
    """Initialize the database with all tables (asynchronous)."""
    print("Creating database tables asynchronously...")

    # Create all tables
    await create_db_and_tables_async()

    print("Database tables created successfully!")
    print("\nCreated tables:")
    print("- users")
    print("- tasks")

    # Print connection info
    print(f"\nDatabase URL: {async_engine.url}")


async def verify_connection():
    """Verify database connection."""
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Database connection successful!")
            print(f"PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


async def create_indexes():
    """Create additional indexes for performance optimization."""
    print("\nCreating additional indexes...")

    async with async_engine.begin() as conn:
        # Composite index for user tasks filtering
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks(user_id, completed)"
        ))

        # Index for task priority filtering
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_tasks_user_priority ON tasks(user_id, priority)"
        ))

        # Index for due date queries
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_tasks_user_due_date ON tasks(user_id, due_date)"
        ))

    print("Additional indexes created successfully!")


async def main():
    """Main initialization function."""
    print("=" * 60)
    print("Todo Application - Database Initialization")
    print("=" * 60)
    print()

    # Verify connection
    if not await verify_connection():
        print("\nExiting due to connection failure.")
        return

    print()

    # Initialize database
    await init_db_async()

    # Create additional indexes
    await create_indexes()

    print()
    print("=" * 60)
    print("Database initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())