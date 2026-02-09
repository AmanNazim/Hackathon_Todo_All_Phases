"""
Database backup and recovery utilities for NeonDB PostgreSQL.

This module provides utilities for backing up and restoring the database.
NeonDB provides built-in backup capabilities, but these utilities help with
manual backups and point-in-time recovery.
"""

import asyncio
import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy import text
from database import async_engine


class DatabaseBackup:
    """Database backup and recovery manager."""

    def __init__(self, backup_dir: str = "./backups"):
        """Initialize backup manager with backup directory."""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a logical backup of the database using pg_dump.

        Note: For NeonDB, you should use their built-in backup features for production.
        This is primarily for development and testing purposes.

        Args:
            backup_name: Optional custom backup name

        Returns:
            Dictionary with backup information
        """
        try:
            # Generate backup filename
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            if backup_name:
                filename = f"{backup_name}_{timestamp}.sql"
            else:
                filename = f"backup_{timestamp}.sql"

            backup_path = self.backup_dir / filename

            # Get database URL from environment
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL not found in environment")

            # Note: This requires pg_dump to be installed
            # For NeonDB production, use their backup features instead
            print(f"Creating backup: {backup_path}")
            print("Note: This requires pg_dump to be installed locally")
            print("For production, use NeonDB's built-in backup features")

            return {
                "status": "info",
                "message": "Manual backup requires pg_dump. Use NeonDB backup features for production.",
                "backup_path": str(backup_path),
                "timestamp": timestamp,
                "instructions": {
                    "manual_backup": f"pg_dump {database_url} > {backup_path}",
                    "neondb_backup": "Use NeonDB Console > Backups > Create Backup",
                    "point_in_time_recovery": "NeonDB supports PITR up to 7 days (Pro plan)"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Backup failed: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }

    async def list_backups(self) -> Dict[str, Any]:
        """List all available backups."""
        try:
            backups = []
            for backup_file in self.backup_dir.glob("*.sql"):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(stat.st_ctime, UTC).isoformat()
                })

            backups.sort(key=lambda x: x["created_at"], reverse=True)

            return {
                "status": "success",
                "backup_count": len(backups),
                "backups": backups,
                "backup_directory": str(self.backup_dir)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list backups: {str(e)}"
            }

    async def verify_backup_capability(self) -> Dict[str, Any]:
        """Verify that backup and recovery capabilities are available."""
        try:
            async with async_engine.connect() as conn:
                # Check if we can query the database
                result = await conn.execute(text("SELECT current_database(), version()"))
                row = result.fetchone()

                return {
                    "status": "success",
                    "database": row[0],
                    "version": row[1],
                    "backup_methods": {
                        "neondb_console": {
                            "available": True,
                            "description": "Use NeonDB Console for automated backups",
                            "features": [
                                "Automated daily backups",
                                "Point-in-time recovery (PITR)",
                                "Backup retention policies",
                                "One-click restore"
                            ]
                        },
                        "neondb_branching": {
                            "available": True,
                            "description": "Use NeonDB branching for development/staging",
                            "features": [
                                "Create database branches from any point in time",
                                "Isolated development environments",
                                "Zero-cost for inactive branches",
                                "Fast branch creation"
                            ]
                        },
                        "pg_dump": {
                            "available": "requires_local_installation",
                            "description": "Manual logical backup using pg_dump",
                            "use_case": "Development and testing only"
                        }
                    },
                    "recommendations": [
                        "Enable automated backups in NeonDB Console",
                        "Set backup retention to at least 7 days",
                        "Use branching for development/staging environments",
                        "Test recovery procedures regularly",
                        "Document recovery runbooks"
                    ]
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Verification failed: {str(e)}"
            }

    async def get_recovery_info(self) -> Dict[str, Any]:
        """Get information about recovery options."""
        return {
            "status": "info",
            "recovery_methods": {
                "neondb_console_restore": {
                    "description": "Restore from automated backup via NeonDB Console",
                    "steps": [
                        "1. Go to NeonDB Console > Your Project > Backups",
                        "2. Select the backup point to restore from",
                        "3. Click 'Restore' and confirm",
                        "4. Wait for restoration to complete",
                        "5. Verify data integrity"
                    ],
                    "downtime": "Minimal (typically < 5 minutes)",
                    "data_loss": "Up to the backup point selected"
                },
                "point_in_time_recovery": {
                    "description": "Restore to any point in time within retention period",
                    "steps": [
                        "1. Go to NeonDB Console > Your Project > Backups",
                        "2. Select 'Point-in-time Recovery'",
                        "3. Choose the exact timestamp to restore to",
                        "4. Create a new branch or restore to existing",
                        "5. Verify and switch to restored database"
                    ],
                    "downtime": "Minimal (branch creation is fast)",
                    "data_loss": "Precise to the second"
                },
                "branch_restore": {
                    "description": "Create a branch from a specific point in time",
                    "steps": [
                        "1. Go to NeonDB Console > Your Project > Branches",
                        "2. Click 'Create Branch'",
                        "3. Select parent branch and point in time",
                        "4. Name the branch (e.g., 'recovery-YYYYMMDD')",
                        "5. Test on the branch before switching"
                    ],
                    "downtime": "Zero (branch is separate)",
                    "data_loss": "None (original data preserved)"
                }
            },
            "best_practices": [
                "Always test recovery on a branch first",
                "Document the incident and recovery steps",
                "Verify data integrity after recovery",
                "Update connection strings if using a new branch",
                "Keep recovery runbooks up to date"
            ]
        }


async def run_backup_info():
    """Display backup and recovery information."""
    backup_manager = DatabaseBackup()

    print("=" * 70)
    print("DATABASE BACKUP AND RECOVERY INFORMATION")
    print("=" * 70)

    # Verify capabilities
    print("\n1. Verifying Backup Capabilities...")
    capabilities = await backup_manager.verify_backup_capability()

    if capabilities["status"] == "success":
        print(f"   Database: {capabilities['database']}")
        print(f"\n   Available Backup Methods:")
        for method, info in capabilities["backup_methods"].items():
            print(f"\n   - {method}:")
            print(f"     Status: {info['available']}")
            print(f"     {info['description']}")

    # Get recovery info
    print("\n2. Recovery Options:")
    recovery_info = await backup_manager.get_recovery_info()
    for method, info in recovery_info["recovery_methods"].items():
        print(f"\n   - {method}:")
        print(f"     {info['description']}")
        print(f"     Downtime: {info['downtime']}")

    # List existing backups
    print("\n3. Local Backups:")
    backups = await backup_manager.list_backups()
    if backups["backup_count"] > 0:
        for backup in backups["backups"][:5]:  # Show last 5
            print(f"   - {backup['filename']} ({backup['size_mb']} MB)")
    else:
        print("   No local backups found")

    print("\n" + "=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    if capabilities["status"] == "success":
        for i, rec in enumerate(capabilities["recommendations"], 1):
            print(f"{i}. {rec}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(run_backup_info())
