"""
Flashcard repository for managing flashcard entities and related operations.

Provides flashcard-specific queries, validation, and answer type support.
"""

from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import and_, func, select  # pylint: disable=import-error
from sqlalchemy.orm import Session  # pylint: disable=import-error

from core.db import models
from core.db.crud.repository import BaseRepository


class FlashcardRepository(BaseRepository[models.Flashcard]):
    """
    Repository for Flashcard database operations.

    Provides methods for:
    - Flashcard creation with enhanced answer type support
    - Bulk operations
    - Quiz-specific queries
    - Answer type management and statistics
    """

    def __init__(self, db: Session):
        """
        Initialize flashcard repository.

        Args:
            db: SQLAlchemy database session
        """
        super().__init__(db, models.Flashcard)

    # =========================================================================
    # FLASHCARD RETRIEVAL METHODS
    # =========================================================================

    def get_by_quiz_id(self, quiz_id: int) -> Sequence[models.Flashcard]:
        """
        Get all flashcards for a specific quiz.

        Args:
            quiz_id: Quiz ID to retrieve flashcards for

        Returns:
            List of flashcards
        """
        return self._execute_query(select(models.Flashcard).where(models.Flashcard.quiz_id == quiz_id))

    def get_by_difficulty(self, quiz_id: int, difficulty: int) -> Sequence[models.Flashcard]:
        """
        Get flashcards by difficulty level.

        Args:
            quiz_id: Quiz ID
            difficulty: Difficulty level (1-5)

        Returns:
            List of flashcards matching difficulty
        """
        return self._execute_query(
            select(models.Flashcard).where(
                and_(models.Flashcard.quiz_id == quiz_id, models.Flashcard.question_difficulty == difficulty)
            )
        )

    def get_by_answer_type(self, quiz_id: int, answer_type: str) -> Sequence[models.Flashcard]:
        """
        Get flashcards filtered by answer type.

        Args:
            quiz_id: Quiz ID
            answer_type: Answer type (text, integer, float, range, etc.)

        Returns:
            List of flashcards with specified answer type
        """
        return self._execute_query(
            select(models.Flashcard).where(
                and_(models.Flashcard.quiz_id == quiz_id, models.Flashcard.answer_type == answer_type)
            )
        )

    def search_by_question_text(self, quiz_id: int, text: str) -> Sequence[models.Flashcard]:
        """
        Search flashcards by question text (case-insensitive).

        Args:
            quiz_id: Quiz ID
            text: Search text

        Returns:
            List of matching flashcards
        """
        return self._execute_query(
            select(models.Flashcard).where(
                and_(models.Flashcard.quiz_id == quiz_id, models.Flashcard.question_text.ilike(f"%{text}%"))
            )
        )

    # =========================================================================
    # FLASHCARD CREATION WITH ANSWER TYPE SUPPORT
    # =========================================================================

    def create_flashcard(self, quiz_id: int, question: Dict[str, Any], answer: Dict[str, Any]) -> models.Flashcard:
        """
        Create a single flashcard with enhanced answer type support.

        Args:
            quiz_id: Quiz ID
            question: Question dictionary with title, text, lang, difficulty, emoji, image
            answer: Answer dictionary with text, lang, type, options, metadata

        Returns:
            Created flashcard instance
        """
        # Extract and validate answer type
        answer_type = answer.get("type", "text")
        answer_options = answer.get("options")
        answer_metadata = answer.get("metadata", {}) or {}

        # Set default tolerances for numeric types
        if answer_type == "integer" and "tolerance" not in answer_metadata:
            answer_metadata["tolerance"] = 0
        elif answer_type == "float" and "tolerance" not in answer_metadata:
            answer_metadata["tolerance"] = 0.01
        elif answer_type == "range" and "overlap_threshold" not in answer_metadata:
            answer_metadata["overlap_threshold"] = 0.5

        # Validate answer type
        answer_type = self._validate_answer_type(answer_type)

        return self.create(
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
            answer_metadata=answer_metadata,
        )

    def bulk_create_flashcards(self, quiz_id: int, cards: List[Dict[str, Any]]) -> List[models.Flashcard]:
        """
        Create multiple flashcards with enhanced answer type support.

        Args:
            quiz_id: Quiz ID
            cards: List of card dictionaries with question and answer

        Returns:
            List of created flashcard instances
        """
        card_data = []
        for card in cards:
            q = card.get("question", {})
            a = card.get("answer", {})

            # Extract and validate answer type
            answer_type = a.get("type", "text")
            answer_options = a.get("options")
            answer_metadata = a.get("metadata", {}) or {}

            # Set default tolerances for numeric types
            if answer_type == "integer" and "tolerance" not in answer_metadata:
                answer_metadata["tolerance"] = 0
            elif answer_type == "float" and "tolerance" not in answer_metadata:
                answer_metadata["tolerance"] = 0.01
            elif answer_type == "range" and "overlap_threshold" not in answer_metadata:
                answer_metadata["overlap_threshold"] = 0.5

            # Validate answer type
            answer_type = self._validate_answer_type(answer_type)

            card_data.append(
                {
                    "quiz_id": quiz_id,
                    # Question fields
                    "question_title": q["title"],
                    "question_text": q["text"],
                    "question_lang": q.get("lang"),
                    "question_difficulty": q.get("difficulty"),
                    "question_emoji": q.get("emoji"),
                    "question_image": q.get("image"),
                    # Answer fields with type support
                    "answer_text": a["text"],
                    "answer_lang": a.get("lang"),
                    "answer_type": answer_type,
                    "answer_options": answer_options,
                    "answer_metadata": answer_metadata,
                }
            )

        return self.bulk_create(card_data)

    # =========================================================================
    # ANSWER TYPE MANAGEMENT
    # =========================================================================

    def update_answer_type(
        self,
        flashcard_id: int,
        answer_type: str,
        answer_options: Optional[List[Dict[str, Any]]] = None,
        answer_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[models.Flashcard]:
        """
        Update the answer type and related fields of an existing flashcard.

        Args:
            flashcard_id: Flashcard ID
            answer_type: New answer type
            answer_options: Optional answer options
            answer_metadata: Optional answer metadata

        Returns:
            Updated flashcard or None if not found

        Raises:
            ValueError: If answer type is invalid
        """
        flashcard = self.get_by_id(flashcard_id)
        if not flashcard:
            return None

        # Validate answer type (raises ValueError if invalid)
        validated_type = self._validate_answer_type(answer_type, raise_on_invalid=True)

        return self.update(
            flashcard, answer_type=validated_type, answer_options=answer_options, answer_metadata=answer_metadata or {}
        )

    def get_answer_type_statistics(self, quiz_id: int) -> Dict[str, int]:
        """
        Get statistics about answer types in a quiz.

        Args:
            quiz_id: Quiz ID

        Returns:
            Dictionary mapping answer type to count
        """
        results = self.db.execute(
            select(models.Flashcard.answer_type, func.count(models.Flashcard.id)) # pylint: disable=not-callable
            .where(models.Flashcard.quiz_id == quiz_id)
            .group_by(models.Flashcard.answer_type)
        ).all()

        return {answer_type or "text": count for answer_type, count in results}

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _validate_answer_type(self, answer_type: str, raise_on_invalid: bool = False) -> str:
        """
        Validate answer type against allowed types.

        Args:
            answer_type: Answer type to validate
            raise_on_invalid: If True, raise ValueError on invalid type

        Returns:
            Validated answer type (defaults to 'text' if invalid and not raising)

        Raises:
            ValueError: If answer type is invalid and raise_on_invalid=True
        """
        valid_types = ["text", "integer", "float", "range", "boolean", "choice", "multiple_choice", "short_text"]

        if answer_type not in valid_types:
            if raise_on_invalid:
                raise ValueError(f"Invalid answer type: {answer_type}. Must be one of {valid_types}")
            return "text"

        return answer_type
