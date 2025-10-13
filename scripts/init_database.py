#!/usr/bin/env python3
"""
Initialize database for deployment.

This script handles database initialization with options to:
- Create tables if they don't exist
- Optionally reset (drop and recreate) the database
- Optionally create demo data
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.db.database import Base, engine, init_database, reset_database


def create_demo_data_wrapper():
    """Create demo data by calling the existing create_demo_data script."""
    from scripts.create_demo_data import main as create_demo_data_main

    # Temporarily override input() to auto-accept (no reset since already done)
    original_input = __builtins__.__dict__['input']
    __builtins__.__dict__['input'] = lambda prompt: 'no'

    try:
        create_demo_data_main()
    finally:
        # Restore original input function
        __builtins__.__dict__['input'] = original_input


def main():
    """Main function to initialize database."""
    parser = argparse.ArgumentParser(description='Initialize SlayFlashcards database')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset database (drop and recreate all tables)'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo data after initialization'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🗄️  SlayFlashcards Database Initialization")
    print("=" * 80)

    try:
        if args.reset:
            print("\n⚠️  RESETTING DATABASE - All data will be lost!")
            reset_database()
        else:
            print("\nInitializing database (creating tables if not exist)...")
            init_database()

        if args.demo:
            print("\n📊 Creating demo data...")
            create_demo_data_wrapper()

        print("\n" + "=" * 80)
        print("✅ Database initialization complete!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during database initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
