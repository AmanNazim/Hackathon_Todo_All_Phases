"""
NeonDB Branching Utilities and Development Workflow Guide.

NeonDB branching allows you to create isolated database environments
for development, testing, and staging without duplicating data.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, UTC
import os


class NeonDBBranching:
    """
    NeonDB branching management and workflow utilities.

    Note: Branch creation and management is done through the NeonDB Console
    or API. This class provides guidance and helper utilities.
    """

    @staticmethod
    def get_branching_guide() -> Dict[str, Any]:
        """
        Get comprehensive guide for NeonDB branching workflow.

        Returns:
            Dictionary with branching guide and best practices
        """
        return {
            "overview": {
                "description": "NeonDB branches are isolated database environments created from a parent branch",
                "benefits": [
                    "Zero-cost for inactive branches",
                    "Instant branch creation from any point in time",
                    "Isolated development and testing environments",
                    "Safe experimentation without affecting production",
                    "Easy rollback and recovery"
                ],
                "use_cases": [
                    "Feature development",
                    "Testing database migrations",
                    "Staging environments",
                    "Bug investigation",
                    "Performance testing",
                    "Data recovery and rollback"
                ]
            },
            "branch_types": {
                "main": {
                    "description": "Production database branch",
                    "purpose": "Live production data",
                    "protection": "Should be protected from direct changes",
                    "backup": "Automated backups enabled"
                },
                "staging": {
                    "description": "Pre-production testing environment",
                    "purpose": "Final testing before production deployment",
                    "source": "Created from main branch",
                    "updates": "Periodically refreshed from main"
                },
                "development": {
                    "description": "Development and testing environment",
                    "purpose": "Feature development and testing",
                    "source": "Created from main or staging",
                    "lifecycle": "Short-lived, deleted after feature completion"
                },
                "feature_branches": {
                    "description": "Individual feature development branches",
                    "purpose": "Isolated feature development",
                    "naming": "feature/<feature-name>",
                    "lifecycle": "Created for feature, deleted after merge"
                }
            },
            "workflow": {
                "setup": [
                    "1. Create main branch (production database)",
                    "2. Create staging branch from main",
                    "3. Create development branch from main",
                    "4. Configure connection strings for each environment"
                ],
                "feature_development": [
                    "1. Create feature branch from main or development",
                    "2. Update DATABASE_URL to point to feature branch",
                    "3. Develop and test feature on isolated branch",
                    "4. Run migrations on feature branch",
                    "5. Test thoroughly on feature branch",
                    "6. Merge code changes to main repository",
                    "7. Apply migrations to staging, then production",
                    "8. Delete feature branch after deployment"
                ],
                "migration_testing": [
                    "1. Create test branch from production",
                    "2. Apply migration to test branch",
                    "3. Verify migration success and data integrity",
                    "4. Test application with migrated schema",
                    "5. If successful, apply to staging then production",
                    "6. If failed, delete test branch and fix migration"
                ],
                "bug_investigation": [
                    "1. Create debug branch from production at specific timestamp",
                    "2. Investigate issue on isolated branch",
                    "3. Test fixes on debug branch",
                    "4. Apply fixes to main codebase",
                    "5. Delete debug branch after resolution"
                ]
            },
            "best_practices": [
                "Name branches descriptively (e.g., feature/user-auth, debug/task-deletion)",
                "Delete branches after they're no longer needed to reduce costs",
                "Use point-in-time branching for debugging production issues",
                "Test migrations on branches before applying to production",
                "Keep staging branch synchronized with production regularly",
                "Document branch purpose and lifecycle in branch description",
                "Use environment variables for connection strings",
                "Never commit connection strings to version control"
            ],
            "commands": {
                "create_branch": {
                    "method": "NeonDB Console or API",
                    "console_steps": [
                        "1. Go to NeonDB Console > Your Project > Branches",
                        "2. Click 'Create Branch'",
                        "3. Select parent branch",
                        "4. Choose point in time (current or specific timestamp)",
                        "5. Name the branch",
                        "6. Click 'Create'"
                    ],
                    "api_example": "curl -X POST https://console.neon.tech/api/v2/projects/{project_id}/branches"
                },
                "switch_branch": {
                    "method": "Update DATABASE_URL environment variable",
                    "steps": [
                        "1. Get connection string from NeonDB Console",
                        "2. Update DATABASE_URL in .env file",
                        "3. Restart application",
                        "4. Verify connection to correct branch"
                    ]
                },
                "delete_branch": {
                    "method": "NeonDB Console or API",
                    "console_steps": [
                        "1. Go to NeonDB Console > Your Project > Branches",
                        "2. Find the branch to delete",
                        "3. Click '...' menu > Delete",
                        "4. Confirm deletion"
                    ],
                    "warning": "Cannot delete main branch or branches with active connections"
                }
            }
        }

    @staticmethod
    def get_environment_config() -> Dict[str, Any]:
        """
        Get recommended environment configuration for different branches.

        Returns:
            Dictionary with environment configurations
        """
        return {
            "production": {
                "branch_name": "main",
                "env_file": ".env.production",
                "settings": {
                    "DATABASE_URL": "postgresql://user:pass@host/db?sslmode=require",
                    "ENVIRONMENT": "production",
                    "DEBUG": "false",
                    "LOG_LEVEL": "info",
                    "ENABLE_METRICS": "true",
                    "BACKUP_ENABLED": "true"
                },
                "recommendations": [
                    "Enable automated backups",
                    "Set up monitoring and alerting",
                    "Use connection pooling",
                    "Enable SSL/TLS",
                    "Restrict database access"
                ]
            },
            "staging": {
                "branch_name": "staging",
                "env_file": ".env.staging",
                "settings": {
                    "DATABASE_URL": "postgresql://user:pass@host-staging/db?sslmode=require",
                    "ENVIRONMENT": "staging",
                    "DEBUG": "false",
                    "LOG_LEVEL": "debug",
                    "ENABLE_METRICS": "true",
                    "BACKUP_ENABLED": "false"
                },
                "recommendations": [
                    "Refresh from production periodically",
                    "Test migrations before production",
                    "Mirror production configuration",
                    "Use for final testing"
                ]
            },
            "development": {
                "branch_name": "development",
                "env_file": ".env.development",
                "settings": {
                    "DATABASE_URL": "postgresql://user:pass@host-dev/db?sslmode=require",
                    "ENVIRONMENT": "development",
                    "DEBUG": "true",
                    "LOG_LEVEL": "debug",
                    "ENABLE_METRICS": "false",
                    "BACKUP_ENABLED": "false"
                },
                "recommendations": [
                    "Use for feature development",
                    "Safe to experiment and break things",
                    "Reset from production when needed",
                    "Share among development team"
                ]
            },
            "local": {
                "branch_name": "feature/<your-feature>",
                "env_file": ".env.local",
                "settings": {
                    "DATABASE_URL": "postgresql://user:pass@host-feature/db?sslmode=require",
                    "ENVIRONMENT": "local",
                    "DEBUG": "true",
                    "LOG_LEVEL": "debug",
                    "ENABLE_METRICS": "false",
                    "BACKUP_ENABLED": "false"
                },
                "recommendations": [
                    "Create personal feature branches",
                    "Delete after feature completion",
                    "Use for isolated development",
                    "Test migrations safely"
                ]
            }
        }

    @staticmethod
    def validate_branch_connection(database_url: str) -> Dict[str, Any]:
        """
        Validate and parse NeonDB connection string.

        Args:
            database_url: Database connection URL

        Returns:
            Dictionary with validation results
        """
        try:
            from urllib.parse import urlparse

            parsed = urlparse(database_url)

            return {
                "status": "valid",
                "scheme": parsed.scheme,
                "host": parsed.hostname,
                "port": parsed.port or 5432,
                "database": parsed.path.lstrip('/').split('?')[0],
                "username": parsed.username,
                "ssl_mode": "require" if "sslmode=require" in database_url else "prefer",
                "is_neondb": "neon.tech" in (parsed.hostname or ""),
                "recommendations": [
                    "Ensure sslmode=require is set for security",
                    "Use environment variables, never commit credentials",
                    "Verify you're connecting to the correct branch"
                ]
            }
        except Exception as e:
            return {
                "status": "invalid",
                "error": str(e),
                "message": "Invalid database URL format"
            }

    @staticmethod
    def get_migration_workflow() -> Dict[str, Any]:
        """
        Get recommended workflow for database migrations with branching.

        Returns:
            Dictionary with migration workflow
        """
        return {
            "workflow": {
                "1_develop_migration": {
                    "description": "Develop migration on feature branch",
                    "steps": [
                        "Create feature branch from main",
                        "Write migration script",
                        "Test migration on feature branch",
                        "Verify application works with new schema",
                        "Commit migration to version control"
                    ]
                },
                "2_test_on_staging": {
                    "description": "Test migration on staging branch",
                    "steps": [
                        "Create test branch from staging",
                        "Apply migration to test branch",
                        "Run full test suite",
                        "Verify data integrity",
                        "If successful, apply to actual staging",
                        "If failed, fix and repeat"
                    ]
                },
                "3_production_deployment": {
                    "description": "Deploy migration to production",
                    "steps": [
                        "Create backup branch from production (safety net)",
                        "Schedule maintenance window if needed",
                        "Apply migration to production",
                        "Monitor for errors",
                        "Verify application health",
                        "If issues occur, rollback using backup branch"
                    ]
                },
                "4_cleanup": {
                    "description": "Clean up temporary branches",
                    "steps": [
                        "Delete feature branch",
                        "Delete test branches",
                        "Keep backup branch for 7-30 days",
                        "Document migration in changelog"
                    ]
                }
            },
            "rollback_strategy": {
                "immediate_rollback": [
                    "If migration fails, restore from backup branch",
                    "Update connection string to backup branch",
                    "Investigate and fix migration",
                    "Retry on new test branch"
                ],
                "point_in_time_recovery": [
                    "Create new branch from timestamp before migration",
                    "Verify data integrity",
                    "Switch application to recovery branch",
                    "Fix migration and retry"
                ]
            }
        }


def print_branching_guide():
    """Print comprehensive NeonDB branching guide."""
    guide = NeonDBBranching.get_branching_guide()

    print("=" * 80)
    print("NEONDB BRANCHING GUIDE")
    print("=" * 80)

    print("\n📋 OVERVIEW")
    print(f"Description: {guide['overview']['description']}")
    print("\nBenefits:")
    for benefit in guide['overview']['benefits']:
        print(f"  ✓ {benefit}")

    print("\n🌳 BRANCH TYPES")
    for branch_type, info in guide['branch_types'].items():
        print(f"\n{branch_type.upper()}:")
        print(f"  Description: {info['description']}")
        print(f"  Purpose: {info['purpose']}")

    print("\n⚙️ RECOMMENDED WORKFLOW")
    print("\nFeature Development:")
    for i, step in enumerate(guide['workflow']['feature_development'], 1):
        print(f"  {i}. {step}")

    print("\n✅ BEST PRACTICES")
    for practice in guide['best_practices']:
        print(f"  • {practice}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_branching_guide()
