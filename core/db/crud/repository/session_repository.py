from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from core.db import models
from core.db.crud.repository import BaseRepository


class SessionRepository(BaseRepository[models.Session]):
    """Repository for Session operations with comprehensive query methods."""

    def __init__(self, db: Session):
        super().__init__(db, models.Session)

    def create_session(
        self,
        user_id: int,
        quiz_id: int,
        mode: str,
        score: Optional[int] = None
    ) -> models.Session:
        """Create a new learning/test session."""
        return self.create(
            user_id=user_id,
            quiz_id=quiz_id,
            mode=mode,
            score=score,
            started_at=datetime.now()
        )

    def get_by_user_id(self, user_id: int) -> List[models.Session]:
        """Get all sessions for a user ordered by start time (newest first)."""
        return self.db.execute(
            select(models.Session)
            .where(models.Session.user_id == user_id)
            .order_by(desc(models.Session.started_at))
        ).scalars().all()

    def get_by_quiz_id(self, quiz_id: int) -> List[models.Session]:
        """Get all sessions for a quiz ordered by start time (newest first)."""
        return self.db.execute(
            select(models.Session)
            .where(models.Session.quiz_id == quiz_id)
            .order_by(desc(models.Session.started_at))
        ).scalars().all()

    def get_by_mode(self, user_id: int, mode: str) -> List[models.Session]:
        """Get sessions by mode (learn/test) for a user."""
        return self.db.execute(
            select(models.Session).where(
                and_(
                    models.Session.user_id == user_id,
                    models.Session.mode == mode
                )
            ).order_by(desc(models.Session.started_at))
        ).scalars().all()

    def get_recent_sessions(self, user_id: int, limit: int = 10) -> List[models.Session]:
        """Get recent sessions for a user."""
        return self.db.execute(
            select(models.Session)
            .where(models.Session.user_id == user_id)
            .order_by(desc(models.Session.started_at))
            .limit(limit)
        ).scalars().all()

    def get_sessions_by_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[models.Session]:
        """Get sessions within a date range for a user."""
        return self.db.execute(
            select(models.Session).where(
                and_(
                    models.Session.user_id == user_id,
                    models.Session.started_at >= start_date,
                    models.Session.started_at <= end_date
                )
            ).order_by(desc(models.Session.started_at))
        ).scalars().all()

    def get_sessions_by_quiz_and_mode(
        self,
        quiz_id: int,
        mode: str
    ) -> List[models.Session]:
        """Get sessions for a specific quiz and mode."""
        return self.db.execute(
            select(models.Session).where(
                and_(
                    models.Session.quiz_id == quiz_id,
                    models.Session.mode == mode
                )
            ).order_by(desc(models.Session.started_at))
        ).scalars().all()

    def get_user_quiz_sessions(
        self,
        user_id: int,
        quiz_id: int
    ) -> List[models.Session]:
        """Get all sessions for a specific user and quiz combination."""
        return self.db.execute(
            select(models.Session).where(
                and_(
                    models.Session.user_id == user_id,
                    models.Session.quiz_id == quiz_id
                )
            ).order_by(desc(models.Session.started_at))
        ).scalars().all()

    def get_sessions_since_date(
        self,
        user_id: int,
        since_date: datetime
    ) -> List[models.Session]:
        """Get sessions since a specific date."""
        return self.db.execute(
            select(models.Session).where(
                and_(
                    models.Session.user_id == user_id,
                    models.Session.started_at >= since_date
                )
            ).order_by(desc(models.Session.started_at))
        ).scalars().all()

    def get_best_test_scores(
        self,
        user_id: int,
        quiz_id: Optional[int] = None,
        limit: int = 10
    ) -> List[models.Session]:
        """Get best test scores for a user, optionally filtered by quiz."""
        query = select(models.Session).where(
            and_(
                models.Session.user_id == user_id,
                models.Session.mode == "test",
                models.Session.score.is_not(None)
            )
        )

        if quiz_id:
            query = query.where(models.Session.quiz_id == quiz_id)

        return self.db.execute(
            query.order_by(desc(models.Session.score)).limit(limit)
        ).scalars().all()

    def get_session_statistics(self, user_id: int) -> dict:
        """Get comprehensive session statistics for a user."""
        all_sessions = self.get_by_user_id(user_id)

        if not all_sessions:
            return {
                "total_sessions": 0,
                "learn_sessions": 0,
                "test_sessions": 0,
                "average_score": None,
                "best_score": None,
                "total_study_time": 0,  # Could be calculated if we track end times
                "unique_quizzes": 0,
                "sessions_this_week": 0,
                "sessions_this_month": 0
            }

        learn_sessions = [s for s in all_sessions if s.mode == "learn"]
        test_sessions = [s for s in all_sessions if s.mode == "test"]

        # Calculate scores
        test_scores = [s.score for s in test_sessions if s.score is not None]
        avg_score = sum(test_scores) / len(test_scores) if test_scores else None
        best_score = max(test_scores) if test_scores else None

        # Unique quizzes
        unique_quizzes = len(set(s.quiz_id for s in all_sessions))

        # Recent activity counts
        now = datetime.now()
        week_ago = now - datetime.timedelta(days=7)
        month_ago = now - datetime.timedelta(days=30)

        sessions_this_week = len([
            s for s in all_sessions
            if s.started_at >= week_ago
        ])
        sessions_this_month = len([
            s for s in all_sessions
            if s.started_at >= month_ago
        ])

        return {
            "total_sessions": len(all_sessions),
            "learn_sessions": len(learn_sessions),
            "test_sessions": len(test_sessions),
            "average_score": avg_score,
            "best_score": best_score,
            "unique_quizzes": unique_quizzes,
            "sessions_this_week": sessions_this_week,
            "sessions_this_month": sessions_this_month
        }