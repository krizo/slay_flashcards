"""
Quiz service for business logic related to quizzes and flashcards.

Provides high-level operations that combine repository calls.
"""

from collections import Counter
from typing import Any, Dict, Optional, Sequence

from sqlalchemy.orm import Session  # pylint: disable=import-error

from core.db import models
from core.db.crud import importers
from core.db.crud.repository.flashcard_repository import FlashcardRepository
from core.db.crud.repository.quiz_repository import QuizRepository


class QuizService:
    """
    Service for managing quizzes and flashcards.

    Provides high-level business logic operations using repositories.
    """

    def __init__(self, db: Session):
        """
        Initialize quiz service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.quiz_repo = QuizRepository(db)
        self.flashcard_repo = FlashcardRepository(db)

    # =========================================================================
    # QUIZ OPERATIONS
    # =========================================================================

    def get_all_quizzes(self, user_id: Optional[int] = None) -> Sequence[models.Quiz]:
        """
        Get all available quizzes, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter quizzes by ownership

        Returns:
            List of all quizzes (or user's quizzes if user_id provided)
        """
        if user_id is not None:
            return self.quiz_repo.get_by_user_id(user_id)
        return self.quiz_repo.get_all()

    def get_quiz_by_id(self, quiz_id: int) -> Optional[models.Quiz]:
        """
        Get a quiz by its ID.

        Args:
            quiz_id: Quiz ID

        Returns:
            Quiz instance or None if not found
        """
        return self.quiz_repo.get_by_id(quiz_id)

    def create_quiz(
        self,
        name: str,
        user_id: int,
        subject: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        description: Optional[str] = None
    ) -> models.Quiz:
        """
        Create a new quiz.

        Args:
            name: Quiz name
            user_id: ID of the user who owns this quiz
            subject: Optional subject/category
            category: Optional category within subject (e.g., "Poland" within "Geography")
            level: Optional level of advancement (e.g., "Beginner", "Class 5")
            description: Optional description

        Returns:
            Created quiz instance
        """
        return self.quiz_repo.create_quiz(name, user_id, subject, category, level, description)

    def delete_quiz(self, quiz_id: int) -> bool:
        """
        Delete a quiz by its ID.

        Args:
            quiz_id: Quiz ID

        Returns:
            True if deleted, False if not found
        """
        return self.quiz_repo.delete_by_id(quiz_id)

    # =========================================================================
    # FLASHCARD OPERATIONS
    # =========================================================================

    def get_quiz_flashcards(self, quiz_id: int) -> Sequence[models.Flashcard]:
        """
        Get all flashcards for a quiz.

        Args:
            quiz_id: Quiz ID

        Returns:
            List of flashcards

        Raises:
            ValueError: If quiz not found
        """
        quiz = self.get_quiz_by_id(quiz_id)
        if quiz is None:
            raise ValueError(f"Quiz with id {quiz_id} not found")
        return self.flashcard_repo.get_by_quiz_id(quiz_id)

    def get_flashcards_by_difficulty(self, quiz_id: int, difficulty: int) -> Sequence[models.Flashcard]:
        """
        Get flashcards by difficulty level.

        Args:
            quiz_id: Quiz ID
            difficulty: Difficulty level (1-5)

        Returns:
            List of flashcards with specified difficulty
        """
        return self.flashcard_repo.get_by_difficulty(quiz_id, difficulty)

    def search_flashcards(self, quiz_id: int, text: str) -> Sequence[models.Flashcard]:
        """
        Search flashcards by question text.

        Args:
            quiz_id: Quiz ID
            text: Search text

        Returns:
            List of matching flashcards
        """
        return self.flashcard_repo.search_by_question_text(quiz_id, text)

    # =========================================================================
    # IMPORT OPERATIONS
    # =========================================================================

    def import_quiz_from_file(self, file_path: str, user_id: int) -> models.Quiz:
        """
        Import a quiz from a JSON file.

        Args:
            file_path: Path to JSON file
            user_id: ID of the user who will own this quiz

        Returns:
            Imported quiz instance
        """
        return importers.import_quiz_from_file(self.db, file_path, user_id)

    def import_quiz_from_dict(self, data: dict, user_id: int) -> models.Quiz:
        """
        Import a quiz from a dictionary.

        Args:
            data: Quiz data dictionary
            user_id: ID of the user who will own this quiz

        Returns:
            Imported quiz instance
        """
        return importers.import_quiz_from_dict(self.db, data, user_id)

    # =========================================================================
    # STATISTICS AND ANALYSIS
    # =========================================================================

    def get_quiz_statistics(self, quiz_id: int) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a quiz.

        Args:
            quiz_id: Quiz ID

        Returns:
            Dictionary with quiz statistics
        """
        quiz = self.get_quiz_by_id(quiz_id)
        if not quiz:
            return {}

        cards = self.get_quiz_flashcards(quiz_id)

        # Count difficulties
        difficulties = [card.question_difficulty for card in cards if card.question_difficulty is not None]
        difficulty_distribution = dict(Counter(difficulties))

        # Count languages
        question_langs = [card.question_lang for card in cards if card.question_lang]
        answer_langs = [card.answer_lang for card in cards if card.answer_lang]

        # Get answer type statistics
        answer_type_stats = self.flashcard_repo.get_answer_type_statistics(quiz_id)

        return {
            "total_cards": len(cards),
            "difficulty_distribution": difficulty_distribution,
            "question_languages": dict(Counter(question_langs)),
            "answer_languages": dict(Counter(answer_langs)),
            "answer_types": answer_type_stats,
            "subject": quiz.subject,
            "created_at": quiz.created_at,
            "description": quiz.description,
        }

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def validate_quiz_data(self, data: dict) -> bool:
        """
        Validate quiz data structure.

        Args:
            data: Quiz data dictionary

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if quiz section exists
            if "quiz" not in data:
                return False

            quiz_data = data["quiz"]

            # Check required quiz fields
            if "name" not in quiz_data or not quiz_data["name"]:
                return False

            # Check flashcards
            if "flashcards" in data:
                for card in data["flashcards"]:
                    # Check if card has question and answer
                    if "question" not in card or "answer" not in card:
                        return False

                    question = card["question"]
                    answer = card["answer"]

                    # Check required fields
                    if "title" not in question or "text" not in answer:
                        return False

            return True

        except (TypeError, KeyError):
            return False
