import typer
from sqlalchemy.orm import Session

from db import database
from services.quiz_service import QuizService
from services.user_service import UserService
from services.audio_service import GTTSAudioService, SilentAudioService
from learning.learning_session import LearningSession, LearningSessionConfig
from learning.flashcard_presenter import CLIFlashcardPresenter
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
            typer.echo(f"📝 Cards: {len(cards)}")
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
                typer.echo(f"\n\n⏹️  Learning session interrupted.")

            typer.echo(f"📊 Reviewed {learning_session.cards_reviewed} cards")

        finally:
            db.close()

    @staticmethod
    def test(quiz_id: int):
        """Run a test for a specific quiz (placeholder for future implementation)."""
        typer.echo(f"🧪 Test mode for quiz {quiz_id} - Coming soon!")

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


def main():
    """Entry point for the CLI application."""
    app = CLIApplication()
    app.run()

if __name__ == "__main__":
    main()