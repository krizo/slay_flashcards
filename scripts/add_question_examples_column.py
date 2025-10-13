#!/usr/bin/env python3
"""
Migration script to add question_examples column to flashcards table.

This script safely adds the new question_examples JSON column to the flashcards table
if it doesn't already exist.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect, text  # pylint: disable=import-error

from core.db.database import engine


def column_exists(table_name: str, column_name: str) -> bool:
    """
    Check if a column exists in a table.

    Args:
        table_name: Name of the table
        column_name: Name of the column

    Returns:
        True if column exists, False otherwise
    """
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def add_question_examples_column():
    """Add question_examples column to flashcards table if it doesn't exist."""
    table_name = "flashcards"
    column_name = "question_examples"

    print("=" * 80)
    print("🔧 Database Migration: Add question_examples column")
    print("=" * 80)
    print()

    # Check if column already exists
    if column_exists(table_name, column_name):
        print(f"✅ Column '{column_name}' already exists in '{table_name}' table.")
        print("   No migration needed.")
        return

    print(f"📝 Adding column '{column_name}' to '{table_name}' table...")

    try:
        # SQLite specific syntax for adding column
        with engine.begin() as conn:
            conn.execute(
                text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} JSON")
            )

        print(f"✅ Successfully added column '{column_name}' to '{table_name}' table.")
        print()
        print("=" * 80)
        print("✅ Migration completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error adding column: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    add_question_examples_column()
