#!/usr/bin/env python3
"""
Seed database with representative demo data for user Emila
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.db.database import get_db
from core.services.user_service import UserService
from core.services.quiz_service import QuizService
from core.db.models import Session
from sqlalchemy import text


def clear_existing_sessions(db, user_id: int):
    """Clear existing sessions for the user."""
    print(f"🗑️  Clearing existing sessions for user {user_id}...")
    db.query(Session).filter(Session.user_id == user_id).delete()
    db.commit()
    print("✅ Existing sessions cleared")


def create_demo_sessions(db, user_id: int):
    """Create realistic demo sessions for a user."""
    quiz_service = QuizService(db)

    # Get all quizzes
    quizzes = quiz_service.get_all_quizzes()

    if not quizzes:
        print("⚠️  No quizzes found in database.")
        return 0

    print(f"📚 Found {len(quizzes)} quizzes")

    sessions_created = 0

    # Create varied sessions over the past 30 days
    # More recent days have more sessions (simulating active learning)
    for days_ago in range(30):
        # More activity in recent days
        if days_ago < 7:
            num_sessions = random.randint(2, 5)  # Very active last week
        elif days_ago < 14:
            num_sessions = random.randint(1, 3)  # Active
        else:
            num_sessions = random.randint(0, 2)  # Less active in the past

        for _ in range(num_sessions):
            quiz = random.choice(quizzes)

            # 70% learn mode, 30% test mode (realistic ratio)
            mode = 'learn' if random.random() < 0.7 else 'test'

            # Generate realistic scores
            if mode == 'test':
                # Test scores: improving over time
                base_score = 70 + (30 - days_ago) * 0.5  # Better scores as we go forward
                score = min(100, max(60, int(base_score + random.uniform(-10, 15))))
            else:
                score = None  # Learn mode doesn't have scores

            # Create session at a realistic time
            started_at = datetime.now() - timedelta(
                days=days_ago,
                hours=random.randint(8, 22),  # Between 8 AM and 10 PM
                minutes=random.randint(0, 59)
            )

            # Session duration: 5-30 minutes
            completed_at = started_at + timedelta(minutes=random.randint(5, 30))

            # Create session
            session = Session(
                user_id=user_id,
                quiz_id=quiz.id,
                mode=mode,
                started_at=started_at,
                completed_at=completed_at,
                score=score
            )

            db.add(session)
            sessions_created += 1

    db.commit()
    print(f"✅ Created {sessions_created} demo sessions")
    return sessions_created


def print_statistics(db, user_id: int):
    """Print statistics about the created data."""
    print("\n" + "="*80)
    print("📊 DEMO DATA STATISTICS")
    print("="*80)

    # Total sessions
    total = db.query(Session).filter(Session.user_id == user_id).count()
    print(f"\n📈 Total Sessions: {total}")

    # Learn vs Test
    learn = db.query(Session).filter(
        Session.user_id == user_id,
        Session.mode == 'learn'
    ).count()
    test = db.query(Session).filter(
        Session.user_id == user_id,
        Session.mode == 'test'
    ).count()
    print(f"📖 Learn Sessions: {learn}")
    print(f"✅ Test Sessions: {test}")

    # Score statistics
    scores = db.execute(
        text("""
            SELECT AVG(score) as avg_score, MIN(score) as min_score, MAX(score) as max_score
            FROM sessions
            WHERE user_id = :user_id AND score IS NOT NULL
        """),
        {"user_id": user_id}
    ).fetchone()

    if scores and scores[0]:
        print(f"\n🎯 Average Score: {scores[0]:.1f}%")
        print(f"📉 Lowest Score: {scores[1]}%")
        print(f"📈 Highest Score: {scores[2]}%")

    # Sessions by week
    sessions_last_7 = db.execute(
        text("""
            SELECT COUNT(*)
            FROM sessions
            WHERE user_id = :user_id
            AND started_at >= datetime('now', '-7 days')
        """),
        {"user_id": user_id}
    ).scalar()

    sessions_last_30 = db.execute(
        text("""
            SELECT COUNT(*)
            FROM sessions
            WHERE user_id = :user_id
            AND started_at >= datetime('now', '-30 days')
        """),
        {"user_id": user_id}
    ).scalar()

    print(f"\n📅 Sessions (Last 7 days): {sessions_last_7}")
    print(f"📅 Sessions (Last 30 days): {sessions_last_30}")

    print("\n" + "="*80)


def main():
    """Main function to seed demo data."""
    print("🚀 Seeding demo data for SlayFlashcards...\n")

    db = next(get_db())

    try:
        user_service = UserService(db)

        # Get user
        user = user_service.get_user_by_name("Emila")

        if not user:
            print("❌ User 'Emila' not found!")
            return

        print(f"✅ Found user: {user.name} (id: {user.id})\n")

        # Clear existing sessions
        clear_existing_sessions(db, user.id)

        # Create new demo sessions
        print("\n📊 Creating demo sessions...")
        sessions_created = create_demo_sessions(db, user.id)

        # Print statistics
        print_statistics(db, user.id)

        print("\n✅ Demo data seeded successfully!")
        print("\n💡 Tip: Restart the frontend dev server (npm run dev) to see the new data")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
