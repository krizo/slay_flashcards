from typing import Optional, Sequence, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, Row

from db import models
from db.crud.repository import BaseRepository
from db.models import User


class UserRepository(BaseRepository[models.User]):
    """Repository for User operations with advanced user management."""

    def __init__(self, db: Session):
        super().__init__(db, models.User)

    def get_by_name(self, name: str) -> Optional[models.User]:
        """Get user by name (case-insensitive)."""
        return self.db.execute(
            select(models.User).where(
                func.lower(models.User.name) == func.lower(name)
            )
        ).scalar_one_or_none()

    def create_user(self, name: str) -> models.User:
        """Create a new user with validation."""
        # Check if user already exists
        existing = self.get_by_name(name)
        if existing:
            raise ValueError(f"User with name '{name}' already exists")

        if not name or not name.strip():
            raise ValueError("User name cannot be empty")

        return self.create(name=name.strip())

    def ensure_exists(self, name: str) -> models.User:
        """Get user or create if it doesn't exist."""
        user = self.get_by_name(name)
        if not user:
            user = self.create(name=name.strip())
        return user

    def search_by_name_pattern(self, pattern: str) -> Sequence[User]:
        """Search users by name pattern (case-insensitive)."""
        return self.db.execute(
            select(models.User).where(
                func.lower(models.User.name).like(f"%{pattern.lower()}%")
            ).order_by(models.User.name)
        ).scalars().all()

    def get_users_with_sessions(self) -> Sequence[User]:
        """Get users who have at least one session."""
        return self.db.execute(
            select(models.User)
            .join(models.Session)
            .distinct()
            .order_by(models.User.name)
        ).scalars().all()

    def get_most_active_users(self, limit: int = 10) -> Sequence[Row[tuple[User, Any]]]:
        """Get most active users with session counts."""
        return self.db.execute(
            select(
                models.User,
                func.count(models.Session.id).label('session_count')
            )
            .join(models.Session)
            .group_by(models.User.id)
            .order_by(func.count(models.Session.id).desc())
            .limit(limit)
        ).all()

    def delete_user_and_sessions(self, user_id: int) -> bool:
        """Delete user and all associated sessions."""
        user = self.get_by_id(user_id)
        if not user:
            return False

        # Delete all user sessions first
        self.db.query(models.Session).filter(
            models.Session.user_id == user_id
        ).delete()

        # Delete user
        self.delete(user)
        return True

    def rename_user(self, user_id: int, new_name: str) -> Optional[models.User]:
        """Rename a user with validation."""
        user = self.get_by_id(user_id)
        if not user:
            return None

        # Check if new name is already taken
        existing = self.get_by_name(new_name)
        if existing and existing.id != user_id:
            raise ValueError(f"User with name '{new_name}' already exists")

        if not new_name or not new_name.strip():
            raise ValueError("User name cannot be empty")

        return self.update(user, name=new_name.strip())
