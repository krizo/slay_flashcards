import pytest


@pytest.fixture
def test_validators():
    """Validators for common test assertions."""
    class TestValidators:
        @staticmethod
        def validate_quiz_structure(quiz):
            """Validate quiz has correct structure."""
            assert hasattr(quiz, 'id')
            assert hasattr(quiz, 'name')
            assert hasattr(quiz, 'subject')
            assert quiz.name is not None

        @staticmethod
        def validate_user_session(session):
            """Validate session has correct structure."""
            assert hasattr(session, 'id')
            assert hasattr(session, 'user_id')
            assert hasattr(session, 'quiz_id')
            assert hasattr(session, 'mode')
            assert session.mode in ["learn", "test"]

        @staticmethod
        def validate_test_results(results):
            """Validate test results structure."""
            required_keys = ["total_questions", "correct", "incorrect", "final_score"]
            for key in required_keys:
                assert key in results

            assert 0 <= results["final_score"] <= 100
            assert results["total_questions"] > 0

        @staticmethod
        def validate_score_progression(scores, should_improve=True):
            """Validate that scores show expected progression."""
            assert len(scores) >= 2
            if should_improve:
                assert scores[-1] > scores[0], f"Expected improvement: {scores[0]} -> {scores[-1]}"

        @staticmethod
        def validate_performance_metrics(metrics, max_duration=5.0, max_memory_mb=100):
            """Validate performance is within acceptable limits."""
            assert "duration_seconds" in metrics
            assert "memory_delta_mb" in metrics

            assert metrics["duration_seconds"] <= max_duration, f"Operation took {metrics['duration_seconds']}s, expected <= {max_duration}s"
            assert abs(metrics["memory_delta_mb"]) <= max_memory_mb, f"Memory delta {metrics['memory_delta_mb']}MB, expected <= {max_memory_mb}MB"

    return TestValidators()