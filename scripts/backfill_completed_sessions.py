#!/usr/bin/env python3
"""
Backfill script to mark all existing sessions as completed.
This is needed because the completed field was added after sessions were created.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.db.database import engine
from sqlalchemy import text


def backfill_completed_sessions():
    """Mark existing sessions as completed based on completed_at or score."""
    print("=" * 80)
    print("🔧 Backfilling completed status for existing sessions")
    print("=" * 80)

    with engine.connect() as connection:
        trans = connection.begin()

        try:
            # Check current state
            print("\n📋 Current session status:")
            result = connection.execute(text(
                "SELECT COUNT(*) as total, "
                "SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed, "
                "SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END) as incomplete "
                "FROM sessions"
            ))
            stats = result.fetchone()
            print(f"   Total sessions: {stats[0]}")
            print(f"   Completed: {stats[1]}")
            print(f"   Incomplete: {stats[2]}")

            # Strategy 1: Mark sessions with completed_at as completed
            print("\n📝 Marking sessions with completed_at timestamp as completed...")
            result = connection.execute(text(
                "UPDATE sessions SET completed = 1 "
                "WHERE completed_at IS NOT NULL AND completed = 0"
            ))
            rows_updated = result.rowcount
            print(f"   ✅ Updated {rows_updated} sessions based on completed_at")

            # Strategy 2: Mark test sessions with score as completed
            print("\n📝 Marking test sessions with score as completed...")
            result = connection.execute(text(
                "UPDATE sessions SET completed = 1 "
                "WHERE mode = 'test' AND score IS NOT NULL AND completed = 0"
            ))
            rows_updated = result.rowcount
            print(f"   ✅ Updated {rows_updated} test sessions based on score")

            # Strategy 3: Mark older learn sessions (more than 5 minutes old) as completed
            # This assumes if a learn session was started more than 5 minutes ago, it's either
            # completed or abandoned
            print("\n📝 Marking old learn sessions as completed...")
            result = connection.execute(text(
                "UPDATE sessions SET completed = 1 "
                "WHERE mode = 'learn' "
                "AND completed = 0 "
                "AND datetime(started_at) < datetime('now', '-5 minutes')"
            ))
            rows_updated = result.rowcount
            print(f"   ✅ Updated {rows_updated} old learn sessions")

            # Commit transaction
            trans.commit()

            # Show final state
            print("\n✅ Final session status:")
            result = connection.execute(text(
                "SELECT COUNT(*) as total, "
                "SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed, "
                "SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END) as incomplete "
                "FROM sessions"
            ))
            stats = result.fetchone()
            print(f"   Total sessions: {stats[0]}")
            print(f"   Completed: {stats[1]}")
            print(f"   Incomplete: {stats[2]}")

            print("\n" + "=" * 80)
            print("✅ Backfill completed successfully!")
            print("=" * 80)

        except Exception as e:
            trans.rollback()
            print(f"\n❌ Backfill failed: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    backfill_completed_sessions()
