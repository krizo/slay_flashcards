from unittest.mock import Mock

from db import models
from learning.presenters.test_presenter import CLITestPresenter
from learning.sessions.test_session import CardResult, AnswerEvaluation


def test_cli_presenter_show_test_header(capsys):
    """Test test header display."""
    presenter = CLITestPresenter()
    presenter.show_test_header(5)

    captured = capsys.readouterr()
    assert "🧪 Test Mode Started" in captured.out
    assert "📝 5 questions to answer" in captured.out
    assert "💡 Type 'quit' to exit early" in captured.out


def test_cli_presenter_show_question(capsys, mock_flashcard):
    """Test question display."""
    presenter = CLITestPresenter()
    presenter.show_question(mock_flashcard, 1, 3)

    captured = capsys.readouterr()
    assert "📋 Question 1/3" in captured.out
    assert "❓ dog" in captured.out
    assert "🐶" in captured.out


def test_cli_presenter_show_question_no_emoji(capsys):
    """Test question display without emoji."""
    card = Mock(spec=models.Flashcard)
    card.question_title = "test"
    card.question_text = "test question"
    card.question_emoji = None

    presenter = CLITestPresenter()
    presenter.show_question(card, 1, 1)

    captured = capsys.readouterr()
    assert "❓ test" in captured.out
    assert "test question" in captured.out


def test_cli_presenter_show_answer_result_correct(capsys, mock_flashcard):
    """Test showing correct answer result."""
    result = CardResult(mock_flashcard, "chien", AnswerEvaluation.CORRECT, 1.0)

    presenter = CLITestPresenter()
    presenter.show_answer_result(result)

    captured = capsys.readouterr()
    assert "✅ Correct!" in captured.out
    assert "100%" in captured.out


def test_cli_presenter_show_answer_result_partial(capsys, mock_flashcard):
    """Test showing partial answer result."""
    result = CardResult(mock_flashcard, "chein", AnswerEvaluation.PARTIAL, 0.8)

    presenter = CLITestPresenter()
    presenter.show_answer_result(result)

    captured = capsys.readouterr()
    assert "⚠️  Partially correct" in captured.out
    assert "80%" in captured.out
    assert "Your answer: chein" in captured.out
    assert "Correct answer: chien" in captured.out


def test_cli_presenter_show_answer_result_incorrect(capsys, mock_flashcard):
    """Test showing incorrect answer result."""
    result = CardResult(mock_flashcard, "cat", AnswerEvaluation.INCORRECT, 0.0)

    presenter = CLITestPresenter()
    presenter.show_answer_result(result)

    captured = capsys.readouterr()
    assert "❌ Incorrect" in captured.out
    assert "0%" in captured.out
    assert "Your answer: cat" in captured.out
    assert "Correct answer: chien" in captured.out


def test_cli_presenter_show_final_results_excellent(capsys):
    """Test showing final results for excellent performance."""
    results = {
        "total_questions": 10,
        "correct": 9,
        "partial": 1,
        "incorrect": 0,
        "final_score": 95,
        "breakdown": []
    }

    presenter = CLITestPresenter()
    presenter.show_final_results(results)

    captured = capsys.readouterr()
    assert "🎯 TEST COMPLETED!" in captured.out
    assert "📊 Final Score: 95%" in captured.out
    assert "📝 Total Questions: 10" in captured.out
    assert "✅ Correct: 9" in captured.out
    assert "⚠️  Partially Correct: 1" in captured.out
    assert "🌟 Excellent work!" in captured.out


def test_cli_presenter_show_final_results_poor(capsys):
    """Test showing final results for poor performance."""
    results = {
        "total_questions": 10,
        "correct": 3,
        "partial": 1,
        "incorrect": 6,
        "final_score": 35,
        "breakdown": []
    }

    presenter = CLITestPresenter()
    presenter.show_final_results(results)

    captured = capsys.readouterr()
    assert "📊 Final Score: 35%" in captured.out
    assert "💪 Don't give up! Review and try again!" in captured.out


def test_cli_presenter_show_final_results_with_breakdown(capsys):
    """Test showing final results with detailed breakdown."""
    results = {
        "total_questions": 3,
        "correct": 2,
        "partial": 0,
        "incorrect": 1,
        "final_score": 67,
        "breakdown": [
            {"question": "dog", "evaluation": "correct", "score": 1.0},
            {"question": "cat", "evaluation": "correct", "score": 1.0},
            {"question": "house", "evaluation": "incorrect", "score": 0.0},
        ]
    }

    presenter = CLITestPresenter()
    presenter.show_final_results(results)

    captured = capsys.readouterr()
    assert "📋 Detailed Results:" in captured.out
    assert "1. ✅ dog (100%)" in captured.out
    assert "2. ✅ cat (100%)" in captured.out
    assert "3. ❌ house (0%)" in captured.out


def test_cli_presenter_performance_feedback_ranges(capsys):
    """Test different performance feedback ranges."""
    test_cases = [
        (95, "🌟 Excellent work!"),
        (85, "👍 Great job!"),
        (75, "👌 Good effort!"),
        (65, "📚 Keep practicing!"),
        (45, "💪 Don't give up! Review and try again!"),
    ]

    for score, expected_feedback in test_cases:
        results = {
            "total_questions": 10,
            "correct": score // 10,
            "partial": 0,
            "incorrect": 10 - (score // 10),
            "final_score": score,
            "breakdown": []
        }

        presenter = CLITestPresenter()
        presenter.show_final_results(results)

        captured = capsys.readouterr()
        assert expected_feedback in captured.out
