"""
Test script to verify if Better Auth is properly initializing and creating tables
"""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import after adding to path
from sqlmodel import create_engine
from sqlalchemy import text

def test_ba_table_creation():
    """Test if Better Auth tables are created when Better Auth initializes."""
    print("Testing Better Auth table creation readiness...")

    # Get database URL with fallback (same as in drop_ba_tables.py)
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_CDA80JRTZFLG@ep-cool-fog-a1y1cy20-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    )
    print(f"Using database URL: {database_url[:50]}...")

    print(f"Using DATABASE_URL: {database_url[:50]}...")

    # Test if connection works
    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Test the connection
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✓ Database connection successful")
            print(f"  Version: {version[:50]}...")

            # Check what tables exist currently
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"\nTables currently in database ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")

            # Expected Better Auth tables
            expected_ba_tables = ['user', 'session', 'account', 'verification']
            existing_ba_tables = [t for t in expected_ba_tables if t in tables]

            print(f"\nBetter Auth tables status:")
            if existing_ba_tables:
                print(f"  ✅ Found: {existing_ba_tables}")
                print("  Better Auth tables already exist")
            else:
                print("  ❌ None found")
                print("  This may indicate Better Auth hasn't created tables yet")

                print(f"\nExpected Better Auth tables:")
                for table in expected_ba_tables:
                    print(f"  - {table}")

                print("\nThis could mean:")
                print("  1. Better Auth hasn't been initialized yet")
                print("  2. Better Auth initialization failed")
                print("  3. Better Auth is not using the same DB connection")

    except Exception as e:
        print(f"ERROR: Database connection failed: {str(e)}")

if __name__ == "__main__":
    test_ba_table_creation()