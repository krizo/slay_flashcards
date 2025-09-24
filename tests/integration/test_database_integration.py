from unittest.mock import Mock

from learning.sessions.quiz_session import TestSessionConfig, TestSession
from services.audio_service import SilentAudioService
from services.quiz_service import QuizService
from services.user_service import UserService


def test_test_mode_with_real_database(test_db, example_quiz_data):
    """Test complete test mode flow with real database."""
    quiz_service = QuizService(test_db)
    user_service = UserService(test_db)

    # Import quiz and get flashcards
    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)
    cards = quiz_service.get_quiz_flashcards(quiz.id)

    assert len(cards) == 3
    assert quiz.name == "French Basics"

    # Create user
    user = user_service.create_user("integration_test_user")
    assert user.name == "integration_test_user"

    # Run test session
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(side_effect=["chien", "chat", "maison"])  # All correct
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    config = TestSessionConfig(audio_enabled=False)
    session = TestSession(cards, presenter, SilentAudioService(), config)

    result = session.start()
    assert result.value == "completed"
    assert session.get_final_score() == 100

    # Save session to database
    final_score = session.get_final_score()
    db_session = user_service.create_session(user.id, quiz.id, "test", final_score)

    # Verify database record
    assert db_session.user_id == user.id
    assert db_session.quiz_id == quiz.id
    assert db_session.mode == "test"
    assert db_session.score == 100
    assert db_session.started_at is not None

    # Verify user progress includes this session
    user_sessions = user_service.get_user_sessions(user.id)
    assert len(user_sessions) == 1
    assert user_sessions[0].id == db_session.id


def test_multiple_users_test_sessions(test_db, example_quiz_data):
    """Test multiple users taking tests on the same quiz."""
    quiz_service = QuizService(test_db)
    user_service = UserService(test_db)

    # Import quiz
    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)
    cards = quiz_service.get_quiz_flashcards(quiz.id)

    # Create multiple users with different performance
    users_and_scores = [
        ("alice", ["chien", "chat", "maison"], 100),     # Perfect
        ("bob", ["chien", "cat", "house"], (20, 40)),    # Mixed
        ("charlie", ["chein", "caht", "maizon"], (70, 85)), # Typos - partial credit
    ]

    session_records = []

    for username, answers, expected_score_range in users_and_scores:
        # Create user
        user = user_service.create_user(username)

        # Run test
        presenter = Mock()
        presenter.show_test_header = Mock()
        presenter.show_question = Mock()
        presenter.get_user_answer = Mock(side_effect=answers)
        presenter.show_answer_result = Mock()
        presenter.wait_for_next = Mock()

        config = TestSessionConfig(audio_enabled=False, similarity_threshold=0.7)
        session = TestSession(cards, presenter, SilentAudioService(), config)
        session.start()

        final_score = session.get_final_score()

        # Save session
        db_session = user_service.create_session(user.id, quiz.id, "test", final_score)
        session_records.append((username, final_score, db_session))

        # Verify score is in expected range
        if expected_score_range == 100:
            assert final_score == 100
        elif expected_score_range == 33:
            assert 20 <= final_score <= 50  # Approximately 1/3
        else:  # Partial credit case
            assert 40 <= final_score <= 80  # Partial credit range

    # Verify all sessions are independent
    all_sessions = []
    for username, _, _ in users_and_scores:
        user = user_service.get_user_by_name(username)
        user_sessions = user_service.get_user_sessions(user.id)
        assert len(user_sessions) == 1
        all_sessions.extend(user_sessions)

    assert len(all_sessions) == 3
    assert len(set(s.user_id for s in all_sessions)) == 3  # Different users


