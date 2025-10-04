"""
Unit tests for FlashcardRepository.

Tests all flashcard-related database operations including:
- Flashcard creation with answer types
- Bulk flashcard creation
- Flashcard retrieval (by quiz, difficulty, answer type)
- Flashcard search
- Answer type management
- Answer type statistics
"""
import pytest

from core.db.crud.repository.quiz_repository import QuizRepository
from core.db.crud.repository.flashcard_repository import FlashcardRepository


# =============================================================================
# FLASHCARD CREATION TESTS
# =============================================================================

def test_create_flashcard_minimal(test_db):
    """Test creating flashcard with minimal required fields."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Question 1", "text": "What is 2+2?"},
        {"text": "4"}
    )

    assert flashcard.id is not None
    assert flashcard.quiz_id == quiz.id
    assert flashcard.question_title == "Question 1"
    assert flashcard.question_text == "What is 2+2?"
    assert flashcard.answer_text == "4"
    assert flashcard.answer_type == "text"  # Default


def test_create_flashcard_full(test_db):
    """Test creating flashcard with all fields."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {
            "title": "Python Question",
            "text": "What does 'len' return?",
            "lang": "en",
            "difficulty": 3,
            "emoji": "🐍",
            "image": "python.png"
        },
        {
            "text": "The length of the object",
            "lang": "en",
            "type": "short_text"
        }
    )

    assert flashcard.question_lang == "en"
    assert flashcard.question_difficulty == 3
    assert flashcard.question_emoji == "🐍"
    assert flashcard.question_image == "python.png"
    assert flashcard.answer_lang == "en"
    assert flashcard.answer_type == "short_text"


def test_create_flashcard_with_integer_answer(test_db):
    """Test creating flashcard with integer answer type."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Math Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Math", "text": "What is 10 * 5?"},
        {
            "text": "50",
            "type": "integer",
            "metadata": {"tolerance": 0}
        }
    )

    assert flashcard.answer_type == "integer"
    assert flashcard.answer_metadata["tolerance"] == 0


def test_create_flashcard_with_float_answer(test_db):
    """Test creating flashcard with float answer type."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Math Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Pi", "text": "What is pi to 2 decimals?"},
        {
            "text": "3.14",
            "type": "float",
            "metadata": {"tolerance": 0.01}
        }
    )

    assert flashcard.answer_type == "float"
    assert flashcard.answer_metadata["tolerance"] == 0.01


def test_create_flashcard_with_range_answer(test_db):
    """Test creating flashcard with range answer type."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Estimation Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Range", "text": "Estimate the population"},
        {
            "text": "5000000",
            "type": "range",
            "metadata": {"min": 4000000, "max": 6000000}
        }
    )

    assert flashcard.answer_type == "range"
    assert flashcard.answer_metadata["min"] == 4000000
    assert flashcard.answer_metadata["max"] == 6000000


def test_create_flashcard_with_boolean_answer(test_db):
    """Test creating flashcard with boolean answer type."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="True/False Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Bool", "text": "Python is a programming language"},
        {
            "text": "true",
            "type": "boolean"
        }
    )

    assert flashcard.answer_type == "boolean"
    assert flashcard.answer_text == "true"


def test_create_flashcard_with_choice_answer(test_db):
    """Test creating flashcard with choice answer type."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Multiple Choice")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Choice", "text": "What is the capital of France?"},
        {
            "text": "Paris",
            "type": "choice",
            "options": ["London", "Paris", "Berlin", "Madrid"]
        }
    )

    assert flashcard.answer_type == "choice"
    assert "Paris" in flashcard.answer_options
    assert len(flashcard.answer_options) == 4


def test_create_flashcard_with_multiple_choice_answer(test_db):
    """Test creating flashcard with multiple_choice answer type."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Multiple Choice")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Multi", "text": "Which are programming languages?"},
        {
            "text": "Python,Java",
            "type": "multiple_choice",
            "options": ["Python", "Java", "HTML", "CSS"]
        }
    )

    assert flashcard.answer_type == "multiple_choice"
    assert len(flashcard.answer_options) == 4


def test_create_flashcard_sets_default_tolerances(test_db):
    """Test that default tolerances are set for numeric types."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test")

    # Integer without tolerance
    int_card = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Int", "text": "What is 5?"},
        {"text": "5", "type": "integer"}
    )
    assert int_card.answer_metadata["tolerance"] == 0

    # Float without tolerance
    float_card = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Float", "text": "What is 3.14?"},
        {"text": "3.14", "type": "float"}
    )
    assert float_card.answer_metadata["tolerance"] == 0.01


def test_create_flashcard_invalid_answer_type_defaults_to_text(test_db):
    """Test that invalid answer type defaults to 'text'."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Test", "text": "Test"},
        {"text": "Answer", "type": "invalid_type"}
    )

    assert flashcard.answer_type == "text"


