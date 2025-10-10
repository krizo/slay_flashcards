"""
Unit tests for QuizRepository.

Tests all quiz-related database operations including:
- Quiz creation
- Quiz lookup (by ID, name, subject)
- Quiz search operations
- Quiz deletion
- Subject management
"""
from datetime import datetime

from core.db.crud.repository.quiz_repository import QuizRepository
from core.db.crud.repository.flashcard_repository import FlashcardRepository
from core.db.models import User


def _create_test_user(db):
    """Helper to create a test user for quiz ownership."""
    user = User(name="testuser", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# =============================================================================
# QUIZ CREATION TESTS
# =============================================================================

def test_create_quiz_minimal(test_db):
    """Test creating quiz with minimal required fields."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(name="Test Quiz", user_id=user.id)

    assert quiz.id is not None
    assert quiz.name == "Test Quiz"
    assert quiz.subject is None
    assert quiz.description is None
    assert quiz.created_at is not None


def test_create_quiz_with_subject(test_db):
    """Test creating quiz with subject."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(
        name="Math Quiz", user_id=user.id,
        subject="Mathematics"
    )

    assert quiz.subject == "Mathematics"


def test_create_quiz_with_description(test_db):
    """Test creating quiz with description."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(
        name="Quiz", user_id=user.id,
        description="This is a test quiz"
    )

    assert quiz.description == "This is a test quiz"


def test_create_quiz_with_custom_date(test_db):
    """Test creating quiz with custom creation date."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    custom_date = datetime(2024, 1, 1, 12, 0, 0)

    quiz = quiz_repo.create_quiz(
        name="Quiz", user_id=user.id,
        created_at=custom_date
    )

    assert quiz.created_at == custom_date


def test_create_quiz_full(test_db):
    """Test creating quiz with all fields."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(
        name="Complete Quiz", user_id=user.id,
        subject="Testing",
        description="A complete test quiz"
    )

    assert quiz.id is not None
    assert quiz.name == "Complete Quiz"
    assert quiz.subject == "Testing"
    assert quiz.description == "A complete test quiz"


# =============================================================================
# QUIZ LOOKUP TESTS
# =============================================================================

def test_get_by_id(test_db):
    """Test getting quiz by ID."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    created = quiz_repo.create_quiz(name="Test Quiz", user_id=user.id)
    found = quiz_repo.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.name == "Test Quiz"


def test_get_by_id_not_found(test_db):
    """Test getting non-existent quiz returns None."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    found = quiz_repo.get_by_id(99999)

    assert found is None


def test_get_by_name(test_db):
    """Test getting quiz by exact name."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Unique Quiz Name", user_id=user.id)

    found = quiz_repo.get_by_name("Unique Quiz Name")

    assert found is not None
    assert found.name == "Unique Quiz Name"


def test_get_by_name_case_sensitive(test_db):
    """Test that get_by_name is case-sensitive."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="CaseSensitive", user_id=user.id)

    found_exact = quiz_repo.get_by_name("CaseSensitive")
    found_lower = quiz_repo.get_by_name("casesensitive")

    assert found_exact is not None
    assert found_lower is None


def test_get_by_name_not_found(test_db):
    """Test getting non-existent quiz by name returns None."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    found = quiz_repo.get_by_name("NonExistent")

    assert found is None


def test_get_all(test_db):
    """Test getting all quizzes."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Quiz 1", user_id=user.id)
    quiz_repo.create_quiz(name="Quiz 2", user_id=user.id)
    quiz_repo.create_quiz(name="Quiz 3", user_id=user.id)

    quizzes = quiz_repo.get_all()

    assert len(quizzes) >= 3


def test_get_all_with_pagination(test_db):
    """Test getting quizzes with pagination."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    for i in range(10):
        quiz_repo.create_quiz(name=f"Quiz {i}", user_id=user.id)

    # Get first 5
    page1 = quiz_repo.get_all(limit=5, offset=0)
    assert len(page1) == 5

    # Get next 5
    page2 = quiz_repo.get_all(limit=5, offset=5)
    assert len(page2) == 5

    # Ensure no overlap
    page1_ids = {q.id for q in page1}
    page2_ids = {q.id for q in page2}
    assert page1_ids.isdisjoint(page2_ids)


