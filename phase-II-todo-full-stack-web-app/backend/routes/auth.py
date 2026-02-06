"""
Authentication routes for the Todo application API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel
from ..database import get_session
from ..models import User, UserCreate, UserRead
from ..auth import hash_password, verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserLogin(BaseModel):
    """Model for user login requests."""
    email: str
    password: str


class AuthResponse(BaseModel):
    """Model for authentication responses."""
    access_token: str
    token_type: str = "bearer"
    user: UserRead


@router.post("/register", response_model=AuthResponse)
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
        password_hash=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"user_id": db_user.id, "email": db_user.email},
        expires_delta=access_token_expires
    )

    # Return user data and token
    user_read = UserRead(
        id=db_user.id,
        email=db_user.email,
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

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email},
        expires_delta=access_token_expires
    )

    # Return user data and token
    user_read = UserRead(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_read
    )