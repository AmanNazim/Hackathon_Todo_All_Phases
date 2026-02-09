"""
Pytest configuration and shared fixtures for testing.
"""

import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Set test environment
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app
from database import get_session
from models import User, Task, PasswordResetToken, EmailVerificationToken


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    Uses in-memory SQLite for fast, isolated tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database session override.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict:
    """
    Sample user data for testing.
    """
    return {
        "email": "test@example.com",
        "password": "Test@Password123",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def test_user(session: Session, test_user_data: dict) -> User:
    """
    Create a test user in the database.
    """
    from auth import get_password_hash

    user = User(
        email=test_user_data["email"],
        password_hash=get_password_hash(test_user_data["password"]),
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"],
        email_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """
    Generate authentication headers with valid JWT token.
    """
    from auth import create_access_token

    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def unverified_user(session: Session) -> User:
    """
    Create a test user with unverified email.
    """
    from auth import get_password_hash

    user = User(
        email="unverified@example.com",
        password_hash=get_password_hash("Test@Password123"),
        first_name="Unverified",
        last_name="User",
        email_verified=False,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
