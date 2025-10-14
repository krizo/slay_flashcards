#!/usr/bin/env python3
"""
Intelligent database migration script for SlayFlashcards.

This script:
- Checks if there are pending migrations
- Runs migrations only if needed
- Provides detailed logging
- Handles errors gracefully
- Is safe for CI/CD environments
"""

import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

# Ensure we can import from project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.db.database import DATABASE_URL, engine


def get_current_revision():
    """Get the current database revision."""
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
    except Exception as e:
        print(f"⚠️  Warning: Could not get current revision: {e}")
        return None


def get_head_revision():
    """Get the latest migration revision from migration files."""
    try:
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        return script.get_current_head()
    except Exception as e:
        print(f"❌ Error: Could not get head revision: {e}")
        return None


def check_if_migrations_needed():
    """
    Check if migrations are needed.

    Returns:
        tuple: (needs_migration: bool, current_rev: str, head_rev: str)
    """
    current = get_current_revision()
    head = get_head_revision()

    # If current is None, the alembic_version table doesn't exist yet
    # This means we need to stamp the database
    needs_migration = current != head

    return needs_migration, current, head


def check_database_exists():
    """Check if the database file/tables exist."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return len(tables) > 0
    except Exception:
        return False


def run_migrations():
    """Run database migrations intelligently."""
    print("=" * 60)
    print("🔄 SlayFlashcards Database Migration Script")
    print("=" * 60)

    # Check database URL
    print(f"\n📊 Database URL: {DATABASE_URL}")

    # Check if database exists
    db_exists = check_database_exists()
    print(f"📁 Database exists: {'Yes' if db_exists else 'No'}")

    # Check for pending migrations
    print("\n🔍 Checking for pending migrations...")
    needs_migration, current_rev, head_rev = check_if_migrations_needed()

    print(f"   Current revision: {current_rev or 'None (new database)'}")
    print(f"   Latest revision:  {head_rev or 'None (no migrations)'}")

    if not head_rev:
        print("\n⚠️  No migration files found!")
        print("   This is expected if no schema changes have been made yet.")
        print("   To create initial migration, run:")
        print("   .venv/bin/alembic revision --autogenerate -m 'Initial migration'")
        return 0

    if not needs_migration:
        print("\n✅ Database is up to date! No migrations needed.")
        return 0

    print("\n🚀 Migrations needed! Running migrations...")

    try:
        # Load alembic configuration
        alembic_cfg = Config("alembic.ini")

        if current_rev is None and not db_exists:
            # Brand new database - run all migrations
            print("   Running all migrations (new database)...")
            command.upgrade(alembic_cfg, "head")
        elif current_rev is None and db_exists:
            # Database exists but no alembic_version table
            # This happens when migrating from create_all() to Alembic
            print("   Stamping existing database...")
            command.stamp(alembic_cfg, "head")
        else:
            # Normal migration - upgrade from current to head
            print(f"   Upgrading from {current_rev} to {head_rev}...")
            command.upgrade(alembic_cfg, "head")

        print("\n✅ Migrations completed successfully!")

        # Verify migration
        new_current = get_current_revision()
        if new_current == head_rev:
            print(f"✅ Database is now at revision: {new_current}")
        else:
            print(f"⚠️  Warning: Expected revision {head_rev}, but database is at {new_current}")
            return 1

        return 0

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    try:
        exit_code = run_migrations()
        print("\n" + "=" * 60)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
