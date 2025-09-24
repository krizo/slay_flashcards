from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from core.db import models
from core.db.crud.repository import BaseRepository


class QuizRepository(BaseRepository[models.Quiz]):
    """Repository for Quiz operations."""

    def __init__(self, db: Session):
        super().__init__(db, models.Quiz)

    def create_quiz(
            self,
            name: str,
            subject: Optional[str] = None,
            description: Optional[str] = None,
            created_at: Optional[datetime] = None
    ) -> models.Quiz:
        """Create a new quiz."""
        return self.create(
            name=name,
            subject=subject,
            description=description,
            created_at=created_at or datetime.utcnow()
        )

    def get_by_subject(self, subject: str) -> List[models.Quiz]:
        """Get all quizzes for a specific subject."""
        return self.db.execute(
            select(models.Quiz).where(models.Quiz.subject == subject)
        ).scalars().all()

    def search_by_name(self, name_pattern: str) -> List[models.Quiz]:
        """Search quizzes by name pattern."""
        return self.db.execute(
            select(models.Quiz).where(models.Quiz.name.ilike(f"%{name_pattern}%"))
        ).scalars().all()
