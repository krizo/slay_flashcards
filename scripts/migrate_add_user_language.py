"""
Migration script to add language column to users table.

This script adds a 'language' column to the users table to store user's preferred language.
Default value is 'en' (English).
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text, inspect
from core.db.database import get_db, engine


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate():
    """Add language column to users table."""

    # Check if column already exists
    if column_exists('users', 'language'):
        print("✓ Column 'language' already exists in users table. Skipping migration.")
        return

    print("Adding 'language' column to users table...")

    # Get database session
    db = next(get_db())

    try:
        # Add language column with default value 'en'
        db.execute(text("""
            ALTER TABLE users
            ADD COLUMN language VARCHAR(10) NOT NULL DEFAULT 'en'
        """))

        db.commit()
        print("✓ Successfully added 'language' column to users table")
        print("  - Type: VARCHAR(10)")
        print("  - Default: 'en'")
        print("  - Not Null: True")

    except Exception as e:
        db.rollback()
        print(f"✗ Error during migration: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add language column to users table")
    print("=" * 60)
    migrate()
    print("=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)
