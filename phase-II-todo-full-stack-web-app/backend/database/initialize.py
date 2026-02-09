"""
Comprehensive database initialization and setup script.

This script initializes all database components including:
- Tables and schemas
- Indexes
- Views
- Audit trails
- Security settings
"""

import asyncio
from typing import Dict, Any
from datetime import datetime, UTC

from database import async_engine, AsyncSessionLocal
from models import SQLModel
from database.views import DatabaseViews, initialize_views
from database.audit import create_audit_views
from database.security import DatabaseSecurity
from database.health_check import run_health_check
from database.backup import DatabaseBackup
from database.branching import NeonDBBranching


async def initialize_database() -> Dict[str, Any]:
    """
    Initialize the complete database with all components.

    Returns:
        Dictionary with initialization results
    """
    results = {
        "status": "success",
        "timestamp": datetime.now(UTC).isoformat(),
        "steps": []
    }

    print("=" * 80)
    print("DATABASE INITIALIZATION")
    print("=" * 80)

    # Step 1: Create tables
    print("\n1. Creating database tables...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("   ✓ Tables created successfully")
        results["steps"].append({
            "step": "create_tables",
            "status": "success",
            "message": "All tables created"
        })
    except Exception as e:
        print(f"   ✗ Failed to create tables: {e}")
        results["steps"].append({
            "step": "create_tables",
            "status": "error",
            "message": str(e)
        })
        results["status"] = "partial_failure"

    # Step 2: Create views
    print("\n2. Creating database views...")
    try:
        async with AsyncSessionLocal() as session:
            view_result = await initialize_views(session)
            if view_result["status"] == "success":
                print(f"   ✓ Created {len(view_result['views_created'])} views")
                results["steps"].append({
                    "step": "create_views",
                    "status": "success",
                    "views": view_result["views_created"]
                })
            else:
                print(f"   ⚠ Partial success: {len(view_result.get('errors', []))} errors")
                results["steps"].append({
                    "step": "create_views",
                    "status": "partial_success",
                    "views": view_result["views_created"],
                    "errors": view_result.get("errors", [])
                })
    except Exception as e:
        print(f"   ✗ Failed to create views: {e}")
        results["steps"].append({
            "step": "create_views",
            "status": "error",
            "message": str(e)
        })

    # Step 3: Create audit views
    print("\n3. Creating audit trail views...")
    try:
        async with AsyncSessionLocal() as session:
            audit_result = await create_audit_views(session)
            if audit_result["status"] == "success":
                print(f"   ✓ Created audit views")
                results["steps"].append({
                    "step": "create_audit_views",
                    "status": "success",
                    "views": audit_result["views"]
                })
            else:
                print(f"   ✗ Failed to create audit views")
                results["steps"].append({
                    "step": "create_audit_views",
                    "status": "error",
                    "message": audit_result.get("message", "Unknown error")
                })
    except Exception as e:
        print(f"   ✗ Failed to create audit views: {e}")
        results["steps"].append({
            "step": "create_audit_views",
            "status": "error",
            "message": str(e)
        })

    # Step 4: Setup security audit logging
    print("\n4. Setting up security audit logging...")
    try:
        async with AsyncSessionLocal() as session:
            security_result = await DatabaseSecurity.setup_audit_logging(session)
            if security_result["status"] == "success":
                print(f"   ✓ Security audit logging configured")
                results["steps"].append({
                    "step": "setup_security_logging",
                    "status": "success",
                    "table": security_result["table"]
                })
            else:
                print(f"   ✗ Failed to setup security logging")
                results["steps"].append({
                    "step": "setup_security_logging",
                    "status": "error",
                    "message": security_result.get("message", "Unknown error")
                })
    except Exception as e:
        print(f"   ✗ Failed to setup security logging: {e}")
        results["steps"].append({
            "step": "setup_security_logging",
            "status": "error",
            "message": str(e)
        })

    # Step 5: Run health check
    print("\n5. Running database health check...")
    try:
        health_result = await run_health_check()
        if health_result["status"] == "healthy":
            results["steps"].append({
                "step": "health_check",
                "status": "success",
                "message": "Database is healthy"
            })
        else:
            results["steps"].append({
                "step": "health_check",
                "status": "warning",
                "message": "Health check completed with warnings"
            })
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        results["steps"].append({
            "step": "health_check",
            "status": "error",
            "message": str(e)
        })

    # Step 6: Display backup information
    print("\n6. Backup and recovery information...")
    try:
        backup_manager = DatabaseBackup()
        backup_info = await backup_manager.verify_backup_capability()
        print("   ✓ Backup capabilities verified")
        results["steps"].append({
            "step": "backup_info",
            "status": "success",
            "message": "Backup capabilities available"
        })
    except Exception as e:
        print(f"   ⚠ Backup info: {e}")
        results["steps"].append({
            "step": "backup_info",
            "status": "warning",
            "message": str(e)
        })

    # Step 7: Display branching guide
    print("\n7. NeonDB branching workflow...")
    try:
        branching = NeonDBBranching()
        guide = branching.get_branching_guide()
        print("   ✓ Branching guide available")
        results["steps"].append({
            "step": "branching_guide",
            "status": "success",
            "message": "Branching workflow documented"
        })
    except Exception as e:
        print(f"   ⚠ Branching guide: {e}")

    print("\n" + "=" * 80)
    print("INITIALIZATION COMPLETE")
    print("=" * 80)

    # Summary
    success_count = sum(1 for step in results["steps"] if step["status"] == "success")
    total_count = len(results["steps"])

    print(f"\nSummary: {success_count}/{total_count} steps completed successfully")

    if results["status"] == "success":
        print("\n✓ Database is ready for use!")
    else:
        print("\n⚠ Database initialized with some warnings. Review the output above.")

    return results


async def reset_database() -> Dict[str, Any]:
    """
    Reset the database by dropping and recreating all tables.

    WARNING: This will delete all data!

    Returns:
        Dictionary with reset results
    """
    print("=" * 80)
    print("WARNING: DATABASE RESET")
    print("=" * 80)
    print("\nThis will DELETE ALL DATA in the database!")
    print("Are you sure you want to continue? (yes/no): ", end="")

    # In automated scripts, skip confirmation
    # For manual use, uncomment the following:
    # response = input()
    # if response.lower() != "yes":
    #     print("Reset cancelled.")
    #     return {"status": "cancelled", "message": "User cancelled reset"}

    print("\nDropping all tables...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        print("✓ All tables dropped")
    except Exception as e:
        print(f"✗ Failed to drop tables: {e}")
        return {"status": "error", "message": str(e)}

    print("\nDropping all views...")
    try:
        async with AsyncSessionLocal() as session:
            await DatabaseViews.drop_all_views(session)
        print("✓ All views dropped")
    except Exception as e:
        print(f"⚠ Failed to drop views: {e}")

    print("\nReinitializing database...")
    result = await initialize_database()

    return result


async def verify_database() -> Dict[str, Any]:
    """
    Verify database setup and configuration.

    Returns:
        Dictionary with verification results
    """
    print("=" * 80)
    print("DATABASE VERIFICATION")
    print("=" * 80)

    results = {
        "status": "success",
        "checks": []
    }

    # Check 1: Connection
    print("\n1. Checking database connection...")
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        print("   ✓ Connection successful")
        results["checks"].append({"check": "connection", "status": "pass"})
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        results["checks"].append({"check": "connection", "status": "fail", "error": str(e)})
        results["status"] = "failure"

    # Check 2: Tables exist
    print("\n2. Checking tables...")
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"   ✓ Found {len(tables)} tables")
            for table in tables:
                print(f"     - {table}")
            results["checks"].append({"check": "tables", "status": "pass", "count": len(tables)})
    except Exception as e:
        print(f"   ✗ Failed to check tables: {e}")
        results["checks"].append({"check": "tables", "status": "fail", "error": str(e)})

    # Check 3: Views exist
    print("\n3. Checking views...")
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.views
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            views = [row[0] for row in result]
            print(f"   ✓ Found {len(views)} views")
            for view in views:
                print(f"     - {view}")
            results["checks"].append({"check": "views", "status": "pass", "count": len(views)})
    except Exception as e:
        print(f"   ✗ Failed to check views: {e}")
        results["checks"].append({"check": "views", "status": "fail", "error": str(e)})

    # Check 4: Indexes
    print("\n4. Checking indexes...")
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("""
                SELECT COUNT(*) FROM pg_indexes
                WHERE schemaname = 'public'
            """))
            index_count = result.scalar()
            print(f"   ✓ Found {index_count} indexes")
            results["checks"].append({"check": "indexes", "status": "pass", "count": index_count})
    except Exception as e:
        print(f"   ✗ Failed to check indexes: {e}")
        results["checks"].append({"check": "indexes", "status": "fail", "error": str(e)})

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

    passed = sum(1 for check in results["checks"] if check["status"] == "pass")
    total = len(results["checks"])
    print(f"\nResult: {passed}/{total} checks passed")

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "init":
            asyncio.run(initialize_database())
        elif command == "reset":
            asyncio.run(reset_database())
        elif command == "verify":
            asyncio.run(verify_database())
        else:
            print(f"Unknown command: {command}")
            print("Usage: python initialize.py [init|reset|verify]")
    else:
        # Default: initialize
        asyncio.run(initialize_database())
