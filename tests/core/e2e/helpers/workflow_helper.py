from typing import Dict, Any

import pytest

from core.learning.sessions.quiz_session import TestSession


@pytest.fixture
def quiz_workflow(e2e_services):
    """Helper for common quiz workflow operations."""
    class QuizWorkflow:
        def __init__(self, services):
            self.services = services

        def create_and_import_quiz(self, quiz_data: Dict[str, Any]):
            """Create and import a quiz, return quiz object and cards."""
            quiz_service = self.services["quiz_service"]
            quiz = quiz_service.import_quiz_from_dict(quiz_data)
            cards = quiz_service.get_quiz_flashcards(quiz.id)
            return quiz, cards

        def run_learning_session(self, user, quiz_id: int):
            """Run a learning session for a user."""
            user_service = self.services["user_service"]
            return user_service.create_session(user.id, quiz_id, "learn")

        def run_test_session(self, user, quiz, cards, presenter, config):
            """Run a complete test session and save results."""

            user_service = self.services["user_service"]
            audio_service = self.services["audio_service"]

            session = TestSession(cards, presenter, audio_service, config)
            result = session.start()
            score = session.get_final_score()

            # Save session
            db_session = user_service.create_session(user.id, quiz.id, "test", score)

            return {
                "result": result,
                "score": score,
                "session": session,
                "db_session": db_session,
                "detailed_results": session.get_detailed_results()
            }

    return QuizWorkflow(e2e_services)


@pytest.fixture
def progress_analyzer(e2e_services):
    """Helper for analyzing user progress and generating reports."""
    class ProgressAnalyzer:
        def __init__(self, services):
            self.services = services

        def get_user_progress(self, user):
            """Get comprehensive progress data for a user."""
            user_service = self.services["user_service"]
            sessions = user_service.get_user_sessions(user.id)

            learn_sessions = [s for s in sessions if s.mode == "learn"]
            test_sessions = [s for s in sessions if s.mode == "test"]

            return {
                "total_sessions": len(sessions),
                "learn_sessions": len(learn_sessions),
                "test_sessions": len(test_sessions),
                "test_scores": [s.score for s in test_sessions],
                "improvement": self._calculate_improvement(test_sessions),
                "recent_activity": sessions[:5]  # Most recent 5
            }

        @staticmethod
        def _calculate_improvement(test_sessions):
            """Calculate improvement between first and last test."""
            if len(test_sessions) < 2:
                return 0

            # Sessions are ordered newest first
            latest_score = test_sessions[0].score
            earliest_score = test_sessions[-1].score
            return latest_score - earliest_score

        def generate_class_report(self, users, quiz_id):
            """Generate class-wide performance report."""
            all_scores = []
            user_reports = []

            for user in users:
                progress = self.get_user_progress(user)
                user_test_scores = [
                    s.score for s in progress["recent_activity"]
                    if s.mode == "test" and s.quiz_id == quiz_id
                ]

                if user_test_scores:
                    best_score = max(user_test_scores)
                    all_scores.append(best_score)
                    user_reports.append({
                        "user": user.name,
                        "best_score": best_score,
                        "attempts": len(user_test_scores)
                    })

            return {
                "class_average": sum(all_scores) / len(all_scores) if all_scores else 0,
                "highest_score": max(all_scores) if all_scores else 0,
                "lowest_score": min(all_scores) if all_scores else 0,
                "total_students": len(users),
                "students_tested": len(user_reports),
                "user_reports": user_reports
            }

    return ProgressAnalyzer(e2e_services)

