from unittest.mock import Mock

import pytest

from learning.sessions.test_session import TestSessionConfig, TestSession
from services.audio_service import SilentAudioService
from services.quiz_service import QuizService
from services.user_service import UserService


def test_database_error_handling(test_db):
    """Test handling of database errors during test sessions."""
    quiz_service = QuizService(test_db)
    user_service = UserService(test_db)

    # Create valid quiz and user first
    quiz_data = {
        "quiz": {"name": "Error Test Quiz", "subject": "Testing"},
        "flashcards": [
            {
                "question": {"title": "test", "text": "test"},
                "answer": {"text": "answer"}
            }
        ]
    }

    quiz = quiz_service.import_quiz_from_dict(quiz_data)
    user_service.create_user("error_test_user")

    # Test with invalid quiz ID
    with pytest.raises((ValueError, AttributeError)) or pytest.warns():
        quiz_service.get_quiz_flashcards(99999)  # Non-existent quiz

    # Test with invalid user ID
    with pytest.raises((ValueError, AttributeError)) or pytest.warns():
        user_service.create_session(99999, quiz.id, "test", 100)  # Non-existent user


def test_audio_service_error_handling():
    """Test handling of audio service errors."""
    # Test with mock audio service that fails
    failing_audio_service = Mock()
    failing_audio_service.is_available.return_value = False
    failing_audio_service.play_text.side_effect = Exception("Audio failed")

    card = Mock()
    card.question_title = "test"
    card.question_text = "test"
    card.answer_text = "answer"

    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(return_value="answer")
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    config = TestSessionConfig(audio_enabled=True)
    session = TestSession([card], presenter, failing_audio_service, config)

    # Should complete despite audio failures
    result = session.start()
    assert result.value == "completed"


def test_presenter_error_handling():
    """Test handling of presenter errors."""
    card = Mock()
    card.question_title = "test"
    card.question_text = "test"
    card.answer_text = "answer"

    # Mock presenter that fails on some operations
    failing_presenter = Mock()
    failing_presenter.show_test_header = Mock()
    failing_presenter.show_question = Mock()
    failing_presenter.get_user_answer = Mock(return_value="answer")
    failing_presenter.show_answer_result = Mock(side_effect=Exception("Display failed"))
    failing_presenter.wait_for_next = Mock()

    config = TestSessionConfig(audio_enabled=False)
    session = TestSession([card], presenter=failing_presenter, audio_service=SilentAudioService(), config=config)

    # Should handle presenter failures gracefully
    with pytest.raises(Exception):
        session.start()
