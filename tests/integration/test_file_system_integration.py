import json
import tempfile
from pathlib import Path

import pytest

from services.quiz_service import QuizService


def test_quiz_import_from_file_integration(test_db):
    """Test importing quiz from actual file."""
    quiz_service = QuizService(test_db)

    # Create temporary quiz file
    quiz_data = {
        "quiz": {
            "name": "File Import Test",
            "subject": "Testing",
            "description": "Test quiz imported from file"
        },
        "flashcards": [
            {
                "question": {
                    "title": "test",
                    "text": "This is a test question",
                    "lang": "en"
                },
                "answer": {
                    "text": "test answer",
                    "lang": "en"
                }
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(quiz_data, f)
        temp_file = f.name

    try:
        # Import from file
        quiz = quiz_service.import_quiz_from_file(temp_file)

        assert quiz.name == "File Import Test"
        assert quiz.subject == "Testing"

        # Verify flashcards were imported
        cards = quiz_service.get_quiz_flashcards(quiz.id)
        assert len(cards) == 1
        assert cards[0].question_title == "test"
        assert cards[0].answer_text == "test answer"

    finally:
        # Clean up
        Path(temp_file).unlink()


def test_invalid_quiz_file_handling(test_db):
    """Test handling of invalid quiz files."""
    quiz_service = QuizService(test_db)

    # Test with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        invalid_json_file = f.name

    try:
        with pytest.raises(json.JSONDecodeError):
            quiz_service.import_quiz_from_file(invalid_json_file)
    finally:
        Path(invalid_json_file).unlink()

    # Test with missing required fields
    incomplete_data = {"quiz": {"subject": "Test"}}  # Missing name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(incomplete_data, f)
        incomplete_file = f.name

    try:
        # Should either raise an error or handle gracefully
        # depending on validation implementation
        result = quiz_service.validate_quiz_data(incomplete_data)
        assert result == False
    finally:
        Path(incomplete_file).unlink()
