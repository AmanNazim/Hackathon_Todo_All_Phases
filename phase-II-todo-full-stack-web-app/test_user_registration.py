"""
Test script to verify that user registration is working properly and
user data is being created in the database.
"""
import asyncio
import os
from datetime import datetime
from sqlmodel import create_engine, Session, select
from models import BetterAuthUser, User
from database import DATABASE_URL

def test_user_registration():
    """
    Test that user data is properly created in the database after registration.
    """
    print("Testing user registration and database persistence...")

    # Create a database engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Get a session
    with Session(engine) as session:
        # Query the user table to see if users exist
        try:
            # Count number of users
            stmt = select(BetterAuthUser)
            users = session.exec(stmt).all()

            print(f"Number of users found in database: {len(users)}")

            if users:
                print("Users in database:")
                for i, user in enumerate(users, 1):
                    print(f"  {i}. ID: {user.id}")
                    print(f"     Email: {user.email}")
                    print(f"     Name: {user.name}")
                    print(f"     Created: {user.createdAt}")
                    print(f"     Verified: {user.emailVerified}")
                    print()
            else:
                print("No users found in the database.")
                print("This could mean either:")
                print("  1. Better Auth tables haven't been created yet")
                print("  2. No registrations have been performed yet")
                print("  3. There's a configuration issue with Better Auth table creation")

        except Exception as e:
            print(f"Error querying users: {str(e)}")
            print("This might indicate that the Better Auth tables don't exist yet.")
            print("Make sure Better Auth has run its migrations properly.")

if __name__ == "__main__":
    test_user_registration()