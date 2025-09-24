from unittest.mock import Mock, patch

import pytest

from core.learning.presenters.quiz_presenter import CLITestPresenter
from core.learning.sessions.quiz_session import TestSessionConfig, TestSession, CardResult, AnswerEvaluation
from core.services.audio_service import SilentAudioService, GTTSAudioService
from core.services.quiz_service import QuizService
from core.services.user_service import UserService


def test_audio_service_integration():
    """Test audio service integration with test sessions."""
    # Test SilentAudioService
    silent_service = SilentAudioService()
    assert silent_service.is_available() == True
    assert silent_service.play_text("test") == True
    assert silent_service.play_text("test", "fr") == True

    # Test GTTSAudioService (if available)
    try:
        gtts_service = GTTSAudioService()
        assert gtts_service is not None
        # Don't actually play audio in tests, just verify it doesn't crash
        available = gtts_service.is_available()
        assert isinstance(available, bool)
    except ImportError:
        pytest.skip("GTTS not available for testing")


def test_cli_application_integration():
    """Test CLI application integration with test mode."""
    # This would require more complex mocking of CLI inputs
    # For now, just verify the CLI app can be instantiated
    from cli.cli_application import CLIApplication
    app = CLIApplication()
    assert app is not None
    assert hasattr(app, 'test')
    assert hasattr(app, 'learn')
    assert hasattr(app, 'import_quiz')


@patch('builtins.input')
def test_cli_test_presenter_integration(mock_input, capsys):
    """Test CLI test presenter with actual user input simulation."""
    mock_input.side_effect = ["test_answer", ""]  # Answer + Enter for continue

    presenter = CLITestPresenter()

    # Test complete flow
    presenter.show_test_header(1)

    card = Mock()
    card.question_title = "test"
    card.question_text = "test question"
    card.question_emoji = "❓"

    presenter.show_question(card, 1, 1)

    answer = presenter.get_user_answer()
    assert answer == "test_answer"

    # Test result display
    result = CardResult(card, "test_answer", AnswerEvaluation.CORRECT, 1.0)
    presenter.show_answer_result(result)

    captured = capsys.readouterr()
    assert "Test Mode Started" in captured.out
    assert "test question" in captured.out
    assert "Correct!" in captured.out


def test_end_to_end_workflow(test_db):
    """Test complete end-to-end workflow from quiz creation to test completion."""
    # Create services
    quiz_service = QuizService(test_db)
    user_service = UserService(test_db)

    # Step 1: Create quiz data
    quiz_data = {
        "quiz": {
            "name": "Integration Test Quiz",
            "subject": "Testing",
            "description": "End-to-end test quiz"
        },
        "flashcards": [
            {
                "question": {
                    "title": "capital",
                    "text": "What is the capital of France?",
                    "lang": "en",
                    "difficulty": 1
                },
                "answer": {
                    "text": "Paris",
                    "lang": "en"
                }
            },
            {
                "question": {
                    "title": "color",
                    "text": "What color is the sky?",
                    "lang": "en",
                    "difficulty": 1
                },
                "answer": {
                    "text": "blue",
                    "lang": "en"
                }
            }
        ]
    }

    # Step 2: Import quiz
    quiz = quiz_service.import_quiz_from_dict(quiz_data)
    assert quiz.name == "Integration Test Quiz"

    # Step 3: Get flashcards
    cards = quiz_service.get_quiz_flashcards(quiz.id)
    assert len(cards) == 2

    # Step 4: Create user
    user = user_service.ensure_user_exists("end_to_end_user")

    # Step 5: Run learning session first
    learning_session = user_service.create_session(user.id, quiz.id, "learn")
    assert learning_session.mode == "learn"

    # Step 6: Run test session
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(side_effect=["Paris", "blue"])
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    config = TestSessionConfig(audio_enabled=False)
    test_session = TestSession(cards, presenter, SilentAudioService(), config)

    result = test_session.start()
    assert result.value == "completed"
    assert test_session.get_final_score() == 100

    # Step 7: Save test session
    final_score = test_session.get_final_score()
    db_test_session = user_service.create_session(user.id, quiz.id, "test", final_score)

    # Step 8: Verify complete workflow
    user_sessions = user_service.get_user_sessions(user.id)
    assert len(user_sessions) == 2

    learn_sessions = [s for s in user_sessions if s.mode == "learn"]
    test_sessions = [s for s in user_sessions if s.mode == "test"]

    assert len(learn_sessions) == 1
    assert len(test_sessions) == 1
    assert test_sessions[0].score == 100

