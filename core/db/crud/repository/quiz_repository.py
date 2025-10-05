"""
Quiz repository for managing quiz entities and related operations.

Provides quiz-specific queries, validation, and statistics.
"""

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select  # pylint: disable=import-error
from sqlalchemy.orm import Session  # pylint: disable=import-error

from core.db import models
from core.db.crud.repository import BaseRepository


class QuizRepository(BaseRepository[models.Quiz]):
    """
    Repository for Quiz database operations.

    Provides methods for:
    - Quiz creation and management
    - Quiz search and lookup
    - Subject-based filtering
    """

    def __init__(self, db: Session):
        """
        Initialize quiz repository.

        Args:
            db: SQLAlchemy database session
        """
        super().__init__(db, models.Quiz)

    # =========================================================================
    # QUIZ CREATION METHODS
    # =========================================================================

    def create_quiz(
        self,
        name: str,
        subject: Optional[str] = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> models.Quiz:
        """
        Create a new quiz.

        Args:
            name: Quiz name
            subject: Optional subject/category
            description: Optional description
            created_at: Optional creation timestamp

        Returns:
            Created quiz instance
        """
        return self.create(
            name=name, subject=subject, description=description, created_at=created_at or datetime.utcnow()
        )

    # =========================================================================
    # QUIZ LOOKUP METHODS
    # =========================================================================

    def get_by_name(self, name: str) -> Optional[models.Quiz]:
        """
        Get quiz by exact name (case-sensitive).

        Args:
            name: Quiz name

        Returns:
            Quiz instance or None if not found
        """
        return self._execute_single(select(models.Quiz).where(models.Quiz.name == name))

    def get_by_subject(self, subject: str) -> Sequence[models.Quiz]:
        """
        Get all quizzes for a specific subject.

        Args:
            subject: Subject/category name

        Returns:
            List of quizzes in that subject
        """
        return self._execute_query(select(models.Quiz).where(models.Quiz.subject == subject).order_by(models.Quiz.name))

    # =========================================================================
    # QUIZ SEARCH METHODS
    # =========================================================================

    def search_by_name(self, name_pattern: str) -> Sequence[models.Quiz]:
        """
        Search quizzes by name pattern (case-insensitive).

        Args:
            name_pattern: Search pattern

        Returns:
            List of matching quizzes
        """
        return self._execute_query(
            select(models.Quiz).where(models.Quiz.name.ilike(f"%{name_pattern}%")).order_by(models.Quiz.name)
        )

    def get_all_subjects(self) -> Sequence[str]:
        """
        Get list of all unique subjects.

        Returns:
            List of subject names
        """
        results = (
            self.db.execute(
                select(models.Quiz.subject)
                .where(models.Quiz.subject.is_not(None))
                .distinct()
                .order_by(models.Quiz.subject)
            )
            .scalars()
            .all()
        )

        return results
