#!/usr/bin/env python3
"""
Migration script to add 'completed' field to Session table.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.db.database import engine
from sqlalchemy import text


def migrate():
    """Add completed column to sessions table."""
    print("=" * 80)
    print("🔧 Database Migration: Add Session completed field")
    print("=" * 80)

    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()

        try:
            # Check if column already exists
            print("\n📋 Checking existing schema...")
            result = connection.execute(text("PRAGMA table_info(sessions)"))
            columns = [row[1] for row in result.fetchall()]

            print(f"   Found columns: {', '.join(columns)}")

            # Add completed column if it doesn't exist
            if 'completed' not in columns:
                print("\n➕ Adding 'completed' column...")
                connection.execute(text(
                    "ALTER TABLE sessions ADD COLUMN completed BOOLEAN NOT NULL DEFAULT 0"
                ))
                print("   ✅ Column 'completed' added successfully")

                # Update existing sessions: mark as completed if they have completed_at set
                print("\n📝 Updating existing sessions...")
                result = connection.execute(text(
                    "UPDATE sessions SET completed = 1 WHERE completed_at IS NOT NULL"
                ))
                rows_updated = result.rowcount
                print(f"   ✅ Updated {rows_updated} existing sessions to completed=true")
            else:
                print("\n   ℹ️  Column 'completed' already exists")

            # Commit transaction
            trans.commit()

            # Verify changes
            print("\n✅ Verifying schema changes...")
            result = connection.execute(text("PRAGMA table_info(sessions)"))
            updated_columns = [row[1] for row in result.fetchall()]
            print(f"   Updated columns: {', '.join(updated_columns)}")

            print("\n" + "=" * 80)
            print("✅ Migration completed successfully!")
            print("=" * 80)

        except Exception as e:
            trans.rollback()
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    migrate()
