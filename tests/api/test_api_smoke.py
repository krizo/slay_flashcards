"""
API smoke tests with proper fixtures and email validation
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from api.main_api import app
from core.db.database import Base, engine

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup and teardown the database for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "SlayFlashcards API"


def test_auth_flow():
    """Test basic authentication flow."""
    # Register a new user
    register_data = {
        "username": "authflowuser",
        "password": "SecurePass123",
        "email": "authflow@example.com"
    }

    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201

    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

    # Store token for authenticated requests
    token = data["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test getting user info
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200

    user_data = response.json()
    assert user_data["success"] is True
    assert user_data["data"]["name"] == "authflowuser"
    assert user_data["data"]["email"] == "authflow@example.com"


def test_registration_validation():
    """Test registration validation for password and email."""
    # Test weak password
    weak_pass_data = {
        "username": "weakuser",
        "password": "weak",  # Too short, no uppercase, no digit
        "email": "weak@example.com"
    }
    response = client.post("/api/v1/auth/register", json=weak_pass_data)
    assert response.status_code == 422

    # Test invalid email
    invalid_email_data = {
        "username": "invaliduser",
        "password": "ValidPass123",
        "email": "not-an-email"
    }
    response = client.post("/api/v1/auth/register", json=invalid_email_data)
    assert response.status_code == 422

    # Test missing email
    no_email_data = {
        "username": "noemailuser",
        "password": "ValidPass123"
    }
    response = client.post("/api/v1/auth/register", json=no_email_data)
    assert response.status_code == 422


def test_duplicate_registration(registered_user):
    """Test that duplicate username/email is rejected."""
    # Try to register with same username
    duplicate_username = {
        "username": registered_user["username"],
        "password": "AnotherPass123",
        "email": "different@example.com"
    }
    response = client.post("/api/v1/auth/register", json=duplicate_username)
    assert response.status_code == 409
    assert "Username already exists" in response.json()["detail"]

    # Try to register with same email
    duplicate_email = {
        "username": "differentuser",
        "password": "AnotherPass123",
        "email": registered_user["email"]
    }
    response = client.post("/api/v1/auth/register", json=duplicate_email)
    assert response.status_code == 409
    assert "Email address already exists" in response.json()["detail"]


def test_quiz_crud(authenticated_client):
    """Test basic quiz CRUD operations."""
    # Create a quiz
    quiz_data = {
        "name": "Test Quiz",
        "subject": "Testing",
        "description": "A test quiz for API testing"
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    assert response.status_code == 201

    created_quiz = response.json()
    assert created_quiz["success"] is True
    quiz_id = created_quiz["data"]["id"]

    # Get the quiz
    response = authenticated_client.get(f"/api/v1/quizzes/{quiz_id}")
    assert response.status_code == 200

    quiz = response.json()
    assert quiz["data"]["name"] == "Test Quiz"
    assert quiz["data"]["subject"] == "Testing"

    # List quizzes
    response = authenticated_client.get("/api/v1/quizzes/")
    assert response.status_code == 200

    quizzes = response.json()
    assert len(quizzes["data"]) >= 1


def test_flashcard_creation(authenticated_client):
    """Test flashcard creation."""
    # Create quiz first
    quiz_data = {"name": "Flashcard Test Quiz", "subject": "Testing"}
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = quiz_response.json()["data"]["id"]

    # Create a flashcard
    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {
            "title": "What is 2+2?",
            "text": "What is 2+2?",
            "lang": "en",
            "difficulty": 1,
            "emoji": "🧮"
        },
        "answer": {
            "text": "4",
            "type": "integer",
            "lang": "en"
        }
    }

    response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    assert response.status_code == 201

    flashcard = response.json()
    assert flashcard["success"] is True
    assert flashcard["data"]["question_title"] == "What is 2+2?"
    assert flashcard["data"]["answer_text"] == "4"
    assert flashcard["data"]["answer_type"] == "integer"


def test_quiz_import(authenticated_client):
    """Test quiz import from JSON data."""
    import_data = {
        "quiz": {
            "name": "Imported Quiz",
            "subject": "Import Test",
            "description": "A quiz imported via API"
        },
        "flashcards": [
            {
                "question": {
                    "title": "hello",
                    "text": "How do you say 'hello' in French?",
                    "lang": "en",
                    "difficulty": 1,
                    "emoji": "👋"
                },
                "answer": {
                    "text": "bonjour",
                    "type": "short_text",
                    "lang": "fr"
                }
            },
            {
                "question": {
                    "title": "goodbye",
                    "text": "How do you say 'goodbye' in French?",
                    "lang": "en",
                    "difficulty": 1,
                    "emoji": "👋"
                },
                "answer": {
                    "text": "au revoir",
                    "type": "short_text",
                    "lang": "fr"
                }
            }
        ]
    }

    response = authenticated_client.post("/api/v1/quizzes/import", json=import_data)
    assert response.status_code == 201

    result = response.json()
    assert result["success"] is True
    assert result["data"]["name"] == "Imported Quiz"
    assert result["data"]["flashcard_count"] == 2


def test_session_and_test_submission(authenticated_client):
    """Test creating a session and submitting test answers."""
    # Get user ID
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]

    # Create quiz with flashcards
    import_data = {
        "quiz": {"name": "Math Test", "subject": "Mathematics"},
        "flashcards": [
            {
                "question": {"title": "2+2", "text": "What is 2+2?", "difficulty": 1},
                "answer": {"text": "4", "type": "integer"}
            }
        ]
    }

    quiz_response = authenticated_client.post("/api/v1/quizzes/import", json=import_data)
    quiz_id = quiz_response.json()["data"]["id"]

    # Create test session
    session_data = {
        "user_id": user_id,
        "quiz_id": quiz_id,
        "mode": "test"
    }

    session_response = authenticated_client.post("/api/v1/sessions/", json=session_data)
    assert session_response.status_code == 201
    session_id = session_response.json()["data"]["id"]

    # Get flashcards to find IDs
    flashcards_response = authenticated_client.get(f"/api/v1/flashcards/?quiz_id={quiz_id}")
    flashcards = flashcards_response.json()["data"]
    flashcard_id = flashcards[0]["id"]

    # Submit test answers
    test_submission = {
        "session_id": session_id,
        "answers": [
            {
                "flashcard_id": flashcard_id,
                "user_answer": "4",
                "time_taken": 2.5
            }
        ]
    }

    test_response = authenticated_client.post("/api/v1/sessions/test/submit", json=test_submission)
    assert test_response.status_code == 200

    results = test_response.json()
    assert results["success"] is True
    assert results["data"]["final_score"] == 100
    assert results["data"]["correct"] == 1


def test_user_statistics(authenticated_client):
    """Test retrieving user statistics."""
    # Get user ID
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]

    # Create some activity
    quiz_data = {"name": "Stats Quiz", "subject": "Testing"}
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = quiz_response.json()["data"]["id"]

    # Create a learning session
    session_data = {
        "user_id": user_id,
        "quiz_id": quiz_id,
        "mode": "learn"
    }
    authenticated_client.post("/api/v1/sessions/", json=session_data)

    # Get user statistics
    stats_response = authenticated_client.get(f"/api/v1/users/{user_id}/statistics")
    assert stats_response.status_code == 200, stats_response.json()

    stats = stats_response.json()["data"]
    assert stats["total_sessions"] >= 1
    assert stats["learn_sessions"] >= 1
