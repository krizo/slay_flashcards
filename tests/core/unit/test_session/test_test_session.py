from unittest.mock import Mock, patch

from core.learning.sessions.quiz_session import TestSession, TestResult, AnswerEvaluation, TestSessionConfig


def test_test_session_empty_flashcards(mock_test_presenter, silent_audio_service, default_test_config):
    """Test session with no flashcards."""
    session = TestSession([], mock_test_presenter, silent_audio_service, default_test_config)

    result = session.start()

    assert result == TestResult.COMPLETED
    assert session.get_final_score() == 0
    assert len(session.results) == 0


def test_test_session_single_correct_answer(mock_flashcard, silent_audio_service, default_test_config):
    """Test session with one correct answer."""
    # Mock presenter that provides correct answer
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(return_value="chien")
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    session = TestSession([mock_flashcard], presenter, silent_audio_service, default_test_config)

    result = session.start()

    assert result == TestResult.COMPLETED
    assert session.get_final_score() == 100
    assert len(session.results) == 1
    assert session.results[0].evaluation == AnswerEvaluation.CORRECT


def test_test_session_single_incorrect_answer(mock_flashcard, silent_audio_service, default_test_config):
    """Test session with one incorrect answer."""
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(return_value="cat")
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    session = TestSession([mock_flashcard], presenter, silent_audio_service, default_test_config)

    result = session.start()

    assert result == TestResult.COMPLETED
    assert session.get_final_score() == 0
    assert len(session.results) == 1
    assert session.results[0].evaluation == AnswerEvaluation.INCORRECT


def test_test_session_mixed_answers(mock_flashcards, silent_audio_service, default_test_config):
    """Test session with mixed correct and incorrect answers."""
    # Provide answers: correct, incorrect, correct
    answers = ["chien", "wrong", "maison"]
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(side_effect=answers)
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    session = TestSession(mock_flashcards, presenter, silent_audio_service, default_test_config)

    result = session.start()

    assert result == TestResult.COMPLETED
    assert session.get_final_score() == 67  # 2/3 = 66.7% rounded to 67%
    assert len(session.results) == 3
    assert session.results[0].evaluation == AnswerEvaluation.CORRECT
    assert session.results[1].evaluation == AnswerEvaluation.INCORRECT
    assert session.results[2].evaluation == AnswerEvaluation.CORRECT


def test_test_session_early_quit(mock_flashcard, silent_audio_service, default_test_config):
    """Test quitting early with 'quit' command."""
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(return_value="quit")
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    session = TestSession([mock_flashcard], presenter, silent_audio_service, default_test_config)

    result = session.start()

    assert result == TestResult.QUIT_EARLY
    assert len(session.results) == 0


def test_test_session_early_quit_variations(mock_flashcard, silent_audio_service, default_test_config):
    """Test different ways to quit early."""
    quit_commands = ["quit", "exit", "q", "QUIT", "Exit"]

    for quit_cmd in quit_commands:
        presenter = Mock()
        presenter.show_test_header = Mock()
        presenter.show_question = Mock()
        presenter.get_user_answer = Mock(return_value=quit_cmd)
        presenter.show_answer_result = Mock()
        presenter.wait_for_next = Mock()

        session = TestSession([mock_flashcard], presenter, silent_audio_service, default_test_config)
        result = session.start()

        assert result == TestResult.QUIT_EARLY


def test_test_session_keyboard_interrupt(mock_flashcard, silent_audio_service, default_test_config):
    """Test handling keyboard interrupt."""
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock(side_effect=KeyboardInterrupt())

    session = TestSession([mock_flashcard], presenter, silent_audio_service, default_test_config)

    result = session.start()

    assert result == TestResult.INTERRUPTED


def test_test_session_partial_credit_scoring(mock_flashcard, silent_audio_service):
    """Test partial credit affects final score."""
    config = TestSessionConfig(
        audio_enabled=False,
        allow_partial_credit=True,
        similarity_threshold=0.7
    )

    # Answer with typo should get partial credit
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(return_value="chein")  # Typo
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    session = TestSession([mock_flashcard], presenter, silent_audio_service, config)

    result = session.start()

    assert result == TestResult.COMPLETED
    assert 0 < session.get_final_score() < 100  # Should get partial score
    assert session.results[0].evaluation == AnswerEvaluation.PARTIAL


def test_test_session_detailed_results(mock_flashcard, silent_audio_service, default_test_config):
    """Test detailed results generation."""
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(return_value="chien")
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    session = TestSession([mock_flashcard], presenter, silent_audio_service, default_test_config)
    session.start()

    results = session.get_detailed_results()

    assert results["total_questions"] == 1
    assert results["correct"] == 1
    assert results["partial"] == 0
    assert results["incorrect"] == 0
    assert results["final_score"] == 100
    assert len(results["breakdown"]) == 1

    breakdown_item = results["breakdown"][0]
    assert breakdown_item["question"] == "dog"
    assert breakdown_item["user_answer"] == "chien"
    assert breakdown_item["correct_answer"] == "chien"
    assert breakdown_item["evaluation"] == "correct"
    assert breakdown_item["score"] == 1.0


def test_test_session_audio_integration(mock_flashcard, default_test_config):
    """Test audio integration in test session."""
    # Mock audio service
    audio_service = Mock()
    audio_service.is_available.return_value = True
    audio_service.play_text.return_value = True

    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(return_value="chien")
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    # Enable audio in config
    config = TestSessionConfig(
        audio_enabled=True,
        question_lang="en",
        answer_lang="fr"
    )

    session = TestSession([mock_flashcard], presenter, audio_service, config)
    session.start()

    # Verify audio was played for both question and answer
    assert audio_service.play_text.call_count == 2

    # Check the calls were made with correct text and languages
    calls = audio_service.play_text.call_args_list
    question_call = calls[0]
    answer_call = calls[1]

    assert question_call[0][0] == "What is 'dog' in French?"  # Question text
    assert answer_call[0][0] == "chien"  # Answer text


@patch('learning.sessions.test_session.TestSession._get_question_language')
@patch('learning.sessions.test_session.TestSession._get_answer_language')
def test_test_session_language_override(mock_answer_lang, mock_question_lang, mock_flashcard, silent_audio_service):
    """Test language override functionality."""
    mock_question_lang.return_value = "pl"
    mock_answer_lang.return_value = "de"

    config = TestSessionConfig(
        audio_enabled=True,
        question_lang="pl",
        answer_lang="de",
        override_card_languages=True
    )

    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock(return_value="chien")
    presenter.show_answer_result = Mock()
    presenter.wait_for_next = Mock()

    session = TestSession([mock_flashcard], presenter, silent_audio_service, config)
    session.start()

    # Verify language methods were called
    mock_question_lang.assert_called_once_with(mock_flashcard)
    mock_answer_lang.assert_called_once_with(mock_flashcard)
