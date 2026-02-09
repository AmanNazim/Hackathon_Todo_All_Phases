"""
Database health check and monitoring utilities.
"""

import asyncio
from datetime import datetime, UTC
from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_engine, AsyncSessionLocal


async def check_database_connection() -> Dict[str, Any]:
    """Check if database connection is healthy."""
    try:
        async with async_engine.connect() as conn:
            # Execute a simple query
            result = await conn.execute(text("SELECT 1"))
            result.scalar()

            return {
                "status": "healthy",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Database connection is healthy"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "message": f"Database connection failed: {str(e)}"
        }


async def get_database_info() -> Dict[str, Any]:
    """Get database information and statistics."""
    try:
        async with async_engine.connect() as conn:
            # Get PostgreSQL version
            version_result = await conn.execute(text("SELECT version()"))
            version = version_result.scalar()

            # Get current database name
            db_result = await conn.execute(text("SELECT current_database()"))
            database_name = db_result.scalar()

            # Get connection count
            conn_result = await conn.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
            ))
            connection_count = conn_result.scalar()

            # Get database size
            size_result = await conn.execute(text(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            ))
            database_size = size_result.scalar()

            return {
                "status": "success",
                "database_name": database_name,
                "version": version,
                "connection_count": connection_count,
                "database_size": database_size,
                "timestamp": datetime.now(UTC).isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get database info: {str(e)}",
            "timestamp": datetime.now(UTC).isoformat()
        }


async def get_table_statistics() -> Dict[str, Any]:
    """Get statistics about database tables."""
    try:
        async with async_engine.connect() as conn:
            # Get table row counts
            users_result = await conn.execute(text("SELECT COUNT(*) FROM users"))
            users_count = users_result.scalar()

            tasks_result = await conn.execute(text("SELECT COUNT(*) FROM tasks"))
            tasks_count = tasks_result.scalar()

            # Get table sizes
            users_size_result = await conn.execute(text(
                "SELECT pg_size_pretty(pg_total_relation_size('users'))"
            ))
            users_size = users_size_result.scalar()

            tasks_size_result = await conn.execute(text(
                "SELECT pg_size_pretty(pg_total_relation_size('tasks'))"
            ))
            tasks_size = tasks_size_result.scalar()

            return {
                "status": "success",
                "tables": {
                    "users": {
                        "row_count": users_count,
                        "size": users_size
                    },
                    "tasks": {
                        "row_count": tasks_count,
                        "size": tasks_size
                    }
                },
                "timestamp": datetime.now(UTC).isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get table statistics: {str(e)}",
            "timestamp": datetime.now(UTC).isoformat()
        }


async def check_indexes() -> Dict[str, Any]:
    """Check if all required indexes exist."""
    try:
        async with async_engine.connect() as conn:
            # Query to get all indexes
            result = await conn.execute(text("""
                SELECT
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """))

            indexes = []
            for row in result:
                indexes.append({
                    "table": row[0],
                    "index_name": row[1],
                    "definition": row[2]
                })

            return {
                "status": "success",
                "index_count": len(indexes),
                "indexes": indexes,
                "timestamp": datetime.now(UTC).isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to check indexes: {str(e)}",
            "timestamp": datetime.now(UTC).isoformat()
        }


async def run_health_check() -> Dict[str, Any]:
    """Run a comprehensive health check."""
    print("Running database health check...")
    print("=" * 60)

    # Check connection
    connection_status = await check_database_connection()
    print(f"\n1. Connection Status: {connection_status['status'].upper()}")
    print(f"   {connection_status['message']}")

    if connection_status['status'] != 'healthy':
        return connection_status

    # Get database info
    db_info = await get_database_info()
    print(f"\n2. Database Information:")
    print(f"   Database: {db_info.get('database_name', 'N/A')}")
    print(f"   Size: {db_info.get('database_size', 'N/A')}")
    print(f"   Connections: {db_info.get('connection_count', 'N/A')}")

    # Get table statistics
    table_stats = await get_table_statistics()
    print(f"\n3. Table Statistics:")
    if table_stats['status'] == 'success':
        for table_name, stats in table_stats['tables'].items():
            print(f"   {table_name}: {stats['row_count']} rows, {stats['size']}")

    # Check indexes
    index_info = await check_indexes()
    print(f"\n4. Indexes: {index_info.get('index_count', 0)} total")

    print("\n" + "=" * 60)
    print("Health check complete!")

    return {
        "status": "healthy",
        "connection": connection_status,
        "database_info": db_info,
        "table_statistics": table_stats,
        "indexes": index_info,
        "timestamp": datetime.now(UTC).isoformat()
    }


if __name__ == "__main__":
    asyncio.run(run_health_check())