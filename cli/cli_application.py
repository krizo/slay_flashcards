import typer
from sqlalchemy.orm import Session

from db import database
from learning.presenters.flashcard_presenter import CLIFlashcardPresenter
from learning.presenters.test_presenter import CLITestPresenter
from learning.sessions.learning_session import LearningSessionConfig, LearningSession
from learning.sessions.test_session import TestSessionConfig, TestSession, AnswerEvaluator
from services.quiz_service import QuizService
from services.user_service import UserService
from services.audio_service import GTTSAudioService, SilentAudioService
from cli.progress_reporter import ProgressReporter


class CLIApplication:
    """Main CLI application class."""

    def __init__(self):
        self.app = typer.Typer()
        self._setup_commands()

    def _setup_commands(self):
        """Setup CLI commands."""
        self.app.command()(self.import_quiz)
        self.app.command()(self.list_quizzes)
        self.app.command()(self.learn)
        self.app.command()(self.test)
        self.app.command()(self.progress)
        self.app.command()(self.reset_db)

    @staticmethod
    def _get_db() -> Session:
        """Get database session."""
        return database.SessionLocal()

    def import_quiz(self, file: str):
        """Import a quiz from a JSON file into the database."""
        db = self._get_db()
        try:
            quiz_service = QuizService(db)
            quiz = quiz_service.import_quiz_from_file(file)
            typer.echo(f"✅ Imported quiz: {quiz.name} (id={quiz.id})")
        finally:
            db.close()

    def list_quizzes(self):
        """List all available quizzes in the database."""
        db = self._get_db()
        try:
            quiz_service = QuizService(db)
            quizzes = quiz_service.get_all_quizzes()

            if not quizzes:
                typer.echo("No quizzes found. Import some quizzes first!")
                return

            typer.echo("\n📚 Available Quizzes:")
            typer.echo("-" * 50)

            for quiz in quizzes:
                card_count = len(quiz.flashcards)
                subject_text = f" ({quiz.subject})" if quiz.subject else ""
                typer.echo(f"[{quiz.id}] {quiz.name}{subject_text} - {card_count} cards")
                if quiz.description:
                    typer.echo(f"    └─ {quiz.description}")
            typer.echo()
        finally:
            db.close()

    def learn(
            self,
            quiz_id: int,
            user: str = typer.Option("default", help="Username for tracking progress"),
            audio: bool = typer.Option(True, help="Enable audio playback"),
            lang_question: str = typer.Option("en", help="Language for question TTS"),
            lang_answer: str = typer.Option("fr", help="Language for answer TTS")
    ):
        """Start learning mode for a specific quiz."""
        db = self._get_db()
        try:
            quiz_service = QuizService(db)
            user_service = UserService(db)

            # Validate quiz
            quiz = quiz_service.get_quiz_by_id(quiz_id)
            if not quiz:
                typer.echo(f"❌ Quiz with id {quiz_id} not found!")
                return

            # Get flashcards
            cards = quiz_service.get_quiz_flashcards(quiz_id)
            if not cards:
                typer.echo(f"❌ No flashcards found for quiz '{quiz.name}'")
                return

            # Setup user
            current_user = user_service.ensure_user_exists(user)

            # Create session in database
            user_service.create_session(current_user.id, quiz_id, "learn")

            # Setup services
            audio_service = GTTSAudioService() if audio else SilentAudioService()
            presenter = CLIFlashcardPresenter()
            config = LearningSessionConfig(
                audio_enabled=audio,
                question_lang=lang_question,
                answer_lang=lang_answer
            )

            # Display session info
            typer.echo(f"\n🎓 Learning Mode: {quiz.name}")
            typer.echo(f"👤 User: {current_user.name}")
            typer.echo(f"📄 Cards: {len(cards)}")
            typer.echo(f"🔊 Audio: {'Enabled' if audio and audio_service.is_available() else 'Disabled'}")
            typer.echo("-" * 50)

            # Start learning session
            learning_session = LearningSession(cards, presenter, audio_service, config)
            result = learning_session.start()

            # Show results
            if result.value == "completed":
                typer.echo(f"\n🎉 Learning session completed!")
            elif result.value == "quit_early":
                typer.echo(f"\n📚 Learning session ended early.")
            elif result.value == "interrupted":
                typer.echo(f"\n\nℹ️  Learning session interrupted.")

            typer.echo(f"📊 Reviewed {learning_session.cards_reviewed} cards")

        finally:
            db.close()

    def test(
            self,
            quiz_id: int,
            user: str = typer.Option("default", help="Username for tracking progress"),
            audio: bool = typer.Option(True, help="Enable audio playback"),
            lang_question: str = typer.Option("en", help="Language for question TTS"),
            lang_answer: str = typer.Option("fr", help="Language for answer TTS"),
            strict: bool = typer.Option(False, help="Enable strict answer matching"),
            case_sensitive: bool = typer.Option(False, help="Enable case-sensitive matching"),
            similarity_threshold: float = typer.Option(0.8, help="Similarity threshold for partial credit (0.0-1.0)")
    ):
        """Run a test for a specific quiz."""
        db = self._get_db()
        try:
            quiz_service = QuizService(db)
            user_service = UserService(db)

            # Validate quiz
            quiz = quiz_service.get_quiz_by_id(quiz_id)
            if not quiz:
                typer.echo(f"❌ Quiz with id {quiz_id} not found!")
                return

            # Get flashcards
            cards = quiz_service.get_quiz_flashcards(quiz_id)
            if not cards:
                typer.echo(f"❌ No flashcards found for quiz '{quiz.name}'")
                return

            # Setup user
            current_user = user_service.ensure_user_exists(user)

            # Setup services
            audio_service = GTTSAudioService() if audio else SilentAudioService()
            presenter = CLITestPresenter()
            config = TestSessionConfig(
                audio_enabled=audio,
                question_lang=lang_question,
                answer_lang=lang_answer,
                strict_matching=strict,
                case_sensitive=case_sensitive,
                similarity_threshold=max(0.0, min(1.0, similarity_threshold))  # Clamp to 0-1
            )

            # Display session info
            typer.echo(f"\n🧪 Test Mode: {quiz.name}")
            typer.echo(f"👤 User: {current_user.name}")
            typer.echo(f"📝 Questions: {len(cards)}")
            typer.echo(f"🔊 Audio: {'Enabled' if audio and audio_service.is_available() else 'Disabled'}")
            typer.echo(f"⚖️  Matching: {'Strict' if strict else 'Flexible'}")
            if not strict:
                typer.echo(f"🎯 Similarity threshold: {similarity_threshold:.0%}")
            typer.echo("-" * 50)

            # Start test session
            test_session = TestSession(cards, presenter, audio_service, config)
            result = test_session.start()

            # Calculate final score
            final_score = test_session.get_final_score()

            # Create session in database with score
            user_service.create_session(current_user.id, quiz_id, "test", final_score)

            # Show results based on completion
            if result.value == "completed":
                typer.echo(f"\n🎯 Test completed!")
            elif result.value == "quit_early":
                typer.echo(f"\n📊 Test ended early.")
            elif result.value == "interrupted":
                typer.echo(f"\n\nℹ️  Test interrupted.")

            # Show detailed results
            detailed_results = test_session.get_detailed_results()
            presenter.show_final_results(detailed_results)

        except ValueError as e:
            typer.echo(f"❌ Error: {e}")
        finally:
            db.close()

    def progress(self, user: str = typer.Option("default", help="Username to show progress for")):
        """Show learning progress for a user."""
        db = self._get_db()
        try:
            user_service = UserService(db)

            current_user = user_service.get_user_by_name(user)
            if not current_user:
                typer.echo(f"❌ User '{user}' not found!")
                return

            user_sessions = user_service.get_user_sessions(current_user.id)

            if not user_sessions:
                typer.echo(f"📊 No learning sessions found for user '{user}'")
                return

            reporter = ProgressReporter(current_user, user_sessions)
            reporter.print_report()

        finally:
            db.close()

    @staticmethod
    def reset_db():
        """Reset the database (WARNING: This will delete all data!)."""
        confirm = typer.confirm("Are you sure you want to reset the database? This will delete all data!")
        if confirm:
            from db.database import reset_database
            reset_database()
            typer.echo("🗑️  Database reset completed!")
        else:
            typer.echo("❌ Database reset cancelled.")

    def run(self):
        """Run the CLI application."""
        # Create tables if they don't exist
        database.Base.metadata.create_all(bind=database.engine)
        self.app()


# Helper command for testing specific features
def test_answer_evaluation():
    """Test the answer evaluation system with sample data."""
    from learning.sessions.test_session import TestSessionConfig, AnswerEvaluator

    config = TestSessionConfig(
        strict_matching=False,
        case_sensitive=False,
        similarity_threshold=0.8
    )
    evaluator = AnswerEvaluator(config)

    test_cases = [
        ("chien", "chien"),      # Exact match
        ("Chien", "chien"),      # Case difference
        ("chien.", "chien"),     # Punctuation
        ("le chien", "chien"),   # Extra words
        ("chat", "chien"),       # Wrong answer
        ("chein", "chien"),      # Typo
        ("", "chien"),           # Empty answer
    ]

    print("\n🧪 Answer Evaluation Test:")
    print("-" * 40)

    for user_answer, correct_answer in test_cases:
        evaluation, score = evaluator.evaluate_answer(user_answer, correct_answer)
        status = "✅" if evaluation.value == "correct" else "⚠️" if evaluation.value == "partial" else "❌"
        print(f"{status} '{user_answer}' → '{correct_answer}' | {evaluation.value} ({score:.0%})")

    print()


if __name__ == "__main__":
    app = CLIApplication()
    app.run()