# =============================================================================
# BULK FLASHCARD CREATION TESTS
# =============================================================================

def test_bulk_create_flashcards(test_db):
    """Test bulk creating flashcards."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Bulk Test")

    flashcards_data = [
        {
            "question": {"title": "Q1", "text": "Question 1"},
            "answer": {"text": "Answer 1"}
        },
        {
            "question": {"title": "Q2", "text": "Question 2"},
            "answer": {"text": "Answer 2", "type": "short_text"}
        },
        {
            "question": {"title": "Q3", "text": "Question 3"},
            "answer": {"text": "42", "type": "integer"}
        }
    ]

    created = flashcard_repo.bulk_create_flashcards(quiz.id, flashcards_data)

    assert len(created) == 3
    assert created[0].answer_type == "text"
    assert created[1].answer_type == "short_text"
    assert created[2].answer_type == "integer"


def test_bulk_create_flashcards_with_mixed_types(test_db):
    """Test bulk creating flashcards with different answer types."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Mixed Types")

    flashcards_data = [
        {
            "question": {"title": "Text", "text": "What?"},
            "answer": {"text": "Answer", "type": "text"}
        },
        {
            "question": {"title": "Int", "text": "How many?"},
            "answer": {"text": "5", "type": "integer"}
        },
        {
            "question": {"title": "Bool", "text": "True or false?"},
            "answer": {"text": "true", "type": "boolean"}
        },
        {
            "question": {"title": "Choice", "text": "Pick one"},
            "answer": {
                "text": "A",
                "type": "choice",
                "options": ["A", "B", "C"]
            }
        }
    ]

    created = flashcard_repo.bulk_create_flashcards(quiz.id, flashcards_data)

    assert len(created) == 4
    assert created[0].answer_type == "text"
    assert created[1].answer_type == "integer"
    assert created[2].answer_type == "boolean"
    assert created[3].answer_type == "choice"


# =============================================================================
# FLASHCARD RETRIEVAL TESTS
# =============================================================================

def test_get_by_quiz_id(test_db):
    """Test getting flashcards by quiz ID."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q1", "text": "Question 1"},
        {"text": "Answer 1"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q2", "text": "Question 2"},
        {"text": "Answer 2"}
    )

    flashcards = flashcard_repo.get_by_quiz_id(quiz.id)

    assert len(flashcards) == 2
    assert all(f.quiz_id == quiz.id for f in flashcards)


def test_get_by_difficulty(test_db):
    """Test getting flashcards by difficulty level."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Easy", "text": "Easy Q", "difficulty": 1},
        {"text": "A"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Hard", "text": "Hard Q", "difficulty": 5},
        {"text": "A"}
    )

    easy_cards = flashcard_repo.get_by_difficulty(quiz.id, 1)
    hard_cards = flashcard_repo.get_by_difficulty(quiz.id, 5)

    assert len(easy_cards) == 1
    assert len(hard_cards) == 1
    assert easy_cards[0].question_difficulty == 1
    assert hard_cards[0].question_difficulty == 5


def test_get_by_answer_type(test_db):
    """Test getting flashcards by answer type."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Text", "text": "Text Q"},
        {"text": "A", "type": "text"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Int", "text": "Int Q"},
        {"text": "5", "type": "integer"}
    )

    text_cards = flashcard_repo.get_by_answer_type(quiz.id, "text")
    int_cards = flashcard_repo.get_by_answer_type(quiz.id, "integer")

    assert len(text_cards) == 1
    assert len(int_cards) == 1
    assert text_cards[0].answer_type == "text"
    assert int_cards[0].answer_type == "integer"


def test_count_flashcards_by_quiz_id(test_db):
    """Test counting flashcards in a quiz using base repository method."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q1", "text": "Q1"},
        {"text": "A1"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q2", "text": "Q2"},
        {"text": "A2"}
    )

    flashcards = flashcard_repo.get_by_quiz_id(quiz.id)
    assert len(flashcards) == 2


# =============================================================================
# FLASHCARD SEARCH TESTS
# =============================================================================

def test_search_by_question_text(test_db):
    """Test searching flashcards by question text."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Python", "text": "What is Python?"},
        {"text": "A programming language"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Java", "text": "What is Java?"},
        {"text": "Another language"}
    )

    results = flashcard_repo.search_by_question_text(quiz.id, "Python")

    assert len(results) >= 1
    assert "Python" in results[0].question_text


def test_search_by_question_text_case_insensitive(test_db):
    """Test that question text search is case-insensitive."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Test", "text": "UPPERCASE QUESTION"},
        {"text": "Answer"}
    )

    results = flashcard_repo.search_by_question_text(quiz.id, "uppercase")

    assert len(results) >= 1


