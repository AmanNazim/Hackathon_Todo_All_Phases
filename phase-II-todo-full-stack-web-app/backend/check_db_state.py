"""
Check the current state of the database and verify if Better Auth tables exist
"""
import os
from sqlmodel import create_engine
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_CDA80JRTZFLG@ep-cool-fog-a1y1cy20-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

def check_database_state():
    """Check the current state of Better Auth tables in the database."""
    print(f"Checking database state using URL: {DATABASE_URL}")

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Check if Better Auth tables exist
        ba_tables = ['user', 'session', 'account', 'verification']

        print("\nChecking Better Auth tables:")
        for table_name in ba_tables:
            try:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table_name}'
                    );
                """))
                table_exists = result.scalar()

                status = "EXISTS" if table_exists else "NOT FOUND"
                print(f"  {table_name}: {status}")

            except Exception as e:
                print(f"  {table_name}: ERROR - {str(e)}")

        # Check if any tables are in the database at all
        try:
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            all_tables = [row[0] for row in result.fetchall()]

            print(f"\nAll tables in database ({len(all_tables)}):")
            for table in all_tables:
                print(f"  - {table}")

        except Exception as e:
            print(f"Error querying all tables: {str(e)}")

        # Check if application tables exist (these should be created by SQLModel)
        app_tables = ['tasks', 'task_tags', 'task_history', 'daily_analytics', 'analytics_cache', 'password_reset_tokens', 'email_verification_tokens', 'user_preferences']

        print(f"\nChecking application tables:")
        for table_name in app_tables:
            try:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table_name}'
                    );
                """))
                table_exists = result.scalar()

                status = "EXISTS" if table_exists else "NOT FOUND"
                print(f"  {table_name}: {status}")

            except Exception as e:
                print(f"  {table_name}: ERROR - {str(e)}")

if __name__ == "__main__":
    check_database_state()