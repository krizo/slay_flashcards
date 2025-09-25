"""
Updated database configuration for API compatibility
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from typing import Generator

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./slayflashcards.db")

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL logging in development
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """
    Database dependency for FastAPI.
    Creates a new database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_database():
    """Reset database - drop and recreate all tables."""
    print("Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Done ✅")


def init_database():
    """Initialize database - create tables if they don't exist."""
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized ✅")


# For backwards compatibility with existing code
def get_session():
    """Get database session (for CLI/legacy code)."""
    return SessionLocal()