def test_user_progress_tracking_integration(test_db, example_quiz_data):
    """Test user progress tracking across multiple test sessions."""
    quiz_service = QuizService(test_db)
    user_service = UserService(test_db)

    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)
    user = user_service.create_user("progress_test_user")

    # From the example.json file: dog->chien, cat->chat, house->maison
    test_sessions = [
        (["hello", "goodbye", "thanks"], "First attempt - All English (wrong)"),
        (["chien", "goodbye", "maison"], "Second attempt - 2/3 correct"),
        (["chien", "chat", "maison"], "Third attempt - All correct"),
    ]

    session_scores = []

    for answers, description in test_sessions:
        cards = quiz_service.get_quiz_flashcards(quiz.id)

        presenter = Mock()
        presenter.show_test_header = Mock()
        presenter.show_question = Mock()
        presenter.get_user_answer = Mock(side_effect=answers)
        presenter.show_answer_result = Mock()
        presenter.wait_for_next = Mock()

        config = TestSessionConfig(
            audio_enabled=False,
            similarity_threshold=0.8,
            allow_partial_credit=True,
            strict_matching=False,
            case_sensitive=False
        )
        session = TestSession(cards, presenter, SilentAudioService(), config)
        result = session.start()

        final_score = session.get_final_score()
        session_scores.append(final_score)

        # Save to database
        user_service.create_session(user.id, quiz.id, "test", final_score)

    # Verify improvement trend
    assert len(session_scores) == 3

    # More specific checks
    assert session_scores[0] == 0, f"Expected 0% for all wrong answers, got {session_scores[0]}%"
    assert session_scores[2] == 100, f"Expected 100% for all correct answers, got {session_scores[2]}%"
    assert session_scores[2] > session_scores[0], f"Expected improvement: {session_scores[0]}% -> {session_scores[2]}%"

    # Get user statistics
    user_sessions = user_service.get_user_sessions(user.id)
    assert len(user_sessions) == 3

    test_sessions_only = [s for s in user_sessions if s.mode == "test"]
    assert len(test_sessions_only) == 3

    # Sort by timestamp to get chronological order
    chronological_sessions = sorted(test_sessions_only, key=lambda x: x.started_at)
    chronological_scores = [s.score for s in chronological_sessions]

    # Verify the scores match our expected progression (0 -> 67 -> 100)
    assert chronological_scores == [0, 67, 100], f"Expected [0, 67, 100] chronologically, got {chronological_scores}"

    # Verify all sessions have correct metadata
    for session in test_sessions_only:
        assert session.user_id == user.id
        assert session.quiz_id == quiz.id
        assert session.mode == "test"
        assert session.score in [0, 67, 100]
        assert session.started_at is not None


def test_user_progress_tracking_integration_simple(test_db, example_quiz_data):
    """Simplified version that just tests the core functionality."""
    quiz_service = QuizService(test_db)
    user_service = UserService(test_db)

    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)
    user = user_service.create_user("progress_test_user_simple")

    # Test sessions with known scores
    expected_scores = [0, 67, 100]
    test_sessions = [
        (["hello", "goodbye", "thanks"], 0),      # All wrong
        (["chien", "goodbye", "maison"], 67),     # 2/3 correct
        (["chien", "chat", "maison"], 100),       # All correct
    ]

    actual_scores = []

    for answers, expected_score in test_sessions:
        cards = quiz_service.get_quiz_flashcards(quiz.id)

        presenter = Mock()
        presenter.show_test_header = Mock()
        presenter.show_question = Mock()
        presenter.get_user_answer = Mock(side_effect=answers)
        presenter.show_answer_result = Mock()
        presenter.wait_for_next = Mock()

        config = TestSessionConfig(audio_enabled=False, similarity_threshold=0.8)
        session = TestSession(cards, presenter, SilentAudioService(), config)
        session.start()

        final_score = session.get_final_score()
        actual_scores.append(final_score)

        # Save to database
        user_service.create_session(user.id, quiz.id, "test", final_score)

    # Verify scores match expectations
    assert actual_scores == expected_scores, f"Expected {expected_scores}, got {actual_scores}"

    # Verify database storage
    user_sessions = user_service.get_user_sessions(user.id)
    test_sessions_only = [s for s in user_sessions if s.mode == "test"]

    assert len(test_sessions_only) == 3

    # Verify improvement over time (chronologically)
    chronological_sessions = sorted(test_sessions_only, key=lambda x: x.started_at)
    chronological_scores = [s.score for s in chronological_sessions]

    assert chronological_scores[0] < chronological_scores[2]  # Improvement over time
    assert 0 in chronological_scores  # Had at least one failure
    assert 100 in chronological_scores  # Had at least one perfect score


def test_quiz_statistics_integration(test_db, example_quiz_data):
    """Test quiz statistics with real test data."""
    quiz_service = QuizService(test_db)
    user_service = UserService(test_db)

    # Import quiz
    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)

    # Get quiz statistics
    stats = quiz_service.get_quiz_statistics(quiz.id)

    assert stats["total_cards"] == 3
    assert stats["subject"] == "French"
    assert "difficulty_distribution" in stats
    assert "question_languages" in stats
    assert "answer_languages" in stats

    # Verify language distribution
    assert stats["question_languages"]["en"] == 3  # All questions in English
    assert stats["answer_languages"]["fr"] == 3   # All answers in French