def test_count(test_db):
    """Test counting total quizzes."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    initial_count = quiz_repo.count()

    quiz_repo.create_quiz(name="Quiz 1", user_id=user.id)
    quiz_repo.create_quiz(name="Quiz 2", user_id=user.id)

    assert quiz_repo.count() == initial_count + 2


def test_exists(test_db):
    """Test checking if quiz exists by ID."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    assert quiz_repo.exists(quiz.id) is True
    assert quiz_repo.exists(99999) is False


# =============================================================================
# QUIZ SUBJECT TESTS
# =============================================================================

def test_get_by_subject(test_db):
    """Test getting quizzes by subject."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Math 1", user_id=user.id, subject="Mathematics")
    quiz_repo.create_quiz(name="Math 2", user_id=user.id, subject="Mathematics")
    quiz_repo.create_quiz(name="Sci 1", user_id=user.id, subject="Science")

    math_quizzes = quiz_repo.get_by_subject("Mathematics")

    assert len(math_quizzes) >= 2
    assert all(q.subject == "Mathematics" for q in math_quizzes)


def test_get_by_subject_empty(test_db):
    """Test getting quizzes for subject with no quizzes."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quizzes = quiz_repo.get_by_subject("NonExistent")

    assert len(quizzes) == 0


def test_get_by_subject_ordered_by_name(test_db):
    """Test that quizzes are ordered by name."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="C Quiz", user_id=user.id, subject="Test")
    quiz_repo.create_quiz(name="A Quiz", user_id=user.id, subject="Test")
    quiz_repo.create_quiz(name="B Quiz", user_id=user.id, subject="Test")

    quizzes = quiz_repo.get_by_subject("Test")
    names = [q.name for q in quizzes]

    assert names == sorted(names)


def test_get_all_subjects(test_db):
    """Test getting all unique subjects."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Quiz 1", user_id=user.id, subject="Math")
    quiz_repo.create_quiz(name="Quiz 2", user_id=user.id, subject="Science")
    quiz_repo.create_quiz(name="Quiz 3", user_id=user.id, subject="Math")
    quiz_repo.create_quiz(name="Quiz 4", user_id=user.id)  # No subject

    subjects = quiz_repo.get_all_subjects()

    assert "Math" in subjects
    assert "Science" in subjects
    assert len(subjects) >= 2


def test_get_all_subjects_ordered(test_db):
    """Test that subjects are returned in alphabetical order."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Quiz 1", user_id=user.id, subject="Zebra")
    quiz_repo.create_quiz(name="Quiz 2", user_id=user.id, subject="Apple")
    quiz_repo.create_quiz(name="Quiz 3", user_id=user.id, subject="Banana")

    subjects = quiz_repo.get_all_subjects()
    subjects_list = list(subjects)

    assert subjects_list == sorted(subjects_list)


# =============================================================================
# QUIZ SEARCH TESTS
# =============================================================================

def test_search_by_name_pattern(test_db):
    """Test searching quizzes by name pattern."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Python Basics", user_id=user.id)
    quiz_repo.create_quiz(name="Python Advanced", user_id=user.id)
    quiz_repo.create_quiz(name="JavaScript Basics", user_id=user.id)

    results = quiz_repo.search_by_name("Python")

    assert len(results) >= 2
    assert all("Python" in q.name for q in results)


def test_search_by_name_case_insensitive(test_db):
    """Test that search is case-insensitive."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="JavaScript Tutorial", user_id=user.id)

    results = quiz_repo.search_by_name("javascript")

    assert len(results) >= 1


def test_search_by_name_partial_match(test_db):
    """Test partial name matching."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Introduction to Programming", user_id=user.id)

    results = quiz_repo.search_by_name("gram")

    assert len(results) >= 1


def test_search_by_name_empty_results(test_db):
    """Test search with no matching results."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    results = quiz_repo.search_by_name("NonExistentPattern")

    assert len(results) == 0


def test_search_results_ordered_by_name(test_db):
    """Test that search results are ordered by name."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Z Test Quiz", user_id=user.id)
    quiz_repo.create_quiz(name="A Test Quiz", user_id=user.id)
    quiz_repo.create_quiz(name="M Test Quiz", user_id=user.id)

    results = quiz_repo.search_by_name("Test")
    names = [q.name for q in results]

    assert names == sorted(names)


