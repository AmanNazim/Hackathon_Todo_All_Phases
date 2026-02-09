"""
Email service for sending authentication-related emails.
"""

import os
from typing import Optional
from dotenv import load_dotenv
import logging

load_dotenv()

# Email configuration
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@todoapp.com")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Todo App")

# SMTP configuration (for production)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send an email.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email

    Returns:
        True if email was sent successfully, False otherwise
    """
    if not EMAIL_ENABLED:
        logger.info(f"Email sending disabled. Would send to {to_email}: {subject}")
        logger.debug(f"Email content: {html_content}")
        return True

    try:
        # TODO: Implement actual email sending using SMTP or email service provider
        # For now, just log the email
        logger.info(f"Sending email to {to_email}: {subject}")
        logger.debug(f"Email content: {html_content}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def send_password_reset_email(to_email: str, reset_token: str, user_name: str) -> bool:
    """
    Send a password reset email.

    Args:
        to_email: Recipient email address
        reset_token: Password reset token
        user_name: User's name

    Returns:
        True if email was sent successfully, False otherwise
    """
    # TODO: Get the actual frontend URL from environment variable
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/auth/reset-password?token={reset_token}"

    subject = "Password Reset Request - Todo App"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
            <h2 style="color: #4a5568;">Password Reset Request</h2>
            <p>Hello {user_name},</p>
            <p>We received a request to reset your password for your Todo App account.</p>
            <p>Click the button below to reset your password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="background-color: #4299e1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
            </div>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #4299e1;">{reset_link}</p>
            <p><strong>This link will expire in 1 hour.</strong></p>
            <p>If you didn't request a password reset, you can safely ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">
                This is an automated email from Todo App. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """

    return await send_email(to_email, subject, html_content)


async def send_verification_email(to_email: str, verification_token: str, user_name: str) -> bool:
    """
    Send an email verification email.

    Args:
        to_email: Recipient email address
        verification_token: Email verification token
        user_name: User's name

    Returns:
        True if email was sent successfully, False otherwise
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verification_link = f"{frontend_url}/auth/verify-email?token={verification_token}"

    subject = "Verify Your Email - Todo App"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
            <h2 style="color: #4a5568;">Welcome to Todo App!</h2>
            <p>Hello {user_name},</p>
            <p>Thank you for signing up! Please verify your email address to complete your registration.</p>
            <p>Click the button below to verify your email:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" style="background-color: #48bb78; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email</a>
            </div>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #48bb78;">{verification_link}</p>
            <p><strong>This link will expire in 24 hours.</strong></p>
            <p>If you didn't create an account, you can safely ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">
                This is an automated email from Todo App. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """

    return await send_email(to_email, subject, html_content)


async def send_password_changed_email(to_email: str, user_name: str) -> bool:
    """
    Send a notification email when password is changed.

    Args:
        to_email: Recipient email address
        user_name: User's name

    Returns:
        True if email was sent successfully, False otherwise
    """
    subject = "Password Changed - Todo App"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Changed</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
            <h2 style="color: #4a5568;">Password Changed Successfully</h2>
            <p>Hello {user_name},</p>
            <p>This is a confirmation that your password has been changed successfully.</p>
            <p>If you did not make this change, please contact our support team immediately.</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">
                This is an automated email from Todo App. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """

    return await send_email(to_email, subject, html_content)
