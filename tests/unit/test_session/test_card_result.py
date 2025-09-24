from learning.sessions.quiz_session import CardResult, AnswerEvaluation


def test_card_result_creation(mock_flashcard):
    """Test creating a CardResult."""
    result = CardResult(mock_flashcard, "chien", AnswerEvaluation.CORRECT, 1.0)

    assert result.card == mock_flashcard
    assert result.user_answer == "chien"
    assert result.correct_answer == "chien"
    assert result.evaluation == AnswerEvaluation.CORRECT
    assert result.score == 1.0


def test_card_result_whitespace_trimming(mock_flashcard):
    """Test that user answers are trimmed."""
    result = CardResult(mock_flashcard, "  chien  ", AnswerEvaluation.CORRECT, 1.0)

    assert result.user_answer == "chien"


def test_card_result_different_evaluations(mock_flashcard):
    """Test different evaluation types."""
    # Correct
    correct_result = CardResult(mock_flashcard, "chien", AnswerEvaluation.CORRECT, 1.0)
    assert correct_result.evaluation == AnswerEvaluation.CORRECT
    assert correct_result.score == 1.0

    # Partial
    partial_result = CardResult(mock_flashcard, "chein", AnswerEvaluation.PARTIAL, 0.8)
    assert partial_result.evaluation == AnswerEvaluation.PARTIAL
    assert partial_result.score == 0.8

    # Incorrect
    incorrect_result = CardResult(mock_flashcard, "cat", AnswerEvaluation.INCORRECT, 0.0)
    assert incorrect_result.evaluation == AnswerEvaluation.INCORRECT
    assert incorrect_result.score == 0.0

