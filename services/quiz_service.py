from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from db import models
from db.crud import quizzes, flashcards, users, sessions, importers


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

    def create_quiz(self, name: str, subject: str = None, description: str = None) -> models.Quiz:
        """Create a new quiz."""
        return quizzes.create_quiz(self.db, name, subject, description)

