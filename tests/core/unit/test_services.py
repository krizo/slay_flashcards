from core.services.quiz_service import QuizService


def test_quiz_service_import_quiz_from_dict(quiz_service, example_quiz_data):
    """Test importing quiz from dictionary."""
    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)

    assert quiz.name == "French Basics"
    assert quiz.subject == "French"
    assert quiz.description == "Basic French vocabulary for beginners"
    assert len(quiz.flashcards) == 3


def test_quiz_service_import_quiz_from_file(quiz_service, temp_quiz_file):
    """Test importing quiz from file."""
    quiz = quiz_service.import_quiz_from_file(temp_quiz_file)

    assert quiz.name == "French Basics"
    assert len(quiz.flashcards) == 3


def test_quiz_service_get_all_quizzes(quiz_service, example_quiz_data):
    """Test getting all quizzes."""
    quiz_service.import_quiz_from_dict(example_quiz_data)
    quiz_service.create_quiz("Another Quiz", "Spanish")

    quizzes = quiz_service.get_all_quizzes()
    assert len(quizzes) == 2


def test_quiz_service_get_quiz_flashcards(quiz_service, sample_quiz_with_cards):
    """Test getting flashcards for a quiz."""
    cards = quiz_service.get_quiz_flashcards(sample_quiz_with_cards.id)

    assert len(cards) == 3
    card_titles = [c.question_title for c in cards]
    assert "dog" in card_titles
    assert "cat" in card_titles
    assert "house" in card_titles


def test_quiz_service_get_flashcards_by_difficulty(quiz_service, sample_quiz_with_cards):
    """Test getting flashcards by difficulty."""
    easy_cards = quiz_service.get_flashcards_by_difficulty(sample_quiz_with_cards.id, 1)
    medium_cards = quiz_service.get_flashcards_by_difficulty(sample_quiz_with_cards.id, 2)

    assert len(easy_cards) == 2
    assert len(medium_cards) == 1


def test_quiz_service_search_flashcards(quiz_service, sample_quiz_with_cards):
    """Test searching flashcards by text."""
    results = quiz_service.search_flashcards(sample_quiz_with_cards.id, "dog")
    assert len(results) == 1
    assert results[0].question_title == "dog"


def test_quiz_service_get_quiz_statistics(quiz_service, sample_quiz_with_cards):
    """Test getting quiz statistics."""
    stats = quiz_service.get_quiz_statistics(sample_quiz_with_cards.id)

    assert stats["total_cards"] == 3
    assert stats["difficulty_distribution"] == {1: 2, 2: 1}
    assert stats["question_languages"] == {"en": 3}
    assert stats["answer_languages"] == {"fr": 3}
    assert stats["subject"] == "French"


def test_quiz_service_validate_quiz_data_valid(quiz_service, example_quiz_data):
    """Test validation of valid quiz data."""
    assert quiz_service.validate_quiz_data(example_quiz_data) is True


def test_quiz_service_validate_quiz_data_invalid():
    """Test validation of invalid quiz data."""
    quiz_service = QuizService(None)  # Don't need DB for validation

    # Missing quiz section
    invalid_data = {"flashcards": []}
    assert quiz_service.validate_quiz_data(invalid_data) is False

    # Missing quiz name
    invalid_data = {"quiz": {"subject": "Math"}}
    assert quiz_service.validate_quiz_data(invalid_data) is False

    # Invalid flashcard structure
    invalid_data = {
        "quiz": {"name": "Test"},
        "flashcards": [{"question": {"title": "test"}}]  # Missing answer
    }
    assert quiz_service.validate_quiz_data(invalid_data) is False


def test_user_service_create_user(user_service):
    """Test creating a user."""
    user = user_service.create_user("alice")
    assert user.name == "alice"
    assert user.id is not None


def test_user_service_ensure_user_exists_new(user_service):
    """Test ensuring user exists creates new user."""
    user = user_service.ensure_user_exists("newuser")
    assert user.name == "newuser"


def test_user_service_ensure_user_exists_existing(user_service, sample_user):
    """Test ensuring user exists returns existing user."""
    user = user_service.ensure_user_exists(sample_user.name)
    assert user.id == sample_user.id


def test_user_service_create_session(user_service, quiz_service, sample_user, example_quiz_data):
    """Test creating a learning session."""
    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)
    session = user_service.create_session(sample_user.id, quiz.id, "learn")

    assert session.user_id == sample_user.id
    assert session.quiz_id == quiz.id
    assert session.mode == "learn"


def test_user_service_get_user_statistics_empty(user_service, sample_user):
    """Test getting statistics for user with no sessions."""
    stats = user_service.get_user_statistics(sample_user.id)

    assert stats["total_sessions"] == 0
    assert stats["learn_sessions"] == 0
    assert stats["test_sessions"] == 0
    assert stats["average_score"] is None
    assert stats["study_streak"] == 0


def test_user_service_get_user_statistics_with_sessions(user_service, quiz_service, sample_user, example_quiz_data):
    """Test getting statistics for user with sessions."""
    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)

    # Create some sessions
    user_service.create_session(sample_user.id, quiz.id, "learn")
    user_service.create_session(sample_user.id, quiz.id, "test", 85)
    user_service.create_session(sample_user.id, quiz.id, "test", 92)

    stats = user_service.get_user_statistics(sample_user.id)

    assert stats["total_sessions"] == 3
    assert stats["learn_sessions"] == 1
    assert stats["test_sessions"] == 2
    assert stats["average_score"] == 88.5  # (85 + 92) / 2
    assert len(stats["favorite_subjects"]) == 1
    assert stats["favorite_subjects"][0]["subject"] == "French"


def test_user_service_get_sessions_by_mode(user_service, quiz_service, sample_user, example_quiz_data):
    """Test getting sessions filtered by mode."""
    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)

    user_service.create_session(sample_user.id, quiz.id, "learn")
    user_service.create_session(sample_user.id, quiz.id, "learn")
    user_service.create_session(sample_user.id, quiz.id, "test", 80)

    learn_sessions = user_service.get_sessions_by_mode(sample_user.id, "learn")
    test_sessions = user_service.get_sessions_by_mode(sample_user.id, "test")

    assert len(learn_sessions) == 2
    assert len(test_sessions) == 1
