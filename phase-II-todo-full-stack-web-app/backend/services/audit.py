"""
Audit logging service for authentication events.
"""

import logging
from datetime import datetime
from typing import Optional
from enum import Enum

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler for audit logs
audit_handler = logging.FileHandler('logs/audit.log')
audit_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
audit_handler.setFormatter(formatter)
logger.addHandler(audit_handler)


class AuditEventType(str, Enum):
    """Enumeration of audit event types."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    REGISTRATION = "registration"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    EMAIL_VERIFICATION = "email_verification"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    TOKEN_REFRESH = "token_refresh"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


def log_auth_attempt(
    event_type: AuditEventType,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    details: Optional[str] = None
):
    """
    Log an authentication attempt.

    Args:
        event_type: Type of authentication event
        user_id: User ID (if available)
        email: User email
        ip_address: Client IP address
        user_agent: Client user agent
        success: Whether the attempt was successful
        details: Additional details about the event
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type.value,
        "user_id": user_id or "unknown",
        "email": email or "unknown",
        "ip_address": ip_address or "unknown",
        "user_agent": user_agent or "unknown",
        "success": success,
        "details": details or ""
    }

    log_message = (
        f"AUTH_EVENT: {event_type.value} | "
        f"User: {email or user_id or 'unknown'} | "
        f"IP: {ip_address or 'unknown'} | "
        f"Success: {success} | "
        f"Details: {details or 'none'}"
    )

    if success:
        logger.info(log_message)
    else:
        logger.warning(log_message)


def log_password_change(
    user_id: str,
    email: str,
    ip_address: Optional[str] = None,
    initiated_by: str = "user"
):
    """
    Log a password change event.

    Args:
        user_id: User ID
        email: User email
        ip_address: Client IP address
        initiated_by: Who initiated the change (user, admin, system)
    """
    log_auth_attempt(
        event_type=AuditEventType.PASSWORD_CHANGE,
        user_id=user_id,
        email=email,
        ip_address=ip_address,
        success=True,
        details=f"Password changed by {initiated_by}"
    )


def log_account_modification(
    user_id: str,
    email: str,
    modification_type: str,
    ip_address: Optional[str] = None,
    details: Optional[str] = None
):
    """
    Log an account modification event.

    Args:
        user_id: User ID
        email: User email
        modification_type: Type of modification
        ip_address: Client IP address
        details: Additional details
    """
    log_message = (
        f"ACCOUNT_MODIFICATION: {modification_type} | "
        f"User: {email} ({user_id}) | "
        f"IP: {ip_address or 'unknown'} | "
        f"Details: {details or 'none'}"
    )

    logger.info(log_message)


def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    ip_address: Optional[str] = None,
    severity: str = "INFO",
    details: Optional[str] = None
):
    """
    Log a security-related event.

    Args:
        event_type: Type of security event
        user_id: User ID (if available)
        email: User email (if available)
        ip_address: Client IP address
        severity: Severity level (INFO, WARNING, ERROR, CRITICAL)
        details: Additional details
    """
    log_message = (
        f"SECURITY_EVENT: {event_type} | "
        f"User: {email or user_id or 'unknown'} | "
        f"IP: {ip_address or 'unknown'} | "
        f"Severity: {severity} | "
        f"Details: {details or 'none'}"
    )

    if severity == "CRITICAL" or severity == "ERROR":
        logger.error(log_message)
    elif severity == "WARNING":
        logger.warning(log_message)
    else:
        logger.info(log_message)
