"""
Script to drop all existing tables and recreate them with Better Auth support.
Run this once to clean up the database before deploying the updated code.
"""

from database import engine
from sqlmodel import SQLModel, text

def drop_all_tables():
    """Drop all existing tables."""
    print("Dropping all existing tables...")

    with engine.connect() as conn:
        # Drop tables in correct order (respecting foreign keys)
        tables_to_drop = [
            "task_history",
            "task_tags",
            "user_preferences",
            "analytics_cache",
            "daily_analytics",
            "email_verification_tokens",
            "password_reset_tokens",
            "tasks",
            "users",
            # Better Auth tables (if they exist)
            "session",
            "account",
            "verification",
            "user"
        ]

        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"✓ Dropped table: {table}")
            except Exception as e:
                print(f"✗ Error dropping {table}: {e}")

        conn.commit()

    print("\n✅ All tables dropped successfully!")
    print("\nNext steps:")
    print("1. Deploy the updated code to Hugging Face Space")
    print("2. The backend will automatically create all tables (including Better Auth tables) on startup")

if __name__ == "__main__":
    print("=" * 60)
    print("Database Cleanup Script")
    print("=" * 60)
    print("\nWARNING: This will delete ALL data in the database!")
    print("Press Ctrl+C to cancel, or Enter to continue...")
    input()

    drop_all_tables()
