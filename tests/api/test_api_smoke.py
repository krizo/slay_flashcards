"""
Simple API test example to verify everything works
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

# This assumes your main FastAPI app is in api/main_api.py
from api.main_api import app
from core.db.database import Base, engine

client = TestClient(app)


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # or sqlite:///:memory:
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """ Setup and teardown the database for each test."""
    # Drop and recreate schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Optional teardown if needed
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
        "username": "testuser",
        "password": "testpassword123",
        "email": "test@example.com"
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
    assert user_data["data"]["name"] == "testuser"


def test_quiz_crud():
    """Test basic quiz CRUD operations."""
    # First, authenticate
    register_data = {"username": "quizuser", "password": "password123"}
    auth_response = client.post("/api/v1/auth/register", json=register_data)
    token = auth_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a quiz
    quiz_data = {
        "name": "Test Quiz",
        "subject": "Testing",
        "description": "A test quiz for API testing"
    }

    response = client.post("/api/v1/quizzes/", json=quiz_data, headers=headers)
    assert response.status_code == 201

    created_quiz = response.json()
    assert created_quiz["success"] is True
    quiz_id = created_quiz["data"]["id"]

    # Get the quiz
    response = client.get(f"/api/v1/quizzes/{quiz_id}", headers=headers)
    assert response.status_code == 200

    quiz = response.json()
    assert quiz["data"]["name"] == "Test Quiz"
    assert quiz["data"]["subject"] == "Testing"

    # List quizzes
    response = client.get("/api/v1/quizzes/", headers=headers)
    assert response.status_code == 200

    quizzes = response.json()
    assert len(quizzes["data"]) >= 1


def test_flashcard_creation():
    """Test flashcard creation."""
    # Setup: Create user and quiz
    register_data = {"username": "carduser", "password": "password123"}
    auth_response = client.post("/api/v1/auth/register", json=register_data)
    token = auth_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    quiz_data = {"name": "Flashcard Test Quiz", "subject": "Testing"}
    quiz_response = client.post("/api/v1/quizzes/", json=quiz_data, headers=headers)
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

    response = client.post("/api/v1/flashcards/", json=flashcard_data, headers=headers)
    assert response.status_code == 201, "Response: " + response.text

    flashcard = response.json()
    assert flashcard["success"] is True
    assert flashcard["data"]["question_title"] == "What is 2+2?"
    assert flashcard["data"]["answer_text"] == "4"
    assert flashcard["data"]["answer_type"] == "integer"


def test_quiz_import():
    """Test quiz import from JSON data."""
    # Setup authentication
    register_data = {"username": "importuser", "password": "password123"}
    auth_response = client.post("/api/v1/auth/register", json=register_data)
    token = auth_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Import quiz data (matches your existing JSON structure)
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

    response = client.post("/api/v1/quizzes/import", json=import_data, headers=headers)
    assert response.status_code == 201

    result = response.json()
    assert result["success"] is True
    assert result["data"]["name"] == "Imported Quiz"
    assert result["data"]["flashcard_count"] == 2


def test_session_and_test_submission():
    """Test creating a session and submitting test answers."""
    # Setup: user, quiz, flashcards
    register_data = {"username": "sessionuser", "password": "password123"}
    auth_response = client.post("/api/v1/auth/register", json=register_data)
    token = auth_response.json()["data"]["access_token"]
    user_id = auth_response.json()["data"]["user_id"] if "user_id" in auth_response.json()["data"] else 1
    headers = {"Authorization": f"Bearer {token}"}

    # Get or create user ID (simplified for test)
    user_response = client.get("/api/v1/auth/me", headers=headers)
    user_id = user_response.json()["data"]["id"]

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

    quiz_response = client.post("/api/v1/quizzes/import", json=import_data, headers=headers)
    quiz_id = quiz_response.json()["data"]["id"]

    # Create test session
    session_data = {
        "user_id": user_id,
        "quiz_id": quiz_id,
        "mode": "test"
    }

    session_response = client.post("/api/v1/sessions/", json=session_data, headers=headers)
    assert session_response.status_code == 201
    session_id = session_response.json()["data"]["id"]

    # Get flashcards to find IDs
    flashcards_response = client.get(f"/api/v1/flashcards/?quiz_id={quiz_id}", headers=headers)
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

    test_response = client.post("/api/v1/sessions/test/submit", json=test_submission, headers=headers)
    assert test_response.status_code == 200

    results = test_response.json()
    assert results["success"] is True
    assert results["data"]["final_score"] == 100  # Should be correct
    assert results["data"]["correct"] == 1


if __name__ == "__main__":
    # Run tests manually
    test_health_check()
    print("✅ Health check passed")

    test_auth_flow()
    print("✅ Auth flow passed")

    test_quiz_crud()
    print("✅ Quiz CRUD passed")

    test_flashcard_creation()
    print("✅ Flashcard creation passed")

    test_quiz_import()
    print("✅ Quiz import passed")

    test_session_and_test_submission()
    print("✅ Session and test submission passed")

    print("🎉 All API tests passed!")