# =============================================================================
# ANSWER TYPE MANAGEMENT TESTS
# =============================================================================

def test_update_answer_type(test_db):
    """Test updating flashcard answer type."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q", "text": "Question"},
        {"text": "42", "type": "text"}
    )

    updated = flashcard_repo.update_answer_type(
        flashcard.id,
        "integer",
        answer_metadata={"tolerance": 0}
    )

    assert updated.answer_type == "integer"
    assert updated.answer_metadata["tolerance"] == 0


def test_update_answer_type_invalid_fails(test_db):
    """Test that updating to invalid answer type fails."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q", "text": "Question"},
        {"text": "Answer"}
    )

    with pytest.raises(ValueError, match="Invalid answer type"):
        flashcard_repo.update_answer_type(flashcard.id, "invalid_type")


def test_answer_types_are_validated(test_db):
    """Test that answer types are validated during creation."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test")

    # Valid answer types should work
    for answer_type in ["text", "integer", "float", "range", "boolean", "choice", "multiple_choice", "short_text"]:
        flashcard = flashcard_repo.create_flashcard(
            quiz.id,
            {"title": f"Q-{answer_type}", "text": "Question"},
            {"text": "Answer", "type": answer_type}
        )
        assert flashcard.answer_type == answer_type


def test_validate_answer_type(test_db):
    """Test answer type validation."""
    flashcard_repo = FlashcardRepository(test_db)

    # Valid types should pass
    assert flashcard_repo._validate_answer_type("text") == "text"
    assert flashcard_repo._validate_answer_type("integer") == "integer"

    # Invalid type defaults to 'text' without raising
    assert flashcard_repo._validate_answer_type("invalid") == "text"

    # Invalid type raises when raise_on_invalid=True
    with pytest.raises(ValueError, match="Invalid answer type"):
        flashcard_repo._validate_answer_type("invalid", raise_on_invalid=True)


# =============================================================================
# ANSWER TYPE STATISTICS TESTS
# =============================================================================

def test_count_by_answer_type_using_statistics(test_db):
    """Test counting flashcards by answer type using statistics."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q1", "text": "Q1"},
        {"text": "A1", "type": "text"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q2", "text": "Q2"},
        {"text": "A2", "type": "text"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q3", "text": "Q3"},
        {"text": "5", "type": "integer"}
    )

    stats = flashcard_repo.get_answer_type_statistics(quiz.id)

    assert stats["text"] == 2
    assert stats["integer"] == 1


def test_get_answer_type_statistics(test_db):
    """Test getting answer type statistics for a quiz."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q1", "text": "Q1"},
        {"text": "A1", "type": "text"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q2", "text": "Q2"},
        {"text": "A2", "type": "text"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q3", "text": "Q3"},
        {"text": "5", "type": "integer"}
    )
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q4", "text": "Q4"},
        {"text": "true", "type": "boolean"}
    )

    stats = flashcard_repo.get_answer_type_statistics(quiz.id)

    assert stats["text"] == 2
    assert stats["integer"] == 1
    assert stats["boolean"] == 1
    assert stats.get("float", 0) == 0


# =============================================================================
# FLASHCARD MODIFICATION TESTS
# =============================================================================

def test_update_flashcard(test_db):
    """Test updating flashcard fields."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Old", "text": "Old question"},
        {"text": "Old answer"}
    )

    updated = flashcard_repo.update(
        flashcard,
        question_title="New",
        question_text="New question",
        answer_text="New answer"
    )

    assert updated.question_title == "New"
    assert updated.question_text == "New question"
    assert updated.answer_text == "New answer"


# =============================================================================
# FLASHCARD DELETION TESTS
# =============================================================================

def test_delete_flashcard(test_db):
    """Test deleting a flashcard."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q", "text": "Question"},
        {"text": "Answer"}
    )
    flashcard_id = flashcard.id

    flashcard_repo.delete(flashcard)

    assert flashcard_repo.get_by_id(flashcard_id) is None


def test_delete_by_id(test_db):
    """Test deleting flashcard by ID."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Test Quiz")

    flashcard = flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q", "text": "Question"},
        {"text": "Answer"}
    )

    result = flashcard_repo.delete_by_id(flashcard.id)

    assert result is True
    assert flashcard_repo.get_by_id(flashcard.id) is None
