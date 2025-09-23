from unittest.mock import Mock

import pytest


@pytest.fixture
def error_simulator():
    """Simulate various error conditions for testing error handling."""
    class ErrorSimulator:
        @staticmethod
        def create_failing_audio_service():
            """Create an audio service that fails."""
            failing_service = Mock()
            failing_service.is_available.return_value = False
            failing_service.play_text.side_effect = Exception("Audio failed")
            return failing_service

        @staticmethod
        def create_interrupted_presenter():
            """Create a presenter that simulates keyboard interrupt."""
            presenter = Mock()
            presenter.show_test_header = Mock()
            presenter.show_question = Mock(side_effect=KeyboardInterrupt())
            return presenter

        @staticmethod
        def create_slow_presenter(delay: float = 1.0):
            """Create a presenter with artificial delays."""
            import time

            def slow_method(*args, **kwargs):
                time.sleep(delay)
                return Mock()

            presenter = Mock()
            presenter.show_test_header = Mock(side_effect=slow_method)
            presenter.show_question = Mock(side_effect=slow_method)
            presenter.get_user_answer = Mock(return_value="answer")
            presenter.show_answer_result = Mock(side_effect=slow_method)
            presenter.wait_for_next = Mock(side_effect=slow_method)
            return presenter

    return ErrorSimulator()