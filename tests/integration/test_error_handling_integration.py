"""
Fixed version of test_invalid_data_error_handling
Replace the failing test with this version.
"""
import pytest
from services.quiz_service import QuizService


def test_invalid_data_error_handling(test_db):
    """Test handling of invalid data in quiz import."""
    quiz_service = QuizService(test_db)

    # Test with completely invalid data
    result = quiz_service.validate_quiz_data("not a dictionary")
    assert result == False, "Should return False for invalid data type"

    # Test with None
    result = quiz_service.validate_quiz_data(None)
    assert result == False, "Should return False for None"

    # Test with empty dictionary
    result = quiz_service.validate_quiz_data({})
    assert result == False, "Should return False for empty dict"

    # Test with missing required fields
    incomplete_data = {
        "quiz": {},  # Missing name
        "flashcards": []
    }
    result = quiz_service.validate_quiz_data(incomplete_data)
    assert result == False, "Should return False when quiz name is missing"

    # Test with malformed flashcards
    bad_flashcards_data = {
        "quiz": {"name": "Test Quiz"},
        "flashcards": [
            {"question": "missing answer"},  # Invalid structure
        ]
    }
    result = quiz_service.validate_quiz_data(bad_flashcards_data)
    assert result == False, "Should return False for malformed flashcards"

    # Test with valid data (should return True)
    valid_data = {
        "quiz": {"name": "Valid Quiz"},
        "flashcards": [
            {
                "question": {"title": "test", "text": "test"},
                "answer": {"text": "answer"}
            }
        ]
    }
    result = quiz_service.validate_quiz_data(valid_data)
    assert result == True, "Should return True for valid data"


def test_quiz_import_error_handling(test_db):
    """Test quiz import error handling for operations that DO raise exceptions."""
    quiz_service = QuizService(test_db)

    # Test importing non-existent file (this SHOULD raise FileNotFoundError)
    with pytest.raises(FileNotFoundError):
        quiz_service.import_quiz_from_file("/non/existent/file.json")

    # Test importing invalid JSON file content
    import tempfile
    import json

    # Create a temporary file with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        invalid_json_file = f.name

    try:
        with pytest.raises(json.JSONDecodeError):
            quiz_service.import_quiz_from_file(invalid_json_file)
    finally:
        import os
        os.unlink(invalid_json_file)


def test_quiz_operations_error_handling(test_db):
    """Test quiz operations that should raise specific errors."""
    quiz_service = QuizService(test_db)

    # Test getting flashcards for non-existent quiz (should raise ValueError)
    with pytest.raises(ValueError, match="Quiz with id .* not found"):
        quiz_service.get_quiz_flashcards(99999)

    # Test getting non-existent quiz by ID (should return None, not raise)
    result = quiz_service.get_quiz_by_id(99999)
    assert result is None

    # Test search operations on non-existent quiz
    with pytest.raises(ValueError):
        quiz_service.get_flashcards_by_difficulty(99999, 1)

    with pytest.raises(ValueError):
        quiz_service.search_flashcards(99999, "test")