"""
CLI entry point and Typer commands.

Provides command-line interface for quiz management.
"""
import typer
from sqlalchemy.orm import Session

from cli.cli_application import CLIApplication
from core.db import database
from core.db.crud import importers
from core.db.crud.repository.quiz_repository import QuizRepository

app = typer.Typer()


def get_db() -> Session:
    """Get database session."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.command()
def import_quiz(file: str):
    """Import a quiz from a JSON file into the database."""
    db = next(get_db())
    quiz = importers.import_quiz_from_file(db, file)
    typer.echo(f"Imported quiz: {quiz.name} (id={quiz.id})")


@app.command()
def list_quizzes():
    """List all available quizzes in the database."""
    db = next(get_db())
    quiz_repo = QuizRepository(db)
    quizzes = quiz_repo.get_all()
    for q in quizzes:
        typer.echo(f"[{q.id}] {q.name} ({q.subject or 'no subject'})")


def main():
    """Entry point for the CLI application."""
    cliApp = CLIApplication()
    cliApp.run()


if __name__ == "__main__":
    main()
