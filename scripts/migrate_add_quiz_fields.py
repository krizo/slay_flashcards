#!/usr/bin/env python3
"""
Migration script to add 'favourite' and 'image' fields to Quiz table.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.db.database import engine
from sqlalchemy import text


def migrate():
    """Add favourite and image columns to quizzes table."""
    print("=" * 80)
    print("🔧 Database Migration: Add Quiz favourite and image fields")
    print("=" * 80)

    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()

        try:
            # Check if columns already exist
            print("\n📋 Checking existing schema...")
            result = connection.execute(text("PRAGMA table_info(quizzes)"))
            columns = [row[1] for row in result.fetchall()]

            print(f"   Found columns: {', '.join(columns)}")

            # Add favourite column if it doesn't exist
            if 'favourite' not in columns:
                print("\n➕ Adding 'favourite' column...")
                connection.execute(text(
                    "ALTER TABLE quizzes ADD COLUMN favourite BOOLEAN NOT NULL DEFAULT 0"
                ))
                print("   ✅ Column 'favourite' added successfully")
            else:
                print("\n   ℹ️  Column 'favourite' already exists")

            # Add image column if it doesn't exist
            if 'image' not in columns:
                print("\n➕ Adding 'image' column...")
                connection.execute(text(
                    "ALTER TABLE quizzes ADD COLUMN image BLOB"
                ))
                print("   ✅ Column 'image' added successfully")
            else:
                print("\n   ℹ️  Column 'image' already exists")

            # Commit transaction
            trans.commit()

            # Verify changes
            print("\n✅ Verifying schema changes...")
            result = connection.execute(text("PRAGMA table_info(quizzes)"))
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
