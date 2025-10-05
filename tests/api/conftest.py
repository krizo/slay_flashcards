"""
Shared fixtures for API tests
"""
# pylint: disable=redefined-outer-name,unused-argument
# Note: redefined-outer-name is disabled because it's the standard pytest pattern
# Note: unused-argument is disabled because pytest fixtures may not use all their dependencies

import pytest
from fastapi.testclient import TestClient  # pylint: disable=import-error
from sqlalchemy.orm import sessionmaker  # pylint: disable=import-error

from api.main_api import app
from core.db import models  # pylint: disable=unused-import
from core.db.database import Base, engine, get_db

# Create a TestClient instance
client = TestClient(app)

# Use a separate database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup and teardown the database for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client():
    """Fixture that provides a TestClient instance."""
    return TestClient(app)


@pytest.fixture(scope="function")
def registered_user(test_client):
    """Fixture that registers a user and returns credentials."""
    register_data = {
        "username": "testuser_auth",
        "password": "TestPass123",
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
            "password": f"Password{i}23",
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
