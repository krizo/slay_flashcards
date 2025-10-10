"""
Quiz importer module for loading quizzes from JSON files.

Provides utilities to import quiz definitions into the database.
"""

import json
from datetime import datetime

from sqlalchemy.orm import Session  # pylint: disable=import-error

from core.db import models
from core.db.crud.repository.flashcard_repository import FlashcardRepository
from core.db.crud.repository.quiz_repository import QuizRepository


def import_quiz_from_file(db: Session, file_path: str, user_id: int) -> models.Quiz:
    """
    Load a quiz definition from a JSON file and insert it into DB.

    Args:
        db: SQLAlchemy database session
        file_path: Path to JSON file
        user_id: ID of the user who will own this quiz

    Returns:
        Imported quiz instance
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return import_quiz_from_dict(db, data, user_id)


def import_quiz_from_dict(db: Session, data: dict, user_id: int) -> models.Quiz:
    """
    Import a quiz from a dict matching the JSON schema.

    Args:
        db: SQLAlchemy database session
        data: Quiz data dictionary
        user_id: ID of the user who will own this quiz

    Returns:
        Imported quiz instance
    """
    quiz_meta = data["quiz"]

    quiz_repo = QuizRepository(db)
    flashcard_repo = FlashcardRepository(db)

    quiz = quiz_repo.create_quiz(
        name=quiz_meta["name"],
        user_id=user_id,
        subject=quiz_meta.get("subject"),
        category=quiz_meta.get("category"),
        level=quiz_meta.get("level"),
        description=quiz_meta.get("description"),
        created_at=datetime.fromisoformat(quiz_meta["created_at"]) if quiz_meta.get("created_at") else None,
    )

    flashcard_repo.bulk_create_flashcards(quiz.id, data.get("flashcards", []))
    return quiz
