"""
Database security hardening utilities and configurations.

This module provides security features including role-based access control,
encryption helpers, and security monitoring.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, UTC
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
import hashlib


class DatabaseSecurity:
    """Database security management and hardening."""

    @staticmethod
    async def create_database_roles(session: AsyncSession) -> Dict[str, Any]:
        """
        Create database roles for role-based access control.

        Note: This requires superuser privileges. For NeonDB, roles are managed
        through the console. This is primarily for self-hosted PostgreSQL.

        Returns:
            Dictionary with role creation results
        """
        roles = {
            "app_readonly": {
                "description": "Read-only access for reporting and analytics",
                "permissions": ["SELECT"]
            },
            "app_readwrite": {
                "description": "Read-write access for application operations",
                "permissions": ["SELECT", "INSERT", "UPDATE", "DELETE"]
            },
            "app_admin": {
                "description": "Administrative access for schema changes",
                "permissions": ["ALL"]
            }
        }

        return {
            "status": "info",
            "message": "For NeonDB, manage roles through the NeonDB Console",
            "recommended_roles": roles,
            "instructions": {
                "neondb": [
                    "1. Go to NeonDB Console > Your Project > Roles",
                    "2. Create roles with appropriate permissions",
                    "3. Assign roles to database users",
                    "4. Use connection strings with role-specific credentials"
                ],
                "self_hosted": [
                    "1. Connect as superuser",
                    "2. CREATE ROLE app_readonly WITH LOGIN PASSWORD 'secure_password';",
                    "3. GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;",
                    "4. Repeat for other roles with appropriate permissions"
                ]
            }
        }

    @staticmethod
    async def enable_row_level_security(session: AsyncSession) -> Dict[str, Any]:
        """
        Enable row-level security (RLS) on tables.

        RLS ensures users can only access their own data at the database level.

        Returns:
            Dictionary with RLS setup results
        """
        try:
            results = {
                "status": "success",
                "tables_secured": [],
                "policies_created": []
            }

            # Enable RLS on tasks table
            await session.execute(text("""
                ALTER TABLE tasks ENABLE ROW LEVEL SECURITY
            """))
            results["tables_secured"].append("tasks")

            # Create policy for users to see only their own tasks
            await session.execute(text("""
                CREATE POLICY tasks_user_isolation ON tasks
                FOR ALL
                USING (user_id = current_setting('app.current_user_id')::uuid)
            """))
            results["policies_created"].append("tasks_user_isolation")

            # Enable RLS on user_preferences table
            await session.execute(text("""
                ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY
            """))
            results["tables_secured"].append("user_preferences")

            # Create policy for user preferences
            await session.execute(text("""
                CREATE POLICY preferences_user_isolation ON user_preferences
                FOR ALL
                USING (user_id = current_setting('app.current_user_id')::uuid)
            """))
            results["policies_created"].append("preferences_user_isolation")

            await session.commit()

            results["message"] = f"Enabled RLS on {len(results['tables_secured'])} tables"
            return results

        except Exception as e:
            await session.rollback()
            return {
                "status": "error",
                "message": f"Failed to enable RLS: {str(e)}",
                "note": "RLS requires proper database permissions and may not be available in all environments"
            }

    @staticmethod
    async def audit_security_settings(session: AsyncSession) -> Dict[str, Any]:
        """
        Audit current database security settings.

        Returns:
            Dictionary with security audit results
        """
        try:
            audit_results = {
                "status": "success",
                "timestamp": datetime.now(UTC).isoformat(),
                "checks": {}
            }

            # Check SSL/TLS connection
            ssl_result = await session.execute(text("SHOW ssl"))
            ssl_enabled = ssl_result.scalar()
            audit_results["checks"]["ssl_enabled"] = {
                "status": "pass" if ssl_enabled == "on" else "fail",
                "value": ssl_enabled,
                "recommendation": "SSL should be enabled for all connections"
            }

            # Check password encryption
            password_result = await session.execute(text("SHOW password_encryption"))
            password_encryption = password_result.scalar()
            audit_results["checks"]["password_encryption"] = {
                "status": "pass" if password_encryption in ["scram-sha-256", "md5"] else "fail",
                "value": password_encryption,
                "recommendation": "Use scram-sha-256 for password encryption"
            }

            # Check for tables with RLS enabled
            rls_result = await session.execute(text("""
                SELECT tablename, rowsecurity
                FROM pg_tables
                WHERE schemaname = 'public'
            """))

            rls_tables = []
            for row in rls_result:
                rls_tables.append({
                    "table": row[0],
                    "rls_enabled": row[1]
                })

            audit_results["checks"]["row_level_security"] = {
                "status": "info",
                "tables": rls_tables,
                "recommendation": "Enable RLS on tables containing user-specific data"
            }

            # Check for indexes on sensitive columns
            index_result = await session.execute(text("""
                SELECT
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """))

            indexes = []
            for row in index_result:
                indexes.append({
                    "table": row[0],
                    "index": row[1],
                    "definition": row[2]
                })

            audit_results["checks"]["indexes"] = {
                "status": "info",
                "count": len(indexes),
                "indexes": indexes[:10],  # Show first 10
                "recommendation": "Ensure sensitive columns are indexed for performance"
            }

            return audit_results

        except Exception as e:
            return {
                "status": "error",
                "message": f"Security audit failed: {str(e)}"
            }

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a cryptographically secure random token.

        Args:
            length: Length of the token in bytes

        Returns:
            Hex-encoded secure token
        """
        return secrets.token_hex(length)

    @staticmethod
    def hash_sensitive_data(data: str, salt: Optional[str] = None) -> Dict[str, str]:
        """
        Hash sensitive data using SHA-256.

        Args:
            data: Data to hash
            salt: Optional salt (generated if not provided)

        Returns:
            Dictionary with hash and salt
        """
        if salt is None:
            salt = secrets.token_hex(16)

        hash_obj = hashlib.sha256()
        hash_obj.update(f"{data}{salt}".encode('utf-8'))
        hashed = hash_obj.hexdigest()

        return {
            "hash": hashed,
            "salt": salt
        }

    @staticmethod
    async def setup_audit_logging(session: AsyncSession) -> Dict[str, Any]:
        """
        Set up database-level audit logging.

        Returns:
            Dictionary with audit logging setup results
        """
        try:
            # Create audit log table if it doesn't exist
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS security_audit_log (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    event_type VARCHAR(100) NOT NULL,
                    user_id UUID,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    resource_type VARCHAR(100),
                    resource_id UUID,
                    action VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    details JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))

            # Create index for efficient querying
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_security_audit_log_user_id
                ON security_audit_log(user_id)
            """))

            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_security_audit_log_created_at
                ON security_audit_log(created_at DESC)
            """))

            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_security_audit_log_event_type
                ON security_audit_log(event_type)
            """))

            await session.commit()

            return {
                "status": "success",
                "message": "Security audit logging table created",
                "table": "security_audit_log",
                "indexes": [
                    "idx_security_audit_log_user_id",
                    "idx_security_audit_log_created_at",
                    "idx_security_audit_log_event_type"
                ]
            }

        except Exception as e:
            await session.rollback()
            return {
                "status": "error",
                "message": f"Failed to setup audit logging: {str(e)}"
            }

    @staticmethod
    async def log_security_event(
        session: AsyncSession,
        event_type: str,
        action: str,
        status: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a security event.

        Args:
            session: Database session
            event_type: Type of security event
            action: Action performed
            status: Status of the action (success, failure, blocked)
            user_id: Optional user ID
            ip_address: Optional IP address
            user_agent: Optional user agent
            resource_type: Optional resource type
            resource_id: Optional resource ID
            details: Optional additional details

        Returns:
            Dictionary with logging result
        """
        try:
            await session.execute(
                text("""
                    INSERT INTO security_audit_log
                    (event_type, user_id, ip_address, user_agent, resource_type, resource_id, action, status, details)
                    VALUES (:event_type, :user_id, :ip_address, :user_agent, :resource_type, :resource_id, :action, :status, :details)
                """),
                {
                    "event_type": event_type,
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "action": action,
                    "status": status,
                    "details": details
                }
            )
            await session.commit()

            return {
                "status": "success",
                "message": "Security event logged"
            }

        except Exception as e:
            await session.rollback()
            return {
                "status": "error",
                "message": f"Failed to log security event: {str(e)}"
            }


