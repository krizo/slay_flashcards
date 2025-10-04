"""
User repository for managing user entities and related operations.

Provides user-specific queries, validation, and statistics.
"""
from typing import Optional, Sequence, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta

from core.db import models
from core.db.crud.repository import BaseRepository


class UserRepository(BaseRepository[models.User]):
    """
    Repository for User database operations.
    
    Provides methods for:
    - User creation and management with validation
    - User search and lookup
    - Activity tracking and statistics
    - User-session relationships
    """

    def __init__(self, db: Session):
        """
        Initialize user repository.
        
        Args:
            db: SQLAlchemy database session
        """
        super().__init__(db, models.User)

    # =========================================================================
    # USER LOOKUP METHODS
    # =========================================================================

    def get_by_name(self, name: str) -> Optional[models.User]:
        """
        Get user by username (case-insensitive).
        
        Args:
            name: Username to search for
            
        Returns:
            User instance or None if not found
        """
        return self._execute_single(
            select(models.User).where(
                func.lower(models.User.name) == func.lower(name)
            )
        )

    def get_by_email(self, email: str) -> Optional[models.User]:
        """
        Get user by email address (case-insensitive).
        
        Args:
            email: Email address to search for
            
        Returns:
            User instance or None if not found
        """
        return self._execute_single(
            select(models.User).where(
                func.lower(models.User.email) == func.lower(email)
            )
        )

    def exists_by_name(self, name: str) -> bool:
        """
        Check if username exists.
        
        Args:
            name: Username to check
            
        Returns:
            True if username exists, False otherwise
        """
        return self.get_by_name(name) is not None

    def exists_by_email(self, email: str) -> bool:
        """
        Check if email exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if email exists, False otherwise
        """
        return self.get_by_email(email) is not None

    # =========================================================================
    # USER CREATION WITH VALIDATION
    # =========================================================================

    def create_user(
        self, 
        name: str, 
        email: str, 
        password_hash: Optional[str] = None
    ) -> models.User:
        """
        Create a new user with validation.
        
        Args:
            name: Username (will be trimmed)
            email: Email address (will be lowercased)
            password_hash: Hashed password (optional)
            
        Returns:
            Created user instance
            
        Raises:
            ValueError: If validation fails or user already exists
        """
        # Validate and normalize inputs
        name = name.strip()
        email = email.lower().strip()
        
        if not name:
            raise ValueError("Username cannot be empty")
        
        if not email:
            raise ValueError("Email cannot be empty")
        
        # Check for existing user
        if self.exists_by_name(name):
            raise ValueError(f"Username '{name}' already exists")
        
        if self.exists_by_email(email):
            raise ValueError(f"Email '{email}' already exists")
        
        # Create user
        return self.create(
            name=name,
            email=email,
            password_hash=password_hash,
            created_at=datetime.now()
        )

    def ensure_user_exists(self, name: str, email: Optional[str] = None) -> models.User:
        """
        Get user by name or create if doesn't exist.
        
        Args:
            name: Username
            email: Email (generated if not provided)
            
        Returns:
            Existing or newly created user instance
        """
        user = self.get_by_name(name)
        if user:
            return user
        
        # Generate email if not provided
        if not email:
            email = f"{name.lower()}@generated.local"
        
        return self.create_user(name, email)

    # =========================================================================
    # USER SEARCH METHODS
    # =========================================================================

    def search_by_name_pattern(self, pattern: str) -> Sequence[models.User]:
        """
        Search users by name pattern (case-insensitive).
        
        Args:
            pattern: Search pattern (can include wildcards)
            
        Returns:
            List of matching users ordered by name
        """
        return self._execute_query(
            select(models.User)
            .where(func.lower(models.User.name).like(f"%{pattern.lower()}%"))
            .order_by(models.User.name)
        )

    def search_by_email_pattern(self, pattern: str) -> Sequence[models.User]:
        """
        Search users by email pattern (case-insensitive).
        
        Args:
            pattern: Search pattern
            
        Returns:
            List of matching users
        """
        return self._execute_query(
            select(models.User)
            .where(func.lower(models.User.email).like(f"%{pattern.lower()}%"))
            .order_by(models.User.email)
        )

    # =========================================================================
    # USER ACTIVITY QUERIES
    # =========================================================================

    def get_users_with_sessions(self) -> Sequence[models.User]:
        """
        Get users who have at least one session.
        
        Returns:
            List of users with sessions
        """
        return self._execute_query(
            select(models.User)
            .join(models.Session)
            .distinct()
            .order_by(models.User.name)
        )

    def get_most_active_users(
        self, 
        limit: int = 10,
        days: Optional[int] = None
    ) -> Sequence[Tuple[models.User, int]]:
        """
        Get most active users with session counts.
        
        Args:
            limit: Maximum number of users to return
            days: Optional filter for recent activity (e.g., last 30 days)
            
        Returns:
            List of (user, session_count) tuples
        """
        query = (
            select(
                models.User,
                func.count(models.Session.id).label('session_count')
            )
            .join(models.Session)
        )
        
        # Filter by date if specified
        if days:
            since_date = datetime.now() - timedelta(days=days)
            query = query.where(models.Session.started_at >= since_date)
        
        query = (
            query
            .group_by(models.User.id)
            .order_by(desc(func.count(models.Session.id)))
            .limit(limit)
        )
        
        return self.db.execute(query).all()

    def get_users_by_registration_date(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Sequence[models.User]:
        """
        Get users registered within date range.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            List of users ordered by registration date
        """
        query = select(models.User)
        
        conditions = []
        if start_date:
            conditions.append(models.User.created_at >= start_date)
        if end_date:
            conditions.append(models.User.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return self._execute_query(
            query.order_by(desc(models.User.created_at))
        )

    # =========================================================================
    # USER MODIFICATION METHODS
    # =========================================================================

    def rename_user(self, user_id: int, new_name: str) -> Optional[models.User]:
        """
        Rename a user with validation.
        
        Args:
            user_id: ID of user to rename
            new_name: New username
            
        Returns:
            Updated user instance or None if user not found
            
        Raises:
            ValueError: If new name is invalid or already taken
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        new_name = new_name.strip()
        
        if not new_name:
            raise ValueError("Username cannot be empty")
        
        # Check if new name is already taken by another user
        existing = self.get_by_name(new_name)
        if existing and existing.id != user_id:
            raise ValueError(f"Username '{new_name}' already exists")
        
        return self.update(user, name=new_name)

    def update_email(self, user_id: int, new_email: str) -> Optional[models.User]:
        """
        Update user email with validation.
        
        Args:
            user_id: ID of user to update
            new_email: New email address
            
        Returns:
            Updated user instance or None if user not found
            
        Raises:
            ValueError: If email is invalid or already taken
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        new_email = new_email.lower().strip()
        
        if not new_email:
            raise ValueError("Email cannot be empty")
        
        # Check if email is already taken by another user
        existing = self.get_by_email(new_email)
        if existing and existing.id != user_id:
            raise ValueError(f"Email '{new_email}' already exists")
        
        return self.update(user, email=new_email)

    def update_password(self, user_id: int, password_hash: str) -> Optional[models.User]:
        """
        Update user password hash.
        
        Args:
            user_id: ID of user to update
            password_hash: New hashed password
            
        Returns:
            Updated user instance or None if user not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        return self.update(user, password_hash=password_hash)

    # =========================================================================
    # USER DELETION WITH CASCADING
    # =========================================================================

    def delete_user_and_sessions(self, user_id: int) -> bool:
        """
        Delete user and all associated sessions.
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            True if user was deleted, False if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        # Delete all user sessions first (cascade delete)
        self.db.query(models.Session).filter(
            models.Session.user_id == user_id
        ).delete()
        
        # Delete user
        self.delete(user)
        return True

    # =========================================================================
    # USER STATISTICS
    # =========================================================================

    def get_user_statistics_summary(self) -> dict:
        """
        Get summary statistics for all users.
        
        Returns:
            Dictionary with user statistics
        """
        total_users = self.count()
        
        users_with_sessions = self.db.scalar(
            select(func.count(func.distinct(models.Session.user_id)))
            .select_from(models.Session)
        )
        
        # Users registered in last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_registrations = self.db.scalar(
            select(func.count())
            .select_from(models.User)
            .where(models.User.created_at >= thirty_days_ago)
        )
        
        return {
            "total_users": total_users,
            "users_with_activity": users_with_sessions or 0,
            "inactive_users": total_users - (users_with_sessions or 0),
            "recent_registrations": recent_registrations or 0
        }