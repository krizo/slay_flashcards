from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from collections import Counter

from db import models
from db.crud import quizzes, flashcards, importers


class QuizService:
    """Service for managing quizzes and flashcards."""

    def __init__(self, db: Session):
        self.db = db

    def get_all_quizzes(self) -> List[models.Quiz]:
        """Get all available quizzes."""
        return quizzes.get_quizzes(self.db)

    def get_quiz_by_id(self, quiz_id: int) -> Optional[models.Quiz]:
        """Get a quiz by its ID."""
        return quizzes.get_quiz(self.db, quiz_id)

    def get_quiz_flashcards(self, quiz_id: int) -> List[models.Flashcard]:
        """Get all flashcards for a quiz."""
        return flashcards.get_flashcards_for_quiz(self.db, quiz_id)

    def import_quiz_from_file(self, file_path: str) -> models.Quiz:
        """Import a quiz from a JSON file."""
        return importers.import_quiz_from_file(self.db, file_path)

    def import_quiz_from_dict(self, data: dict) -> models.Quiz:
        """Import a quiz from a dictionary."""
        return importers.import_quiz_from_dict(self.db, data)

    def create_quiz(self, name: str, subject: str = None, description: str = None) -> models.Quiz:
        """Create a new quiz."""
        return quizzes.create_quiz(self.db, name, subject, description)

    def get_flashcards_by_difficulty(self, quiz_id: int, difficulty: int) -> List[models.Flashcard]:
        """Get flashcards by difficulty level."""
        return [card for card in self.get_quiz_flashcards(quiz_id)
                if card.question_difficulty == difficulty]

    def search_flashcards(self, quiz_id: int, text: str) -> List[models.Flashcard]:
        """Search flashcards by question text."""
        cards = self.get_quiz_flashcards(quiz_id)
        return [card for card in cards
                if text.lower() in card.question_text.lower()]

    def get_quiz_statistics(self, quiz_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a quiz."""
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

        return {
            "total_cards": len(cards),
            "difficulty_distribution": difficulty_distribution,
            "question_languages": dict(Counter(question_langs)),
            "answer_languages": dict(Counter(answer_langs)),
            "subject": quiz.subject,
            "created_at": quiz.created_at,
            "description": quiz.description
        }

    def validate_quiz_data(self, data: dict) -> bool:
        """Validate quiz data structure."""
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