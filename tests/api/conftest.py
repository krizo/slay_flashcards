"""
Shared fixtures for API tests
"""
# pylint: disable=redefined-outer-name,unused-argument
# Note: redefined-outer-name is disabled because it's the standard pytest pattern
# Note: unused-argument is disabled because pytest fixtures may not use all their dependencies

import pytest
from fastapi.testclient import TestClient  # pylint: disable=import-error
from sqlalchemy import create_engine  # pylint: disable=import-error
from sqlalchemy.orm import sessionmaker  # pylint: disable=import-error
from sqlalchemy.pool import StaticPool  # pylint: disable=import-error

from api.main_api import app
from core.db import models  # pylint: disable=unused-import
from core.db.database import Base, get_db
from core.db import database as db_module

# Create a TestClient instance
client = TestClient(app)

# Global variables for test database - will be set by setup_test_environment
test_engine = None
TestingSessionLocal = None


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(request):
    """Setup test environment with worker-specific database."""
    global test_engine, TestingSessionLocal

    import os
    import uuid

    # Import models to register them with SQLAlchemy metadata
    # This ensures all tables are created
    import core.db.models  # noqa: F401

    # Get worker ID from xdist (or "master" if not using xdist)
    worker_id = getattr(request.config, 'workerinput', {}).get('workerid', 'master')

    # Use unique database file for each worker to avoid any conflicts
    # Even for master, use a file (not :memory:) to ensure proper isolation
    db_file = f"./test_{worker_id}_{uuid.uuid4().hex[:8]}.db"

    # Create worker-specific engine with appropriate settings
    test_engine = create_engine(
        f"sqlite:///{db_file}",
        echo=False,
        connect_args={
            "check_same_thread": False,
            "timeout": 30  # 30 second timeout for lock waits
        },
        poolclass=StaticPool  # Use StaticPool to avoid connection pool issues
    )

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Override the database module's engine and SessionLocal as well
    # This ensures any code that imports these directly uses the test database
    original_engine = db_module.engine
    original_session_local = db_module.SessionLocal

    db_module.engine = test_engine
    db_module.SessionLocal = TestingSessionLocal

    # Override the app's database dependency
    app.dependency_overrides[get_db] = override_get_db

    yield

    # Restore original database module values
    db_module.engine = original_engine
    db_module.SessionLocal = original_session_local

    # Cleanup: dispose engine and remove test database file
    test_engine.dispose()
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass  # Ignore cleanup errors


@pytest.fixture(scope="function", autouse=True)
def setup_database(setup_test_environment):
    """Setup and teardown the database for each test."""
    # Explicitly depend on setup_test_environment to ensure proper ordering

    # Import models to ensure they're registered
    from core.db import models as db_models  # noqa: F401

    # Clean slate: drop and recreate all tables
    # checkfirst=True prevents errors if tables don't exist
    Base.metadata.drop_all(bind=test_engine, checkfirst=True)
    Base.metadata.create_all(bind=test_engine)

    yield

    # Cleanup after test
    Base.metadata.drop_all(bind=test_engine, checkfirst=True)


@pytest.fixture(scope="function")
def test_client(setup_database):
    """Fixture that provides a TestClient instance."""
    # Explicitly depend on setup_database to ensure tables are created first
    return TestClient(app)


@pytest.fixture(scope="function")
def registered_user(test_client):
    """Fixture that registers a user and returns credentials."""
    register_data = {
        "username": "testuser_auth",
        "password": "TestPass123!",  # Updated to meet password requirements
        "email": "testuser@example.com"
    }
    response = test_client.post("/api/v1/auth/register", json=register_data)

    if response.status_code != 201:
        raise ValueError(f"Registration failed: {response.text}")

    token = response.json()["data"]["access_token"]

    return {
        "username": register_data["username"],
        "email": register_data["email"],
        "password": register_data["password"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture(scope="function")
def authenticated_client(registered_user):
    """A TestClient instance with authentication headers."""
    test_client = TestClient(app)
    test_client.headers.update(registered_user["headers"])
    return test_client


@pytest.fixture(scope="function")
def multiple_users(test_client):
    """Create multiple users for testing."""
    users = []
    for i in range(3):
        user_data = {
            "username": f"user{i}",
            "password": f"Password{i}23!",  # Updated to meet password requirements
            "email": f"user{i}@example.com"
        }
        response = test_client.post("/api/v1/auth/register", json=user_data)
        if response.status_code == 201:
            token = response.json()["data"]["access_token"]
            users.append({
                "username": user_data["username"],
                "email": user_data["email"],
                "token": token,
                "headers": {"Authorization": f"Bearer {token}"}
            })
    return users


@pytest.fixture(scope="function")
def sample_quiz(authenticated_client):
    """Create a sample quiz for testing."""
    quiz_data = {
        "name": "Test Quiz",
        "subject": "Testing",
        "description": "A quiz for testing purposes"
    }
    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    assert response.status_code == 201
    return response.json()["data"]


@pytest.fixture(scope="function")
def sample_quiz_with_flashcards(authenticated_client):
    """Create a quiz with flashcards for testing."""
    import_data = {
        "quiz": {
            "name": "Sample Quiz",
            "subject": "Testing",
            "description": "Quiz with flashcards"
        },
        "flashcards": [
            {
                "question": {
                    "title": "Question 1",
                    "text": "What is 1+1?",
                    "difficulty": 1
                },
                "answer": {"text": "2", "type": "integer"}
            },
            {
                "question": {
                    "title": "Question 2",
                    "text": "What is 2+2?",
                    "difficulty": 1
                },
                "answer": {"text": "4", "type": "integer"}
            },
            {
                "question": {
                    "title": "Question 3",
                    "text": "What is 3+3?",
                    "difficulty": 2
                },
                "answer": {"text": "6", "type": "integer"}
            }
        ]
    }

    response = authenticated_client.post("/api/v1/quizzes/import", json=import_data)
    assert response.status_code == 201

    quiz = response.json()["data"]
    quiz_id = quiz["id"]

    # Get flashcards
    flashcards_response = authenticated_client.get(f"/api/v1/flashcards/?quiz_id={quiz_id}")
    flashcards = flashcards_response.json()["data"]

    return {
        "quiz": quiz,
        "flashcards": flashcards
    }


@pytest.fixture(scope="function")
def user_with_activity(authenticated_client, registered_user, sample_quiz_with_flashcards):
    """Create a user with some learning/test activity."""
    # Get user ID
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]

    quiz = sample_quiz_with_flashcards["quiz"]
    flashcards = sample_quiz_with_flashcards["flashcards"]

    # Create learning session
    learn_session_data = {
        "user_id": user_id,
        "quiz_id": quiz["id"],
        "mode": "learn"
    }
    authenticated_client.post("/api/v1/sessions/", json=learn_session_data)

    # Create test session
    test_session_data = {
        "user_id": user_id,
        "quiz_id": quiz["id"],
        "mode": "test"
    }
    test_session_response = authenticated_client.post("/api/v1/sessions/", json=test_session_data)
    test_session_id = test_session_response.json()["data"]["id"]

    # Submit test answers
    test_submission = {
        "session_id": test_session_id,
        "answers": [
            {"flashcard_id": fc["id"], "user_answer": fc["answer_text"], "time_taken": 2.0}
            for fc in flashcards
        ]
    }
    authenticated_client.post("/api/v1/sessions/test/submit", json=test_submission)

    return {
        "user_id": user_id,
        "quiz": quiz,
        "flashcards": flashcards
    }
