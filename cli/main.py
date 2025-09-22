import typer
from sqlalchemy.orm import Session

from cli.cli_application import CLIApplication
from db import database
from db.crud import quizzes
from db.crud import importers

app = typer.Typer()


def get_db() -> Session:
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
    qs = quizzes.get_quizzes(db)
    for q in qs:
        typer.echo(f"[{q.id}] {q.name} ({q.subject or 'no subject'})")


def main():
    """Entry point for the CLI application."""
    app = CLIApplication()
    app.run()


if __name__ == "__main__":
    main()
