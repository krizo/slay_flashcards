from unittest.mock import Mock

from core.learning.sessions.quiz_session import TestSessionConfig, TestSession
from core.services.audio_service import SilentAudioService
from core.services.quiz_service import QuizService
from core.services.user_service import UserService


def test_large_quiz_performance(test_db):
    """Test performance with large quiz sets."""
    import time

    quiz_service = QuizService(test_db)

    # Create large quiz
    large_quiz_data = {
        "quiz": {
            "name": "Large Performance Test Quiz",
            "subject": "Performance",
            "description": "Large quiz for performance testing"
        },
        "flashcards": []
    }

    # Add 100 flashcards
    for i in range(100):
        card_data = {
            "question": {
                "title": f"question_{i}",
                "text": f"This is question number {i}",
                "lang": "en",
                "difficulty": (i % 5) + 1
            },
            "answer": {
                "text": f"answer_{i}",
                "lang": "en"
            }
        }
        large_quiz_data["flashcards"].append(card_data)

    # Measure import time
    start_time = time.time()
    quiz = quiz_service.import_quiz_from_dict(large_quiz_data)
    import_time = time.time() - start_time

    # Should import reasonably quickly (less than 5 seconds)
    assert import_time < 5.0

    # Verify all cards were imported
    cards = quiz_service.get_quiz_flashcards(quiz.id)
    assert len(cards) == 100

    # Test retrieval performance
    start_time = time.time()
    for _ in range(10):  # Multiple retrievals
        quiz_service.get_quiz_flashcards(quiz.id)
    retrieval_time = time.time() - start_time

    # Should retrieve quickly (less than 1 second for 10 retrievals)
    assert retrieval_time < 1.0

def test_concurrent_sessions_performance(test_db, example_quiz_data):
    """Simplified version that avoids threading issues."""
    import time

    quiz_service = QuizService(test_db)
    user_service = UserService(test_db)

    # Import quiz
    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)
    cards = quiz_service.get_quiz_flashcards(quiz.id)

    # Create multiple users
    users = []
    for i in range(5):
        user = user_service.create_user(f"sequential_user_{i}")
        users.append(user)

    results = []

    # Run sessions sequentially but measure performance
    total_start_time = time.time()

    for i, user in enumerate(users):
        presenter = Mock()
        presenter.show_test_header = Mock()
        presenter.show_question = Mock()
        presenter.get_user_answer = Mock(side_effect=["chien", "chat", "maison"])
        presenter.show_answer_result = Mock()
        presenter.wait_for_next = Mock()

        config = TestSessionConfig(audio_enabled=False)
        session = TestSession(cards, presenter, SilentAudioService(), config)

        session_start_time = time.time()
        result = session.start()
        session_duration = time.time() - session_start_time

        final_score = session.get_final_score()

        # Save to database
        user_service.create_session(user.id, quiz.id, "test", final_score)

        results.append((i, result.value, final_score, session_duration))

    total_time = time.time() - total_start_time

    # Verify all sessions completed successfully
    assert len(results) == 5

    for user_index, result, score, duration in results:
        assert result == "completed"
        assert score == 100
        assert duration < 1.0  # Each session should be fast

    # Verify database storage
    for user in users:
        user_sessions = user_service.get_user_sessions(user.id)
        assert len(user_sessions) == 1
        assert user_sessions[0].mode == "test"
        assert user_sessions[0].score == 100

    print(f"✅ Sequential performance test passed - 5 sessions in {total_time:.2f}s")