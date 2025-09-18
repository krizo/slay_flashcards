from sqlalchemy.orm import Session
from typing import Dict, Any, Type, List

from db import models
from db.models import Flashcard


def get_flashcards_for_quiz(db: Session, quiz_id: int) -> list[Type[Flashcard]]:
    return db.query(models.Flashcard).filter_by(quiz_id=quiz_id).all()


def create_flashcard(db: Session, quiz_id: int, question: Dict[str, Any], answer: Dict[str, Any]) -> models.Flashcard:
    fc = models.Flashcard(
        quiz_id=quiz_id,
        question_title=question["title"],
        question_text=question["text"],
        question_lang=question.get("lang"),
        question_difficulty=question.get("difficulty"),
        question_emoji=question.get("emoji"),
        question_image=question.get("image"),
        answer_text=answer["text"],
        answer_lang=answer.get("lang"),
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
    """Insert many flashcards in one transaction."""
    objs: List[models.Flashcard] = []
    for c in cards:
        q = c.get("question", {})
        a = c.get("answer", {})
        objs.append(
            models.Flashcard(
                quiz_id=quiz_id,
                question_title=q["title"],
                question_text=q["text"],
                question_lang=q.get("lang"),
                question_difficulty=q.get("difficulty"),
                question_emoji=q.get("emoji"),
                question_image=q.get("image"),
                answer_text=a["text"],
                answer_lang=a.get("lang"),
            )
        )
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs
