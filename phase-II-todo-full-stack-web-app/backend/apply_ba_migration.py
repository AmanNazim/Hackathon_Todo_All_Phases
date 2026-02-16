"""
Script to apply Better Auth migration SQL directly to the database
"""
import os
from sqlmodel import create_engine
from sqlalchemy import text

def apply_ba_migration():
    """Apply the Better Auth table creation migration."""
    # Use the same URL as before
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_CDA80JRTZFLG@ep-cool-fog-a1y1cy20-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    )

    print(f"Applying Better Auth migration to database...")

    # Read the migration SQL from the generated file
    migration_file = "../frontend/drizzle/0000_busy_morlun.sql"
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    print("Migration SQL:")
    print(migration_sql)
    print("\n" + "="*50)

    # Connect to the database
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Execute the migration
            statements = migration_sql.split("--> statement-breakpoint")
            for statement in statements:
                statement = statement.strip()
                if statement:
                    print(f"Executing: {statement[:50]}...")
                    conn.execute(text(statement))

            conn.commit()
            print("\nSUCCESS: Better Auth tables created successfully!")

            # Verify tables were created
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('user', 'session', 'account', 'verification')
                ORDER BY table_name;
            """))

            created_tables = [row[0] for row in result.fetchall()]
            print(f"Tables created: {created_tables}")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    apply_ba_migration()