# =============================================================================
# QUIZ MODIFICATION TESTS
# =============================================================================

def test_update_quiz(test_db):
    """Test updating quiz fields."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(name="Old Name", user_id=user.id)

    updated = quiz_repo.update(
        quiz,
        name="New Name",
        subject="New Subject",
        description="New Description"
    )

    assert updated.name == "New Name"
    assert updated.subject == "New Subject"
    assert updated.description == "New Description"


def test_update_partial(test_db):
    """Test partial update of quiz."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(
        name="Quiz", user_id=user.id,
        subject="Old Subject",
        description="Old Description"
    )

    updated = quiz_repo.update(quiz, subject="New Subject")

    assert updated.name == "Quiz"  # Unchanged
    assert updated.subject == "New Subject"  # Changed
    assert updated.description == "Old Description"  # Unchanged


# =============================================================================
# QUIZ DELETION TESTS
# =============================================================================

def test_delete_quiz(test_db):
    """Test deleting a quiz."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(name="To Delete", user_id=user.id)
    quiz_id = quiz.id

    quiz_repo.delete(quiz)

    assert quiz_repo.get_by_id(quiz_id) is None


def test_delete_by_id(test_db):
    """Test deleting quiz by ID."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(name="To Delete", user_id=user.id)

    result = quiz_repo.delete_by_id(quiz.id)

    assert result is True
    assert quiz_repo.get_by_id(quiz.id) is None


def test_delete_by_id_not_found(test_db):
    """Test deleting non-existent quiz returns False."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    result = quiz_repo.delete_by_id(99999)

    assert result is False


def test_delete_quiz_with_flashcards(test_db):
    """Test deleting quiz cascades to flashcards."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz(name="Quiz with Cards", user_id=user.id)
    flashcard_repo.create_flashcard(
        quiz.id,
        {"title": "Q", "text": "Question"},
        {"text": "Answer"}
    )

    # Delete quiz (should cascade to flashcards)
    quiz_repo.delete(quiz)

    # Verify quiz is deleted
    assert quiz_repo.get_by_id(quiz.id) is None

    # Verify flashcards are also deleted
    flashcards = flashcard_repo.get_by_quiz_id(quiz.id)
    assert len(flashcards) == 0


# =============================================================================
# CATEGORY AND LEVEL TESTS
# =============================================================================

def test_create_quiz_with_category(test_db):
    """Test creating quiz with category."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(
        name="Poland Geography",
        user_id=user.id,
        subject="Geography",
        category="Poland"
    )

    assert quiz.category == "Poland"


def test_create_quiz_with_level(test_db):
    """Test creating quiz with level."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(
        name="Beginner Math",
        user_id=user.id,
        subject="Mathematics",
        level="Beginner"
    )

    assert quiz.level == "Beginner"


def test_create_quiz_with_category_and_level(test_db):
    """Test creating quiz with both category and level."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(
        name="Advanced Polish History",
        user_id=user.id,
        subject="History",
        category="Poland",
        level="Class 8"
    )

    assert quiz.category == "Poland"
    assert quiz.level == "Class 8"


def test_get_by_category(test_db):
    """Test getting quizzes by category."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Poland Geo", user_id=user.id, subject="Geography", category="Poland")
    quiz_repo.create_quiz(name="France Geo", user_id=user.id, subject="Geography", category="France")
    quiz_repo.create_quiz(name="Poland History", user_id=user.id, subject="History", category="Poland")

    poland_quizzes = quiz_repo.get_by_category("Poland", user_id=user.id)

    assert len(poland_quizzes) == 2
    assert all(q.category == "Poland" for q in poland_quizzes)


