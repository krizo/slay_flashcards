from core.learning.sessions.answer_evaluator import TypedAnswerEvaluator
from core.learning.sessions.quiz_session import TestSessionConfig


def test_test_session_config_integration():
    """Test test session configuration integration."""
    # Test default configuration
    default_config = TestSessionConfig()
    assert default_config.audio_enabled == True
    assert default_config.question_lang == "en"
    assert default_config.answer_lang == "fr"
    assert default_config.strict_matching == False
    assert default_config.case_sensitive == False
    assert default_config.similarity_threshold == 0.8
    assert default_config.allow_partial_credit == True
    assert default_config.override_card_languages == True

    # Test custom configuration
    custom_config = TestSessionConfig(
        audio_enabled=False,
        question_lang="es",
        answer_lang="de",
        strict_matching=True,
        case_sensitive=True,
        similarity_threshold=0.9,
        allow_partial_credit=False,
        override_card_languages=False
    )

    assert custom_config.audio_enabled == False
    assert custom_config.question_lang == "es"
    assert custom_config.answer_lang == "de"
    assert custom_config.strict_matching == True
    assert custom_config.case_sensitive == True
    assert custom_config.similarity_threshold == 0.9
    assert custom_config.allow_partial_credit == False
    assert custom_config.override_card_languages == False


def test_language_configuration_integration():
    """Test language configuration affects evaluation."""

    # Case-sensitive configuration
    case_sensitive_config = TestSessionConfig(case_sensitive=True)
    case_sensitive_evaluator = TypedAnswerEvaluator(case_sensitive_config)

    # Case-insensitive configuration
    case_insensitive_config = TestSessionConfig(case_sensitive=False)
    case_insensitive_evaluator = TypedAnswerEvaluator(case_insensitive_config)

    # Test same input with different configurations
    user_answer = "Hello"
    correct_answer = "hello"

    # Case-sensitive should fail
    eval1, score1 = case_sensitive_evaluator.evaluate_answer(user_answer, correct_answer)
    assert eval1.value in ["incorrect", "partial"]  # Should not be exactly correct

    # Case-insensitive should pass
    eval2, score2 = case_insensitive_evaluator.evaluate_answer(user_answer, correct_answer)
    assert eval2.value == "correct"
    assert score2 == 1.0
