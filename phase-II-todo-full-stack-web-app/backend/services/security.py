"""
Security service for account lockout and failed attempt tracking.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# In-memory storage for account lockout (use Redis in production)
# Structure: {user_id: {"failed_attempts": int, "locked_until": datetime, "last_attempt": datetime}}
account_lockout_storage: Dict[str, dict] = {}

# Configuration
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
ATTEMPT_WINDOW_MINUTES = 15


def check_lockout(user_id: str) -> tuple[bool, Optional[datetime]]:
    """
    Check if a user account is locked out.

    Args:
        user_id: User ID to check

    Returns:
        Tuple of (is_locked, locked_until)
    """
    if user_id not in account_lockout_storage:
        return False, None

    lockout_data = account_lockout_storage[user_id]
    locked_until = lockout_data.get("locked_until")

    if locked_until and datetime.utcnow() < locked_until:
        logger.warning(f"Account {user_id} is locked until {locked_until}")
        return True, locked_until

    # Lockout expired, reset
    if locked_until and datetime.utcnow() >= locked_until:
        reset_attempts(user_id)
        return False, None

    return False, None


def increment_failed_attempts(user_id: str) -> int:
    """
    Increment failed login attempts for a user.

    Args:
        user_id: User ID

    Returns:
        Current number of failed attempts
    """
    if user_id not in account_lockout_storage:
        account_lockout_storage[user_id] = {
            "failed_attempts": 0,
            "locked_until": None,
            "last_attempt": None
        }

    lockout_data = account_lockout_storage[user_id]

    # Check if attempts are within the window
    last_attempt = lockout_data.get("last_attempt")
    if last_attempt:
        time_since_last = datetime.utcnow() - last_attempt
        if time_since_last > timedelta(minutes=ATTEMPT_WINDOW_MINUTES):
            # Reset if outside the window
            lockout_data["failed_attempts"] = 0

    # Increment attempts
    lockout_data["failed_attempts"] += 1
    lockout_data["last_attempt"] = datetime.utcnow()

    failed_attempts = lockout_data["failed_attempts"]

    # Lock account if threshold exceeded
    if failed_attempts >= MAX_FAILED_ATTEMPTS:
        lockout_data["locked_until"] = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        logger.warning(
            f"Account {user_id} locked after {failed_attempts} failed attempts. "
            f"Locked until {lockout_data['locked_until']}"
        )

    logger.info(f"Failed attempt #{failed_attempts} for user {user_id}")

    return failed_attempts


def reset_attempts(user_id: str):
    """
    Reset failed login attempts for a user.

    Args:
        user_id: User ID
    """
    if user_id in account_lockout_storage:
        account_lockout_storage[user_id] = {
            "failed_attempts": 0,
            "locked_until": None,
            "last_attempt": None
        }
        logger.info(f"Reset failed attempts for user {user_id}")


def get_remaining_attempts(user_id: str) -> int:
    """
    Get the number of remaining login attempts before lockout.

    Args:
        user_id: User ID

    Returns:
        Number of remaining attempts
    """
    if user_id not in account_lockout_storage:
        return MAX_FAILED_ATTEMPTS

    failed_attempts = account_lockout_storage[user_id].get("failed_attempts", 0)
    remaining = MAX_FAILED_ATTEMPTS - failed_attempts

    return max(0, remaining)
