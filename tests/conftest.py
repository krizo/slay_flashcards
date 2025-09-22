import json
import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from services.quiz_service import QuizService
from services.user_service import UserService


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    yield db

    db.close()


@pytest.fixture(scope="function")
def quiz_service(test_db):
    """Create QuizService with test database."""
    return QuizService(test_db)


@pytest.fixture(scope="function")
def user_service(test_db):
    """Create UserService with test database."""
    return UserService(test_db)


@pytest.fixture(scope="session")
def example_quiz_data():
    """Load the example quiz data."""
    return {
        "quiz": {
            "name": "French Basics",
            "subject": "French",
            "created_at": "2025-09-17",
            "description": "Basic French vocabulary for beginners"
        },
        "flashcards": [
            {
                "question": {
                    "title": "dog",
                    "text": "dog",
                    "lang": "en",
                    "difficulty": 1,
                    "emoji": "🐶",
                    "image": "dog.png"
                },
                "answer": {
                    "text": "chien",
                    "lang": "fr"
                }
            },
            {
                "question": {
                    "title": "cat",
                    "text": "cat",
                    "lang": "en",
                    "difficulty": 1,
                    "emoji": "🐱",
                    "image": "cat.png"
                },
                "answer": {
                    "text": "chat",
                    "lang": "fr"
                }
            },
            {
                "question": {
                    "title": "house",
                    "text": "house",
                    "lang": "en",
                    "difficulty": 2,
                    "emoji": "🏠"
                },
                "answer": {
                    "text": "maison",
                    "lang": "fr"
                }
            }
        ]
    }


@pytest.fixture(scope="function")
def temp_quiz_file(example_quiz_data):
    """Create a temporary quiz file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(example_quiz_data, f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    os.unlink(temp_file)


@pytest.fixture(scope="function")
def sample_user(user_service):
    """Create a sample user for testing."""
    return user_service.create_user("testuser")


@pytest.fixture(scope="function")
def sample_quiz_with_cards(quiz_service, example_quiz_data):
    """Create a sample quiz with flashcards."""
    return quiz_service.import_quiz_from_dict(example_quiz_data)