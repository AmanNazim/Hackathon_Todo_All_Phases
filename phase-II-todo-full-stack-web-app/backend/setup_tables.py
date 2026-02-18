"""
Script to setup all database tables for the Todo application backend.
This ensures both Better Auth tables (if not handled by Better Auth)
and application-specific tables are created.
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import models first to register them with SQLModel
from models import User, Task, TaskTag, TaskHistory, PasswordResetToken, EmailVerificationToken, DailyAnalytics, AnalyticsCache

# Then import database operations
from database import create_db_and_tables

if __name__ == "__main__":
    print("Setting up database tables...")
    create_db_and_tables()
    print("Database setup complete!")