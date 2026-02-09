"""
Email delivery testing script.

This script tests email service integration and delivery.

Usage:
    python scripts/test_email.py --to recipient@example.com
    python scripts/test_email.py --test-all
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.email import (
    send_verification_email,
    send_password_reset_email,
    test_smtp_connection
)
from config.production import settings


async def test_smtp_connection_async():
    """Test SMTP server connection."""
    print("Testing SMTP connection...")
    try:
        result = await test_smtp_connection()
        if result:
            print("✓ SMTP connection successful")
            return True
        else:
            print("✗ SMTP connection failed")
            return False
    except Exception as e:
        print(f"✗ SMTP connection error: {e}")
        return False


async def test_verification_email(recipient: str):
    """Test sending verification email."""
    print(f"\nTesting verification email to {recipient}...")
    try:
        token = "test_verification_token_12345"
        await send_verification_email(recipient, token)
        print("✓ Verification email sent successfully")
        print(f"  Check inbox: {recipient}")
        return True
    except Exception as e:
        print(f"✗ Failed to send verification email: {e}")
        return False


async def test_password_reset_email(recipient: str):
    """Test sending password reset email."""
    print(f"\nTesting password reset email to {recipient}...")
    try:
        token = "test_reset_token_12345"
        await send_password_reset_email(recipient, token)
        print("✓ Password reset email sent successfully")
        print(f"  Check inbox: {recipient}")
        return True
    except Exception as e:
        print(f"✗ Failed to send password reset email: {e}")
        return False


async def run_all_tests(recipient: str):
    """Run all email tests."""
    print("=" * 60)
    print("Email Delivery Test Suite")
    print("=" * 60)

    print(f"\nConfiguration:")
    print(f"  SMTP Host: {settings.SMTP_HOST}")
    print(f"  SMTP Port: {settings.SMTP_PORT}")
    print(f"  SMTP Username: {settings.SMTP_USERNAME}")
    print(f"  From Email: {settings.SMTP_FROM_EMAIL}")
    print(f"  Recipient: {recipient}")

    results = []

    # Test SMTP connection
    results.append(await test_smtp_connection_async())

    # Test verification email
    results.append(await test_verification_email(recipient))

    # Test password reset email
    results.append(await test_password_reset_email(recipient))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✓ All email tests passed")
        return 0
    else:
        print("✗ Some email tests failed")
        return 1


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test email delivery")
    parser.add_argument("--to", help="Recipient email address")
    parser.add_argument("--test-all", action="store_true", help="Run all email tests")
    parser.add_argument("--smtp-only", action="store_true", help="Test SMTP connection only")

    args = parser.parse_args()

    if not args.to and not args.test_all:
        parser.error("Either --to or --test-all is required")

    recipient = args.to or "test@example.com"

    if args.smtp_only:
        result = asyncio.run(test_smtp_connection_async())
        sys.exit(0 if result else 1)
    else:
        exit_code = asyncio.run(run_all_tests(recipient))
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
