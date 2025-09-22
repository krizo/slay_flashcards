from sqlalchemy.orm import Session
from typing import List, Optional

from db import models
from db.crud import users, sessions


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

    def create_user(self, name: str) -> models.User:
        """Create a new user."""
        return users.create_user(self.db, name)

    def ensure_user_exists(self, name: str) -> models.User:
        """Get user or create if doesn't exist."""
        user = self.get_user_by_name(name)
        if not user:
            user = self.create_user(name)
        return user

    def create_session(self, user_id: int, quiz_id: int, mode: str, score: Optional[int] = None) -> models.Session:
        """Create a new learning/test session."""
        session = sessions.create_session(self.db, user_id, quiz_id, mode, score)
        self.db.commit()
        return session

    def get_user_sessions(self, user_id: int) -> List[models.Session]:
        """Get all sessions for a user."""
        return sessions.get_sessions_for_user(self.db, user_id)
