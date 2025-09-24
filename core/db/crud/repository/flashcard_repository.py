from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from core.db import models
from core.db.crud.repository import BaseRepository


class FlashcardRepository(BaseRepository[models.Flashcard]):
    """Repository for Flashcard operations."""

    def __init__(self, db: Session):
        super().__init__(db, models.Flashcard)

    def get_by_quiz_id(self, quiz_id: int) -> List[models.Flashcard]:
        """Get all flashcards for a specific quiz."""
        return self.db.execute(
            select(models.Flashcard).where(models.Flashcard.quiz_id == quiz_id)
        ).scalars().all()

    def create_flashcard(
            self,
            quiz_id: int,
            question: Dict[str, Any],
            answer: Dict[str, Any]
    ) -> models.Flashcard:
        """Create a single flashcard."""
        return self.create(
            quiz_id=quiz_id,
            question_title=question["title"],
            question_text=question["text"],
            question_lang=question.get("lang"),
            question_difficulty=question.get("difficulty"),
            question_emoji=question.get("emoji"),
            question_image=question.get("image"),
            answer_text=answer["text"],
            answer_lang=answer.get("lang")
        )

    def bulk_create_flashcards(
            self,
            quiz_id: int,
            cards: List[Dict[str, Any]]
    ) -> List[models.Flashcard]:
        """Create multiple flashcards for a quiz."""
        card_data = []
        for card in cards:
            q = card.get("question", {})
            a = card.get("answer", {})
            card_data.append({
                "quiz_id": quiz_id,
                "question_title": q["title"],
                "question_text": q["text"],
                "question_lang": q.get("lang"),
                "question_difficulty": q.get("difficulty"),
                "question_emoji": q.get("emoji"),
                "question_image": q.get("image"),
                "answer_text": a["text"],
                "answer_lang": a.get("lang")
            })
        return self.bulk_create(card_data)

    def get_by_difficulty(self, quiz_id: int, difficulty: int) -> List[models.Flashcard]:
        """Get flashcards by difficulty level."""
        return self.db.execute(
            select(models.Flashcard).where(
                models.Flashcard.quiz_id == quiz_id,
                models.Flashcard.question_difficulty == difficulty
            )
        ).scalars().all()

    def search_by_question_text(self, quiz_id: int, text: str) -> List[models.Flashcard]:
        """Search flashcards by question text."""
        return self.db.execute(
            select(models.Flashcard).where(
                models.Flashcard.quiz_id == quiz_id,
                models.Flashcard.question_text.ilike(f"%{text}%")
            )
        ).scalars().all()
