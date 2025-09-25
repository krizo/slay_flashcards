from sqlalchemy.orm import Session
from typing import Dict, Any, Type, List, Optional

from core.db import models
from core.db.models import Flashcard


def get_flashcards_for_quiz(db: Session, quiz_id: int) -> list[Type[Flashcard]]:
    return db.query(models.Flashcard).filter_by(quiz_id=quiz_id).all()


def create_flashcard(
    db: Session,
    quiz_id: int,
    question: Dict[str, Any],
    answer: Dict[str, Any]
) -> models.Flashcard:
    """Create a flashcard with enhanced answer type support."""

    # Extract answer type and related fields
    answer_type = answer.get("type", "text")
    answer_options = answer.get("options")
    answer_metadata = answer.get("metadata", {}) or {}

    if answer_type == "integer" and "tolerance" not in answer_metadata:
        answer_metadata["tolerance"] = 0
    elif answer_type == "float" and "tolerance" not in answer_metadata:
        answer_metadata["tolerance"] = 0.01
    elif answer_type == "range" and "overlap_threshold" not in answer_metadata:
        answer_metadata["overlap_threshold"] = 0.5

    # Validate answer type
    valid_types = ["text", "integer", "float", "range", "boolean", "choice", "multiple_choice", "short_text"]
    if answer_type not in valid_types:
        answer_type = "text"

    fc = models.Flashcard(
        quiz_id=quiz_id,
        # Question fields
        question_title=question["title"],
        question_text=question["text"],
        question_lang=question.get("lang"),
        question_difficulty=question.get("difficulty"),
        question_emoji=question.get("emoji"),
        question_image=question.get("image"),
        # Answer fields with type support
        answer_text=answer["text"],
        answer_lang=answer.get("lang"),
        answer_type=answer_type,
        answer_options=answer_options,
        answer_metadata=answer_metadata,  # FIXED: Ensure this is stored as dict
    )
    db.add(fc)
    db.commit()
    db.refresh(fc)
    return fc


def bulk_create_flashcards(
        db: Session,
        quiz_id: int,
        cards: List[Dict[str, Any]],
) -> List[models.Flashcard]:
    """Insert many flashcards with enhanced answer type support."""
    objs: List[models.Flashcard] = []
    for c in cards:
        q = c.get("question", {})
        a = c.get("answer", {})

        # Extract answer type and related fields
        answer_type = a.get("type", "text")
        answer_options = a.get("options")
        answer_metadata = a.get("metadata", {})

        # Validate answer type
        valid_types = ["text", "integer", "float", "range", "boolean", "choice", "multiple_choice", "short_text"]
        if answer_type not in valid_types:
            answer_type = "text"

        objs.append(
            models.Flashcard(
                quiz_id=quiz_id,
                # Question fields
                question_title=q["title"],
                question_text=q["text"],
                question_lang=q.get("lang"),
                question_difficulty=q.get("difficulty"),
                question_emoji=q.get("emoji"),
                question_image=q.get("image"),
                # Answer fields with type support
                answer_text=a["text"],
                answer_lang=a.get("lang"),
                answer_type=answer_type,
                answer_options=answer_options,
                answer_metadata=answer_metadata,
            )
        )
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs


def update_flashcard_answer_type(
        db: Session,
        flashcard_id: int,
        answer_type: str,
        answer_options: Optional[List[Dict[str, Any]]] = None,
        answer_metadata: Optional[Dict[str, Any]] = None
) -> Optional[models.Flashcard]:
    """Update the answer type and related fields of an existing flashcard."""

    flashcard = db.get(models.Flashcard, flashcard_id)
    if not flashcard:
        return None

    # Validate answer type
    valid_types = ["text", "integer", "float", "range", "boolean", "choice", "multiple_choice", "short_text"]
    if answer_type not in valid_types:
        raise ValueError(f"Invalid answer type: {answer_type}")

    flashcard.answer_type = answer_type
    flashcard.answer_options = answer_options
    flashcard.answer_metadata = answer_metadata or {}

    db.commit()
    db.refresh(flashcard)
    return flashcard


def get_flashcards_by_answer_type(db: Session, quiz_id: int, answer_type: str) -> List[models.Flashcard]:
    """Get flashcards filtered by answer type."""
    return db.query(models.Flashcard).filter(
        models.Flashcard.quiz_id == quiz_id,
        models.Flashcard.answer_type == answer_type
    ).all()


def get_answer_type_statistics(db: Session, quiz_id: int) -> Dict[str, int]:
    """Get statistics about answer types in a quiz."""
    from sqlalchemy import func

    results = db.query(
        models.Flashcard.answer_type,
        func.count(models.Flashcard.id)
    ).filter(
        models.Flashcard.quiz_id == quiz_id
    ).group_by(
        models.Flashcard.answer_type
    ).all()

    return {answer_type or "text": count for answer_type, count in results}
