"""
tests/e2e/scenarios/user_journeys/test_new_user_onboarding.py

Simple E2E test that uses the fixtures correctly.
"""
from unittest.mock import Mock

import pytest

from learning.sessions.test_session import TestSessionConfig


def test_basic_user_workflow(
    e2e_services,
    basic_french_quiz,
    quiz_workflow,
    mock_presenter_factory,
    create_user_with_persona,
    progress_analyzer,
    test_validators
):
    """Test basic user workflow from quiz import to completion."""

    # Phase 1: Import quiz
    quiz, cards = quiz_workflow.create_and_import_quiz(basic_french_quiz)
    test_validators.validate_quiz_structure(quiz)
    assert len(cards) == 4

    # Phase 2: Create user
    user = create_user_with_persona("beginner_student", "test_user")
    assert user.name == "test_user"

    # Phase 3: Run initial test (poor performance expected)
    initial_presenter = mock_presenter_factory(["hello", "goodbye", "thanks", "please"])
    config = TestSessionConfig(audio_enabled=False, similarity_threshold=0.6)

    initial_results = quiz_workflow.run_test_session(user, quiz, cards, initial_presenter, config)

    assert initial_results["result"].value == "completed"
    assert initial_results["score"] <= 30  # Poor initial performance with English answers

    # Phase 4: Learning sessions
    for _ in range(3):
        session = quiz_workflow.run_learning_session(user, quiz.id)
        test_validators.validate_user_session(session)

    # Phase 5: Improved test
    improved_presenter = mock_presenter_factory(["bonjour", "au revoir", "merci", "s'il vous plaît"])

    improved_results = quiz_workflow.run_test_session(user, quiz, cards, improved_presenter, config)

    assert improved_results["result"].value == "completed"
    assert improved_results["score"] >= 80  # Should show significant improvement

    # Phase 6: Validate progress
    progress = progress_analyzer.get_user_progress(user)

    assert progress["total_sessions"] >= 5  # 2 tests + 3 learning sessions
    assert progress["test_sessions"] == 2
    assert progress["learn_sessions"] == 3

    test_validators.validate_score_progression(progress["test_scores"], should_improve=True)


def test_quiz_import_and_basic_functionality(
    e2e_services,
    basic_french_quiz,
    quiz_workflow,
    test_validators
):
    """Test basic quiz import and structure validation."""

    # Import quiz
    quiz, cards = quiz_workflow.create_and_import_quiz(basic_french_quiz)

    # Validate structure
    test_validators.validate_quiz_structure(quiz)

    # Validate content
    assert quiz.name == "French Basics"
    assert quiz.subject == "French"
    assert len(cards) == 4

    # Validate individual cards
    card_titles = [card.question_title for card in cards]
    expected_titles = ["hello", "goodbye", "thank you", "please"]

    for title in expected_titles:
        assert title in card_titles


def test_user_creation_and_personas(
    e2e_services,
    create_user_with_persona,
    user_personas
):
    """Test user creation with different personas."""

    # Test different persona types
    personas_to_test = ["beginner_student", "advanced_student", "teacher"]

    for persona_name in personas_to_test:
        user = create_user_with_persona(persona_name, f"test_{persona_name}")

        assert user.name == f"test_{persona_name}"
        assert hasattr(user, '_test_persona')
        assert user._test_persona["name"] == persona_name

        # Verify persona data
        persona_data = user_personas[persona_name]
        assert user._test_persona["skill_level"] == persona_data["skill_level"]


def test_mock_presenter_factory(mock_presenter_factory):
    """Test mock presenter factory functionality."""

    # Test normal behavior
    answers = ["answer1", "answer2", "answer3"]
    presenter = mock_presenter_factory(answers, behavior="normal")

    # Verify mock setup
    assert presenter.show_test_header is not None
    assert presenter.show_question is not None
    assert presenter.get_user_answer is not None

    # Test answer sequence
    for expected_answer in answers:
        actual_answer = presenter.get_user_answer()
        assert actual_answer == expected_answer

    # Test quit early behavior
    quit_presenter = mock_presenter_factory(["answer1", "answer2"], behavior="quit_early")
    first_answer = quit_presenter.get_user_answer()
    second_answer = quit_presenter.get_user_answer()

    assert first_answer == "answer1"
    assert second_answer == "quit"


def test_progress_analyzer(
    e2e_services,
    basic_french_quiz,
    quiz_workflow,
    create_user_with_persona,
    progress_analyzer,
    mock_presenter_factory
):
    # Create test sessions with improving scores
    test_sessions = [
        Mock(mode="test", score=60, started_at="2023-01-01"),
        Mock(mode="test", score=75, started_at="2023-01-02"),
        Mock(mode="test", score=90, started_at="2023-01-03")
    ]

    progress = progress_analyzer.analyze_progress(test_sessions)

    # Should show improvement: 90 - 60 = 30
    assert progress["improvement"] >= 0
    assert progress["improvement"] == 30
    assert progress["trend"] == "improving"


@pytest.mark.slow
def test_performance_baseline(
    e2e_services,
    basic_french_quiz,
    quiz_workflow,
    create_user_with_persona,
    mock_presenter_factory
):
    """Test basic performance baseline for E2E operations."""
    import time

    # Time quiz import
    start_time = time.time()
    quiz, cards = quiz_workflow.create_and_import_quiz(basic_french_quiz)
    import_time = time.time() - start_time

    assert import_time < 1.0  # Should import quickly

    # Time test session
    user = create_user_with_persona("advanced_student", "performance_user")
    presenter = mock_presenter_factory(["bonjour", "au revoir", "merci", "s'il vous plaît"])
    config = TestSessionConfig(audio_enabled=False)

    start_time = time.time()
    results = quiz_workflow.run_test_session(user, quiz, cards, presenter, config)
    session_time = time.time() - start_time

    assert session_time < 1.0  # Should complete quickly
    assert results["result"].value == "completed"
    assert results["score"] == 100


if __name__ == "__main__":
    # Run this specific test file
    pytest.main([__file__, "-v"])