"""
Database configuration and setup for the Todo application backend.
"""

import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/todo_dev")

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    """Get a database session."""
    with Session(engine) as session:
        yield session