class SecurityEventType:
    """Standard security event types."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


def get_security_recommendations() -> Dict[str, Any]:
    """
    Get security hardening recommendations.

    Returns:
        Dictionary with security recommendations
    """
    return {
        "encryption": {
            "at_rest": {
                "status": "NeonDB handles this automatically",
                "description": "All data is encrypted at rest using AES-256",
                "action": "No action required for NeonDB"
            },
            "in_transit": {
                "status": "Enforce SSL/TLS connections",
                "description": "All connections should use SSL/TLS",
                "action": "Ensure DATABASE_URL includes sslmode=require"
            },
            "application_level": {
                "status": "Implement for sensitive fields",
                "description": "Encrypt PII and sensitive data before storing",
                "action": "Use encryption for passwords, tokens, and sensitive user data"
            }
        },
        "access_control": {
            "authentication": {
                "status": "Implement strong authentication",
                "description": "Use JWT tokens with proper expiration",
                "action": "Implemented via Better Auth"
            },
            "authorization": {
                "status": "Enforce user isolation",
                "description": "Users should only access their own data",
                "action": "Filter all queries by user_id"
            },
            "row_level_security": {
                "status": "Optional but recommended",
                "description": "Database-level access control",
                "action": "Enable RLS on user-specific tables"
            }
        },
        "monitoring": {
            "audit_logging": {
                "status": "Implement comprehensive logging",
                "description": "Log all security-relevant events",
                "action": "Use security_audit_log table"
            },
            "anomaly_detection": {
                "status": "Monitor for suspicious patterns",
                "description": "Detect unusual access patterns",
                "action": "Implement rate limiting and pattern detection"
            },
            "alerting": {
                "status": "Set up security alerts",
                "description": "Alert on security events",
                "action": "Configure alerts for failed logins, unauthorized access"
            }
        },
        "data_protection": {
            "backup": {
                "status": "Enable automated backups",
                "description": "Regular backups with retention policy",
                "action": "Configure NeonDB automated backups"
            },
            "pii_handling": {
                "status": "Protect personally identifiable information",
                "description": "Encrypt and limit access to PII",
                "action": "Implement data classification and protection"
            },
            "data_retention": {
                "status": "Define retention policies",
                "description": "Delete old data per policy",
                "action": "Implement automated data cleanup"
            }
        }
    }
