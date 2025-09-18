import json
from sqlalchemy.orm import Session
from datetime import datetime

from db import models
from db.crud import quizzes, flashcards


def import_quiz_from_file(db: Session, file_path: str) -> models.Quiz:
    """Load a quiz definition from a JSON file and insert it into DB."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return import_quiz_from_dict(db, data)


def import_quiz_from_dict(db: Session, data: dict) -> models.Quiz:
    """Import a quiz from a dict matching the JSON schema."""
    quiz_meta = data["quiz"]

    quiz = quizzes.create_quiz(
        db,
        name=quiz_meta["name"],
        subject=quiz_meta.get("subject"),
        description=quiz_meta.get("description"),
        created_at=datetime.fromisoformat(quiz_meta["created_at"])
        if quiz_meta.get("created_at")
        else None,
    )

    flashcards.bulk_create_flashcards(db, quiz.id, data.get("flashcards", []))
    return quiz
