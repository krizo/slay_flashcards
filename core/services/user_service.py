from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from collections import Counter
import datetime

from api.api_schemas import UserCreate
from core.db import models
from core.db.crud import users, sessions


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

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        """Get user by email address."""
        user = self.db.query(models.User).filter(
            models.User.email == email.lower()
        ).first()
        return user

    def create_user(self, user_data: UserCreate) -> models.User:
        """Create a new user with validation."""
        from api.utils.security import hash_password

        # Check for existing username
        if self.get_user_by_name(user_data.name):
            raise ValueError(f"Username '{user_data.name}' already exists")

        # Check for existing email
        if hasattr(user_data, 'email') and user_data.email:
            if self.get_user_by_email(user_data.email):
                raise ValueError(f"Email '{user_data.email}' already exists")

        # Create user object
        db_user = models.User(
            name=user_data.name,
            email=user_data.email.lower() if hasattr(user_data, 'email') and user_data.email else None
        )

        # Hash password if provided
        if hasattr(user_data, 'password') and user_data.password:
            db_user.password_hash = hash_password(user_data.password)

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return self.get_user_by_email(email) is not None

    def ensure_user_exists(self, name: str) -> models.User:
        """Get user or create if it doesn't exist."""
        user = self.get_user_by_name(name)
        if user:
            return user

        # Create minimal user (for backward compatibility)
        user_data = UserCreate(
            name=name,
            email=f"{name}@generated.local",
            password="GeneratedPass123"
        )
        return self.create_user(user_data)

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
                "sessions_this_month": 0,
                "unique_quizzes": 0
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
        now = datetime.datetime.now()
        week_ago = now - datetime.timedelta(days=7)
        month_ago = now - datetime.timedelta(days=30)

        sessions_this_week = len([
            s for s in user_sessions
            if s.started_at >= week_ago
        ])

        sessions_this_month = len([
            s for s in user_sessions
            if s.started_at >= month_ago
        ])

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
            "unique_quizzes": unique_quizzes
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
            if study_date == current_date or study_date == current_date - datetime.timedelta(days=1):
                streak += 1
                current_date = study_date - datetime.timedelta(days=1)
            else:
                break

        return streak
