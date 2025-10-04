"""
Base repository pattern for database operations.

Provides generic CRUD operations and common query patterns.
All specific repositories should inherit from BaseRepository.
"""
from abc import ABC
from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime

from core.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType], ABC):
    """
    Abstract base repository class providing common database operations.
    
    Type Parameters:
        ModelType: SQLAlchemy model class bound to Base
        
    Attributes:
        db: SQLAlchemy database session
        model_class: The model class this repository manages
    """

    def __init__(self, db: Session, model_class: Type[ModelType]):
        """
        Initialize repository with database session and model class.
        
        Args:
            db: SQLAlchemy session
            model_class: Model class to manage
        """
        self.db = db
        self.model_class = model_class

    # =========================================================================
    # BASIC CRUD OPERATIONS
    # =========================================================================

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get a single record by primary key ID.
        
        Args:
            id: Primary key value
            
        Returns:
            Model instance or None if not found
        """
        return self.db.get(self.model_class, id)

    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Sequence[ModelType]:
        """
        Get all records with optional pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        query = select(self.model_class)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return self.db.execute(query).scalars().all()

    def count(self) -> int:
        """
        Count total records.
        
        Returns:
            Total count of records
        """
        return self.db.scalar(
            select(func.count()).select_from(self.model_class)
        )

    def exists(self, id: Any) -> bool:
        """
        Check if record exists by ID.
        
        Args:
            id: Primary key value
            
        Returns:
            True if record exists, False otherwise
        """
        return self.get_by_id(id) is not None

    # =========================================================================
    # CREATE OPERATIONS
    # =========================================================================

    def create(self, **kwargs) -> ModelType:
        """
        Create a new record.
        
        Args:
            **kwargs: Field values for the new record
            
        Returns:
            Created model instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        instance = self.model_class(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def bulk_create(self, instances: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple records in one transaction.
        
        Args:
            instances: List of dictionaries with field values
            
        Returns:
            List of created model instances
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        objects = [self.model_class(**data) for data in instances]
        self.db.add_all(objects)
        self.db.commit()
        
        # Refresh all objects to get database-generated values
        for obj in objects:
            self.db.refresh(obj)
            
        return objects

    # =========================================================================
    # UPDATE OPERATIONS
    # =========================================================================

    def update(self, instance: ModelType, **kwargs) -> ModelType:
        """
        Update an existing record.
        
        Args:
            instance: Model instance to update
            **kwargs: Fields to update with new values
            
        Returns:
            Updated model instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def bulk_update(self, updates: List[tuple[ModelType, Dict[str, Any]]]) -> List[ModelType]:
        """
        Update multiple records in one transaction.
        
        Args:
            updates: List of (instance, updates_dict) tuples
            
        Returns:
            List of updated model instances
        """
        for instance, update_data in updates:
            for key, value in update_data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
        
        self.db.commit()
        
        # Refresh all instances
        for instance, _ in updates:
            self.db.refresh(instance)
            
        return [instance for instance, _ in updates]

    # =========================================================================
    # DELETE OPERATIONS
    # =========================================================================

    def delete(self, instance: ModelType) -> None:
        """
        Delete a record.
        
        Args:
            instance: Model instance to delete
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        self.db.delete(instance)
        self.db.commit()

    def delete_by_id(self, id: Any) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Primary key value
            
        Returns:
            True if record was deleted, False if not found
        """
        instance = self.get_by_id(id)
        if instance:
            self.delete(instance)
            return True
        return False

    def bulk_delete(self, instances: List[ModelType]) -> int:
        """
        Delete multiple records in one transaction.
        
        Args:
            instances: List of model instances to delete
            
        Returns:
            Number of records deleted
        """
        count = len(instances)
        for instance in instances:
            self.db.delete(instance)
        
        self.db.commit()
        return count

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def refresh(self, instance: ModelType) -> ModelType:
        """
        Refresh instance from database.
        
        Args:
            instance: Model instance to refresh
            
        Returns:
            Refreshed model instance
        """
        self.db.refresh(instance)
        return instance

    def commit(self) -> None:
        """Commit current transaction."""
        self.db.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        self.db.rollback()

    def flush(self) -> None:
        """Flush pending changes to database."""
        self.db.flush()

    # =========================================================================
    # QUERY HELPERS
    # =========================================================================

    def _base_query(self):
        """Get base select query for this model."""
        return select(self.model_class)

    def _execute_query(self, query) -> Sequence[ModelType]:
        """Execute query and return results."""
        return self.db.execute(query).scalars().all()

    def _execute_single(self, query) -> Optional[ModelType]:
        """Execute query and return single result."""
        return self.db.execute(query).scalar_one_or_none()