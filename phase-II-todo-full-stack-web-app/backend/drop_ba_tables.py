"""
Utility script to clean Better Auth tables that may have been created by backend.
This is to allow Better Auth to create its tables with the correct schema when initialized.
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

def clean_better_auth_tables():
    """Drop Better Auth tables if they exist, so Better Auth can recreate them properly."""
    engine = create_engine(DATABASE_URL)

    # List of Better Auth managed tables
    better_auth_tables = ["user", "session", "account", "verification"]

    with engine.connect() as conn:
        for table_name in better_auth_tables:
            try:
                # Check if table exists
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table_name}'
                    );
                """))
                table_exists = result.scalar()

                if table_exists:
                    logger.info(f"Found Better Auth table '{table_name}', dropping it...")
                    # Drop the table
                    conn.execute(text(f"DROP TABLE IF EXISTS \"{table_name}\" CASCADE;"))
                    conn.commit()
                    logger.info(f"Successfully dropped table '{table_name}'")
                else:
                    logger.info(f"Table '{table_name}' does not exist, skipping...")

            except Exception as e:
                logger.error(f"Error dropping table '{table_name}': {str(e)}")
                # Don't raise the exception, continue with other tables

    logger.info("Completed cleaning Better Auth tables - Better Auth can now create them with correct schema")

if __name__ == "__main__":
    clean_better_auth_tables()