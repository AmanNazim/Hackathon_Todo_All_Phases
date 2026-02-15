"""
Database configuration and setup for the Todo application backend.
"""

import os
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variable
# Format: postgresql://user:password@host/database?sslmode=require
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_CDA80JRTZFLG@ep-cool-fog-a1y1cy20-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

# Create the synchronous database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Maximum overflow connections
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
)

# Create async engine for async operations
# asyncpg doesn't use sslmode parameter, so we need to remove it
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("?sslmode=require", "")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"ssl": "require"},  # SSL configuration for asyncpg
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_session():
    """Get a synchronous database session."""
    with Session(engine) as session:
        yield session


async def get_async_session():
    """Get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


def create_db_and_tables():
    """Create all database tables (excluding Better Auth tables which are managed by Better Auth)."""
    # Create only application-specific tables, not Better Auth tables
    # Better Auth tables (user, session, account, verification) are managed by Better Auth itself
    application_tables = []
    for table in SQLModel.metadata.tables.values():
        # Skip Better Auth core tables since they're managed by Better Auth
        # But we still need to create password_reset_tokens and email_verification_tokens which depend on Better Auth's user table
        if table.name not in ['user', 'session', 'account', 'verification']:
            application_tables.append(table)

    # Create only the application-specific tables
    from sqlalchemy.schema import CreateTable
    for table in application_tables:
        table.create(engine, checkfirst=True)


async def create_db_and_tables_async():
    """Create all database tables asynchronously."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def drop_db_and_tables():
    """Drop all database tables (use with caution!)."""
    SQLModel.metadata.drop_all(engine)


async def drop_db_and_tables_async():
    """Drop all database tables asynchronously (use with caution!)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)