from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List

from core.db import models


def get_users(db: Session) -> List[models.User]:
    return db.execute(select(models.User)).scalars().all()


def get_user_by_name(db: Session, name: str) -> Optional[models.User]:
    return db.execute(
        select(models.User).where(models.User.name == name)
    ).scalar_one_or_none()


def create_user(db: Session, name: str) -> models.User:
    user = models.User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user