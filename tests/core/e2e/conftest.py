"""
E2E Test Configuration and Fixtures - Fixed Version

This module provides shared configuration and fixtures for all end-to-end tests.
Make sure this file is in the tests/e2e/ directory for proper fixture discovery.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.db.database import Base
from core.services.audio_service import SilentAudioService
from core.services.quiz_service import QuizService
from core.services.user_service import UserService


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest for E2E tests."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )


# =============================================================================
# CORE E2E FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def e2e_test_config():
    """Configuration for E2E tests."""
    return {
        "test_timeout": 30,  # seconds
        "performance_threshold": 5.0,  # seconds for large operations
        "audio_enabled": False,  # Disable audio for faster tests
        "strict_mode": False,  # Use flexible matching by default
        "similarity_threshold": 0.8,
        "temp_file_cleanup": True,
    }


@pytest.fixture(scope="function")
def e2e_database():
    """Create isolated database for each E2E test."""
    # Use in-memory SQLite for E2E tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    yield db

    db.close()


@pytest.fixture(scope="function")
def e2e_services(e2e_database):
    """Create service instances for E2E tests."""
    return {
        "quiz_service": QuizService(e2e_database),
        "user_service": UserService(e2e_database),
        "audio_service": SilentAudioService(),
        "database": e2e_database
    }


@pytest.fixture(scope="function")
def temp_directory():
    """Create temporary directory for file operations."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)