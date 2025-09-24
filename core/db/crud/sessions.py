from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from core.db import models


def create_session(db: Session, user_id: int, quiz_id: int, mode: str, score: Optional[int] = None) -> models.Session:
    session = models.Session(
        user_id=user_id,
        quiz_id=quiz_id,
        mode=mode,
        score=score,
        started_at=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_sessions_for_user(db: Session, user_id: int) -> List[models.Session]:
    return db.execute(
        select(models.Session).where(models.Session.user_id == user_id)
    ).scalars().all()