def test_get_by_level(test_db):
    """Test getting quizzes by level."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Math 1", user_id=user.id, subject="Mathematics", level="Beginner")
    quiz_repo.create_quiz(name="Math 2", user_id=user.id, subject="Mathematics", level="Advanced")
    quiz_repo.create_quiz(name="Science 1", user_id=user.id, subject="Science", level="Beginner")

    beginner_quizzes = quiz_repo.get_by_level("Beginner", user_id=user.id)

    assert len(beginner_quizzes) == 2
    assert all(q.level == "Beginner" for q in beginner_quizzes)


def test_get_all_categories(test_db):
    """Test getting all unique categories."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Quiz 1", user_id=user.id, category="Poland")
    quiz_repo.create_quiz(name="Quiz 2", user_id=user.id, category="France")
    quiz_repo.create_quiz(name="Quiz 3", user_id=user.id, category="Poland")
    quiz_repo.create_quiz(name="Quiz 4", user_id=user.id)  # No category

    categories = quiz_repo.get_all_categories(user_id=user.id)

    assert "Poland" in categories
    assert "France" in categories
    assert len(categories) == 2


def test_get_all_levels(test_db):
    """Test getting all unique levels."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Quiz 1", user_id=user.id, level="Beginner")
    quiz_repo.create_quiz(name="Quiz 2", user_id=user.id, level="Advanced")
    quiz_repo.create_quiz(name="Quiz 3", user_id=user.id, level="Beginner")
    quiz_repo.create_quiz(name="Quiz 4", user_id=user.id)  # No level

    levels = quiz_repo.get_all_levels(user_id=user.id)

    assert "Beginner" in levels
    assert "Advanced" in levels
    assert len(levels) == 2


def test_categories_ordered_alphabetically(test_db):
    """Test that categories are returned in alphabetical order."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Quiz 1", user_id=user.id, category="Zebra")
    quiz_repo.create_quiz(name="Quiz 2", user_id=user.id, category="Apple")
    quiz_repo.create_quiz(name="Quiz 3", user_id=user.id, category="Banana")

    categories = quiz_repo.get_all_categories(user_id=user.id)
    categories_list = list(categories)

    assert categories_list == sorted(categories_list)


def test_levels_ordered_alphabetically(test_db):
    """Test that levels are returned in alphabetical order."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz_repo.create_quiz(name="Quiz 1", user_id=user.id, level="Class 8")
    quiz_repo.create_quiz(name="Quiz 2", user_id=user.id, level="Beginner")
    quiz_repo.create_quiz(name="Quiz 3", user_id=user.id, level="Advanced")

    levels = quiz_repo.get_all_levels(user_id=user.id)
    levels_list = list(levels)

    assert levels_list == sorted(levels_list)


# =============================================================================
# BASE REPOSITORY FUNCTIONALITY TESTS
# =============================================================================

def test_refresh(test_db):
    """Test refreshing a quiz instance from database."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    # Modify quiz using repository update method instead of raw SQL
    quiz_repo.update(quiz, name="Modified")

    # Refresh should reload from database
    test_db.expire(quiz)
    refreshed = quiz_repo.refresh(quiz)
    assert refreshed.name == "Modified"


def test_bulk_create(test_db):
    """Test bulk creating quizzes."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)

    quizzes_data = [
        {"name": "Quiz 1", "user_id": user.id, "subject": "Math"},
        {"name": "Quiz 2", "user_id": user.id, "subject": "Science"},
        {"name": "Quiz 3", "user_id": user.id, "subject": "History"}
    ]

    created = quiz_repo.bulk_create(quizzes_data)

    assert len(created) == 3
    assert all(q.id is not None for q in created)


def test_bulk_delete(test_db):
    """Test bulk deleting quizzes."""
    user = _create_test_user(test_db)
    quiz_repo = QuizRepository(test_db)

    quiz1 = quiz_repo.create_quiz(name="Quiz 1", user_id=user.id)
    quiz2 = quiz_repo.create_quiz(name="Quiz 2", user_id=user.id)
    quiz3 = quiz_repo.create_quiz(name="Quiz 3", user_id=user.id)

    count = quiz_repo.bulk_delete([quiz1, quiz2, quiz3])

    assert count == 3
    assert quiz_repo.get_by_id(quiz1.id) is None
    assert quiz_repo.get_by_id(quiz2.id) is None
    assert quiz_repo.get_by_id(quiz3.id) is None
