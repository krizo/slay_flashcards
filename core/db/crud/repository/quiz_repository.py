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
        user_id: int,
        subject: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> models.Quiz:
        """
        Create a new quiz.

        Args:
            name: Quiz name
            user_id: ID of the user who owns this quiz
            subject: Optional subject/category
            category: Optional category within subject (e.g., "Poland" within "Geography")
            level: Optional level of advancement (e.g., "Beginner", "Class 5")
            description: Optional description
            created_at: Optional creation timestamp

        Returns:
            Created quiz instance
        """
        return self.create(
            name=name,
            user_id=user_id,
            subject=subject,
            category=category,
            level=level,
            description=description,
            created_at=created_at or datetime.utcnow()
        )

    # =========================================================================
    # QUIZ LOOKUP METHODS
    # =========================================================================

    def get_by_user_id(self, user_id: int) -> Sequence[models.Quiz]:
        """
        Get all quizzes owned by a specific user.

        Args:
            user_id: User ID

        Returns:
            List of quizzes owned by the user
        """
        return self._execute_query(
            select(models.Quiz).where(models.Quiz.user_id == user_id).order_by(models.Quiz.created_at.desc())
        )

    def get_by_ids(self, quiz_ids: list[int]) -> Sequence[models.Quiz]:
        """
        Get multiple quizzes by their IDs in a single query.

        Args:
            quiz_ids: List of quiz IDs

        Returns:
            List of quiz instances
        """
        if not quiz_ids:
            return []
        return self._execute_query(
            select(models.Quiz).where(models.Quiz.id.in_(quiz_ids))
        )

    def get_by_name(self, name: str) -> Optional[models.Quiz]:
        """
        Get quiz by exact name (case-sensitive).

        Args:
            name: Quiz name

        Returns:
            Quiz instance or None if not found
        """
        return self._execute_single(select(models.Quiz).where(models.Quiz.name == name))

    def get_by_subject(self, subject: str, user_id: Optional[int] = None) -> Sequence[models.Quiz]:
        """
        Get all quizzes for a specific subject.

        Args:
            subject: Subject/category name
            user_id: Optional user ID to filter by

        Returns:
            List of quizzes in that subject
        """
        query = select(models.Quiz).where(models.Quiz.subject == subject)
        if user_id is not None:
            query = query.where(models.Quiz.user_id == user_id)
        return self._execute_query(query.order_by(models.Quiz.name))

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

    def get_by_category(self, category: str, user_id: Optional[int] = None) -> Sequence[models.Quiz]:
        """
        Get all quizzes for a specific category.

        Args:
            category: Category name
            user_id: Optional user ID to filter by

        Returns:
            List of quizzes in that category
        """
        query = select(models.Quiz).where(models.Quiz.category == category)
        if user_id is not None:
            query = query.where(models.Quiz.user_id == user_id)
        return self._execute_query(query.order_by(models.Quiz.name))

    def get_by_level(self, level: str, user_id: Optional[int] = None) -> Sequence[models.Quiz]:
        """
        Get all quizzes for a specific level.

        Args:
            level: Level name
            user_id: Optional user ID to filter by

        Returns:
            List of quizzes at that level
        """
        query = select(models.Quiz).where(models.Quiz.level == level)
        if user_id is not None:
            query = query.where(models.Quiz.user_id == user_id)
        return self._execute_query(query.order_by(models.Quiz.name))

    def get_all_categories(self, user_id: Optional[int] = None) -> Sequence[str]:
        """
        Get list of all unique categories.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of category names
        """
        query = (
            select(models.Quiz.category)
            .where(models.Quiz.category.is_not(None))
            .distinct()
            .order_by(models.Quiz.category)
        )
        if user_id is not None:
            query = query.where(models.Quiz.user_id == user_id)

        results = self.db.execute(query).scalars().all()
        return results

    def get_all_levels(self, user_id: Optional[int] = None) -> Sequence[str]:
        """
        Get list of all unique levels.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of level names
        """
        query = (
            select(models.Quiz.level)
            .where(models.Quiz.level.is_not(None))
            .distinct()
            .order_by(models.Quiz.level)
        )
        if user_id is not None:
            query = query.where(models.Quiz.user_id == user_id)

        results = self.db.execute(query).scalars().all()
        return results
