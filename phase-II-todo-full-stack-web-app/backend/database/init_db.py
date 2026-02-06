"""
Database initialization and migration setup for the Todo application.
"""

from sqlmodel import SQLModel
from .database import engine
from ..models import User, Task  # Import models to register them with SQLModel


def create_db_and_tables():
    """
    Create database tables based on SQLModel models.
    This function should be called on application startup.
    """
    SQLModel.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_db_and_tables()
    print("Database tables created successfully!")