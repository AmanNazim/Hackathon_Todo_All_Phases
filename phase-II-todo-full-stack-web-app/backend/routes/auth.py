"""
Authentication routes for the Todo application API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from database import get_session
from models import User, UserCreate, UserRead
from auth import hash_password, verify_password, create_access_token, TokenData
from middleware.auth import get_current_user
from datetime import timedelta

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


class UserLogin(BaseModel):
    """Model for user login requests."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class AuthResponse(BaseModel):
    """Model for authentication responses."""
    access_token: str
    token_type: str = "bearer"
    user: UserRead


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user.

    Args:
        user: User registration data
        session: Database session

    Returns:
        Authentication response with token and user data

    Raises:
        HTTPException: If email is already registered
    """
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = hash_password(user.password)

    # Create new user
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password_hash=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Create access token with UUID converted to string
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"user_id": str(db_user.id), "email": db_user.email},
        expires_delta=access_token_expires
    )

    # Return user data and token
    user_read = UserRead(
        id=db_user.id,
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        is_active=db_user.is_active,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_read
    )


@router.post("/login", response_model=AuthResponse)
async def login(user_credentials: UserLogin, session: Session = Depends(get_session)):
    """
    Authenticate user and return access token.

    Args:
        user_credentials: User login credentials
        session: Database session

    Returns:
        Authentication response with token and user data

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = session.exec(select(User).where(User.email == user_credentials.email)).first()
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with UUID converted to string
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )

    # Return user data and token
    user_read = UserRead(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_read
    )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: TokenData = Depends(get_current_user)):
    """
    Logout the current user.

    Note: Since we're using stateless JWT tokens, logout is handled client-side
    by removing the token. This endpoint serves as a confirmation and can be
    extended to implement token blacklisting if needed.

    Args:
        current_user: The current authenticated user

    Returns:
        Success message
    """
    return {
        "message": "Logged out successfully",
        "user_id": current_user.user_id
    }


class ForgotPasswordRequest(BaseModel):
    """Model for forgot password requests."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Model for reset password requests."""
    token: str
    new_password: str = Field(min_length=8, max_length=100)


class ChangePasswordRequest(BaseModel):
    """Model for change password requests."""
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Request a password reset email.

    Args:
        request: Forgot password request with email
        session: Database session

    Returns:
        Success message (always returns success to prevent email enumeration)
    """
    from models import PasswordResetToken
    from auth.tokens import generate_reset_token, get_reset_token_expiry
    from services.email import send_password_reset_email

    # Find user by email
    user = session.exec(select(User).where(User.email == request.email)).first()

    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If the email exists, a password reset link has been sent"}

    # Generate reset token
    plain_token, token_hash = generate_reset_token()
    expires_at = get_reset_token_expiry()

    # Save token to database
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    session.add(reset_token)
    session.commit()

    # Send password reset email
    user_name = f"{user.first_name} {user.last_name}"
    await send_password_reset_email(user.email, plain_token, user_name)

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Reset password using a reset token.

    Args:
        request: Reset password request with token and new password
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    from models import PasswordResetToken
    from auth.tokens import verify_reset_token
    from validators.auth import validate_password_strength
    from services.email import send_password_changed_email
    import hashlib

    # Validate new password strength
    try:
        validate_password_strength(request.new_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Hash the provided token to find it in database
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()

    # Find the reset token
    reset_token = session.exec(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    ).first()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Verify the token
    if not verify_reset_token(request.token, reset_token.token_hash, reset_token.expires_at, reset_token.used):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Get the user
    user = session.get(User, reset_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    user.password_hash = hash_password(request.new_password)
    user.updated_at = datetime.utcnow()

    # Mark token as used
    reset_token.used = True

    session.add(user)
    session.add(reset_token)
    session.commit()

    # Send confirmation email
    user_name = f"{user.first_name} {user.last_name}"
    await send_password_changed_email(user.email, user_name)

    return {"message": "Password reset successfully"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Change password for authenticated user.

    Args:
        request: Change password request with current and new password
        current_user: Current authenticated user
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If current password is incorrect or new password is invalid
    """
    from validators.auth import validate_password_strength
    from services.email import send_password_changed_email

    # Get the user
    user = session.exec(select(User).where(User.id == current_user.user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify current password
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    try:
        validate_password_strength(request.new_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Update password
    user.password_hash = hash_password(request.new_password)
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()

    # Send confirmation email
    user_name = f"{user.first_name} {user.last_name}"
    await send_password_changed_email(user.email, user_name)

    return {"message": "Password changed successfully"}


class VerifyEmailRequest(BaseModel):
    """Model for email verification requests."""
    token: str


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    request: VerifyEmailRequest,
    session: Session = Depends(get_session)
):
    """
    Verify user email using verification token.

    Args:
        request: Email verification request with token
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    from models import EmailVerificationToken
    from auth.tokens import verify_email_token
    import hashlib

    # Hash the provided token to find it in database
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()

    # Find the verification token
    verification_token = session.exec(
        select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)
    ).first()

    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    # Verify the token
    if not verify_email_token(request.token, verification_token.token_hash, verification_token.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    # Get the user
    user = session.get(User, verification_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Mark email as verified
    user.email_verified = True
    user.updated_at = datetime.utcnow()

    # Delete the verification token
    session.delete(verification_token)
    session.add(user)
    session.commit()

    return {"message": "Email verified successfully"}


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Resend email verification link.

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If email is already verified
    """
    from models import EmailVerificationToken
    from auth.tokens import generate_verification_token, get_verification_token_expiry
    from services.email import send_verification_email

    # Get the user
    user = session.exec(select(User).where(User.id == current_user.user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if email is already verified
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # Delete any existing verification tokens for this user
    existing_tokens = session.exec(
        select(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id)
    ).all()
    for token in existing_tokens:
        session.delete(token)

    # Generate new verification token
    plain_token, token_hash = generate_verification_token()
    expires_at = get_verification_token_expiry()

    # Save token to database
    verification_token = EmailVerificationToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    session.add(verification_token)
    session.commit()

    # Send verification email
    user_name = f"{user.first_name} {user.last_name}"
    await send_verification_email(user.email, plain_token, user_name)

    return {"message": "Verification email sent successfully"}
