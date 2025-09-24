from abc import ABC
from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select

from core.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType], ABC):
    """Abstract base repository class."""

    def __init__(self, db: Session, model_class: Type[ModelType]):
        self.db = db
        self.model_class = model_class

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        return self.db.get(self.model_class, id)

    def get_all(self) -> List[ModelType]:
        """Get all records."""
        return self.db.execute(select(self.model_class)).scalars().all()

    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model_class(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, instance: ModelType, **kwargs) -> ModelType:
        """Update an existing record."""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        """Delete a record."""
        self.db.delete(instance)
        self.db.commit()

    def bulk_create(self, instances: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records in one transaction."""
        objects = [self.model_class(**data) for data in instances]
        self.db.add_all(objects)
        self.db.commit()
        for obj in objects:
            self.db.refresh(obj)
        return objects
