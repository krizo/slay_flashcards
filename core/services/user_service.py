# pylint: disable=cyclic-import
"""
User service for business logic related to users and sessions.

Provides high-level operations that combine repository calls.
"""

import datetime
from collections import Counter
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy.orm import Session  # pylint: disable=import-error

from api.api_schemas import UserCreate
from core.db import models  # pylint: disable=cyclic-import
from core.db.crud.repository.session_repository import SessionRepository  # pylint: disable=cyclic-import
from core.db.crud.repository.user_repository import UserRepository  # pylint: disable=cyclic-import


class UserService:
    """
    Service for managing users and their sessions.

    Provides high-level business logic operations using repositories.
    """

    def __init__(self, db: Session):
        """
        Initialize user service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)

    # =========================================================================
    # USER OPERATIONS
    # =========================================================================

    def get_all_users(self) -> Sequence[models.User]:
        """Get all users."""
        return self.user_repo.get_all()

    def get_user_by_name(self, name: str) -> Optional[models.User]:
        """Get user by name."""
        return self.user_repo.get_by_name(name)

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        """Get user by email address."""
        return self.user_repo.get_by_email(email)

    def create_user(self, user_data: UserCreate) -> models.User:
        """Create a new user with validation."""
        from api.utils.security import hash_password  # pylint: disable=import-outside-toplevel

        # Hash password if provided
        password_hash = None
        if hasattr(user_data, "password") and user_data.password:
            password_hash = hash_password(user_data.password)

        # Use repository create_user which handles validation
        return self.user_repo.create_user(name=user_data.name, email=user_data.email, password_hash=password_hash)

    def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return self.user_repo.exists_by_email(email)

    def ensure_user_exists(self, name: str) -> models.User:
        """Get user or create if it doesn't exist."""
        return self.user_repo.ensure_user_exists(name)

    # =========================================================================
    # SESSION OPERATIONS
    # =========================================================================

    def create_session(self, user_id: int, quiz_id: int, mode: str, score: Optional[int] = None) -> models.Session:
        """Create a new learning/test session."""
        return self.session_repo.create_session(user_id, quiz_id, mode, score)

    def get_user_sessions(self, user_id: int) -> Sequence[models.Session]:
        """Get all sessions for a user."""
        return self.session_repo.get_by_user_id(user_id)

    def get_sessions_by_mode(self, user_id: int, mode: str) -> List[models.Session]:
        """Get sessions filtered by mode."""
        user_sessions = self.get_user_sessions(user_id)
        return [session for session in user_sessions if session.mode == mode]

    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:  # pylint: disable=too-many-locals
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
                "sessions_this_month": 0,
                "unique_quizzes": 0,
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

        favorite_subjects = [{"subject": subject, "count": count} for subject, count in subject_counts.most_common(5)]

        # Calculate study streak (consecutive days with sessions)
        study_streak = self._calculate_study_streak(user_sessions)

        # Calculate recent activity
        now = datetime.datetime.now()
        week_ago = now - datetime.timedelta(days=7)
        month_ago = now - datetime.timedelta(days=30)

        sessions_this_week = len([s for s in user_sessions if s.started_at >= week_ago])

        sessions_this_month = len([s for s in user_sessions if s.started_at >= month_ago])

        # Calculate unique quizzes
        unique_quizzes = len(set(s.quiz_id for s in user_sessions))

        return {
            "total_sessions": len(user_sessions),
            "learn_sessions": len(learn_sessions),
            "test_sessions": len(test_sessions),
            "average_score": avg_score,
            "best_score": best_score,
            "study_streak": study_streak,
            "favorite_subjects": favorite_subjects,
            "sessions_this_week": sessions_this_week,
            "sessions_this_month": sessions_this_month,
            "unique_quizzes": unique_quizzes,
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
        current_date = datetime.datetime.now().date()

        for study_date in sorted_dates:
            if study_date == current_date or study_date == current_date - datetime.timedelta(days=1):  # pylint: disable=consider-using-in
                streak += 1
                current_date = study_date - datetime.timedelta(days=1)
            else:
                break

        return streak
