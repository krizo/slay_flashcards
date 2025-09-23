from unittest.mock import Mock

from learning.sessions.test_session import TestSessionConfig, TestSession
from services.audio_service import SilentAudioService
from services.quiz_service import QuizService
from services.user_service import UserService


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
    """Test performance with multiple concurrent test sessions."""
    import threading
    import time

    quiz_service = QuizService(test_db)
    user_service = UserService(test_db)

    # Import quiz
    quiz = quiz_service.import_quiz_from_dict(example_quiz_data)
    cards = quiz_service.get_quiz_flashcards(quiz.id)

    # Create multiple users
    users = []
    for i in range(5):
        user = user_service.create_user(f"concurrent_user_{i}")
        users.append(user)

    results = []

    def run_test_session(user, user_index):
        """Run a test session for a user."""
        presenter = Mock()
        presenter.show_test_header = Mock()
        presenter.show_question = Mock()
        presenter.get_user_answer = Mock(side_effect=["chien", "chat", "maison"])
        presenter.show_answer_result = Mock()
        presenter.wait_for_next = Mock()

        config = TestSessionConfig(audio_enabled=False)
        session = TestSession(cards, presenter, SilentAudioService(), config)

        start_time = time.time()
        result = session.start()
        duration = time.time() - start_time

        final_score = session.get_final_score()

        # Save to database
        user_service.create_session(user.id, quiz.id, "test", final_score)

        results.append((user_index, result.value, final_score, duration))

    # Run sessions concurrently
    threads = []
    start_time = time.time()

    for i, user in enumerate(users):
        thread = threading.Thread(target=run_test_session, args=(user, i))
        threads.append(thread)
        thread.start()

    # Wait for all to complete
    for thread in threads:
        thread.join()

    total_time = time.time() - start_time

    # All sessions should complete successfully
    assert len(results) == 5
    for user_index, result, score, duration in results:
        assert result == "completed"
        assert score == 100
        assert duration < 1.0  # Each session should be fast

    # Total time should be reasonable (less than 5 seconds)
    assert total_time < 5.0

    # Verify all sessions were saved independently
    for user in users:
        user_sessions = user_service.get_user_sessions(user.id)
        assert len(user_sessions) == 1
        assert user_sessions[0].mode == "test"
        assert user_sessions[0].score == 100
