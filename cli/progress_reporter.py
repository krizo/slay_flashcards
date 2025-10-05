from typing import List

from core.db import models


class ProgressReporter:
    """Handles progress reporting and statistics."""

    def __init__(self, user: models.User, sessions: List[models.Session]):
        self.user = user
        self.sessions = sessions

    def generate_report(self) -> dict:
        """Generate progress statistics."""
        if not self.sessions:
            return {
                "total_sessions": 0,
                "learn_sessions": 0,
                "test_sessions": 0,
                "average_score": None,
                "recent_activity": []
            }

        learn_sessions = [s for s in self.sessions if s.mode == "learn"]
        test_sessions = [s for s in self.sessions if s.mode == "test"]

        # Calculate average test score
        test_scores = [s.score for s in test_sessions if s.score is not None]
        avg_score = sum(test_scores) / len(test_scores) if test_scores else None

        # Get recent activity
        recent = sorted(self.sessions, key=lambda x: x.started_at, reverse=True)[:5]

        return {
            "total_sessions": len(self.sessions),
            "learn_sessions": len(learn_sessions),
            "test_sessions": len(test_sessions),
            "average_score": avg_score,
            "recent_activity": recent
        }

    def print_report(self) -> None:
        """Print formatted progress report to console."""
        report = self.generate_report()

        print(f"\n📊 Progress Report for {self.user.name}")
        print("-" * 50)
        print(f"Total sessions: {report['total_sessions']}")
        print(f"Learning sessions: {report['learn_sessions']}")
        print(f"Test sessions: {report['test_sessions']}")

        if report['average_score'] is not None:
            print(f"Average test score: {report['average_score']:.1f}%")

        if report['recent_activity']:
            print("\n🕒 Recent Activity:")
            for session in report['recent_activity']:
                quiz_name = session.quiz.name
                mode_emoji = "🎓" if session.mode == "learn" else "🧪"
                score_text = f" ({session.score}%)" if session.score else ""
                date_str = session.started_at.strftime('%Y-%m-%d %H:%M')
                print(f"  {mode_emoji} {quiz_name}{score_text} - {date_str}")
