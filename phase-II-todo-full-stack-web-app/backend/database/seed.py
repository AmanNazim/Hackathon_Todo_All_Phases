"""
Seed data script for the Todo application.
Creates sample users and tasks for development/testing.
"""

from sqlmodel import Session, select
from .database import engine
from ..models import User, Task
from ..auth import hash_password
from datetime import datetime


def seed_data():
    """
    Populate the database with sample data for development/testing.
    """
    with Session(engine) as session:
        # Check if users already exist
        existing_users = session.exec(select(User)).all()
        if existing_users:
            print("Database already seeded. Skipping seeding.")
            return

        # Create sample user
        password_hash = hash_password("password123")
        sample_user = User(
            email="user@example.com",
            password_hash=password_hash
        )
        session.add(sample_user)
        session.commit()
        session.refresh(sample_user)

        # Create sample tasks for the user
        sample_tasks = [
            Task(
                title="Learn Next.js",
                description="Complete the Next.js tutorial",
                completed=False,
                user_id=sample_user.id
            ),
            Task(
                title="Build API endpoints",
                description="Create FastAPI endpoints for task management",
                completed=True,
                user_id=sample_user.id
            ),
            Task(
                title="Deploy application",
                description="Deploy the full-stack application to production",
                completed=False,
                user_id=sample_user.id
            )
        ]

        for task in sample_tasks:
            session.add(task)

        session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    seed_data()