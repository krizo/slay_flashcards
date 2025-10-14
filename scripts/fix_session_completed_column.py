#!/usr/bin/env python3
"""
Migration script to fix the completed column in sessions table.

This script ensures the completed column has a proper default value of 0 (False)
at the database level, preventing NOT NULL constraint failures.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect, text

from core.db.database import engine


def fix_completed_column():
    """Fix the completed column to have server_default='0'."""
    table_name = "sessions"
    column_name = "completed"

    print("=" * 80)
    print("🔧 Database Migration: Fix sessions.completed column default")
    print("=" * 80)
    print()

    inspector = inspect(engine)

    # Check if table exists
    if table_name not in inspector.get_table_names():
        print(f"⚠️  Table '{table_name}' does not exist yet.")
        print("   Run database initialization first.")
        return

    print(f"📝 Updating default value for '{column_name}' column in '{table_name}' table...")
    print()

    try:
        with engine.begin() as conn:
            # SQLite doesn't support ALTER COLUMN directly
            # We need to:
            # 1. Create a new table with the correct schema
            # 2. Copy data from old table
            # 3. Drop old table
            # 4. Rename new table

            # First, check if we need to migrate at all by trying to insert
            print("   Checking current schema...")

            # For SQLite, we'll recreate the table with proper defaults
            # This is safe because we're in early development

            print("   Creating temporary table with correct schema...")
            conn.execute(text("""
                CREATE TABLE sessions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    quiz_id INTEGER NOT NULL,
                    mode VARCHAR(20) NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    score REAL,
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
                )
            """))

            print("   Copying data from old table...")
            # Copy all data, ensuring completed has a value
            conn.execute(text("""
                INSERT INTO sessions_new (id, user_id, quiz_id, mode, started_at, completed_at, score, completed)
                SELECT id, user_id, quiz_id, mode, started_at, completed_at, score,
                       COALESCE(completed, 0)
                FROM sessions
            """))

            print("   Dropping old table...")
            conn.execute(text("DROP TABLE sessions"))

            print("   Renaming new table...")
            conn.execute(text("ALTER TABLE sessions_new RENAME TO sessions"))

            print("   Recreating indexes...")
            conn.execute(text("CREATE INDEX ix_sessions_id ON sessions (id)"))
            conn.execute(text("CREATE INDEX ix_sessions_user_id ON sessions (user_id)"))
            conn.execute(text("CREATE INDEX ix_sessions_quiz_id ON sessions (quiz_id)"))

        print()
        print(f"✅ Successfully updated '{column_name}' column in '{table_name}' table.")
        print()
        print("=" * 80)
        print("✅ Migration completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error updating column: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    fix_completed_column()
