from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from core.db import models


def get_quizzes(db: Session) -> List[models.Quiz]:
    return db.execute(select(models.Quiz)).scalars().all()


def get_quiz(db: Session, quiz_id: int) -> Optional[models.Quiz]:
    return db.get(models.Quiz, quiz_id)


def create_quiz(db: Session, name: str, subject: str, description: str = None, created_at: datetime = None) -> models.Quiz:
    quiz = models.Quiz(
        name=name,
        subject=subject,
        description=description,
        created_at=created_at or datetime.utcnow(),
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz