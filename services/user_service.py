from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from collections import Counter
from datetime import datetime, timedelta

from db import models
from db.crud import users, sessions


class UserService:
    """Service for managing users and their sessions."""

    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self) -> List[models.User]:
        """Get all users."""
        return users.get_users(self.db)

    def get_user_by_name(self, name: str) -> Optional[models.User]:
        """Get user by name."""
        return users.get_user_by_name(self.db, name)

    def create_user(self, name: str) -> models.User:
        """Create a new user."""
        return users.create_user(self.db, name)

    def ensure_user_exists(self, name: str) -> models.User:
        """Get user or create if it doesn't exist."""
        user = self.get_user_by_name(name)
        if not user:
            user = self.create_user(name)
        return user

    def create_session(self, user_id: int, quiz_id: int, mode: str, score: Optional[int] = None) -> models.Session:
        """Create a new learning/test session."""
        session = sessions.create_session(self.db, user_id, quiz_id, mode, score)
        return session

    def get_user_sessions(self, user_id: int) -> List[models.Session]:
        """Get all sessions for a user."""
        return sessions.get_sessions_for_user(self.db, user_id)

    def get_sessions_by_mode(self, user_id: int, mode: str) -> List[models.Session]:
        """Get sessions filtered by mode."""
        user_sessions = self.get_user_sessions(user_id)
        return [session for session in user_sessions if session.mode == mode]

    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a user."""
        user_sessions = self.get_user_sessions(user_id)

        if not user_sessions:
            return {
                "total_sessions": 0,
                "learn_sessions": 0,
                "test_sessions": 0,
                "average_score": None,
                "best_score": None,
                "study_streak": 0,
                "favorite_subjects": [],
                "sessions_this_week": 0,
                "sessions_this_month": 0
            }

        learn_sessions = [s for s in user_sessions if s.mode == "learn"]
        test_sessions = [s for s in user_sessions if s.mode == "test"]

        # Calculate scores
        test_scores = [s.score for s in test_sessions if s.score is not None]
        avg_score = sum(test_scores) / len(test_scores) if test_scores else None
        best_score = max(test_scores) if test_scores else None

        # Calculate favorite subjects
        subject_counts = Counter()
        for session in user_sessions:
            if session.quiz and session.quiz.subject:
                subject_counts[session.quiz.subject] += 1

        favorite_subjects = [
            {"subject": subject, "count": count}
            for subject, count in subject_counts.most_common(5)
        ]

        # Calculate study streak (consecutive days with sessions)
        study_streak = self._calculate_study_streak(user_sessions)

        # Calculate recent activity
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        sessions_this_week = len([
            s for s in user_sessions
            if s.started_at >= week_ago
        ])

        sessions_this_month = len([
            s for s in user_sessions
            if s.started_at >= month_ago
        ])

        return {
            "total_sessions": len(user_sessions),
            "learn_sessions": len(learn_sessions),
            "test_sessions": len(test_sessions),
            "average_score": avg_score,
            "best_score": best_score,
            "study_streak": study_streak,
            "favorite_subjects": favorite_subjects,
            "sessions_this_week": sessions_this_week,
            "sessions_this_month": sessions_this_month
        }

    @staticmethod
    def _calculate_study_streak(user_sessions: List[models.Session]) -> int:
        """Calculate consecutive days with study sessions."""
        if not user_sessions:
            return 0

        # Get unique study dates
        study_dates = set()
        for session in user_sessions:
            study_dates.add(session.started_at.date())

        if not study_dates:
            return 0

        # Sort dates in descending order
        sorted_dates = sorted(study_dates, reverse=True)

        # Check for consecutive days starting from most recent
        streak = 0
        current_date = datetime.now().date()

        for study_date in sorted_dates:
            if study_date == current_date or study_date == current_date - timedelta(days=1):
                streak += 1
                current_date = study_date - timedelta(days=1)
            else:
                break

        return streak
