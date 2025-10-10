import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, \
    func  # pylint: disable=import-error
from sqlalchemy.orm import relationship  # pylint: disable=import-error

from core.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # pylint: disable=not-callable

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete-orphan")

    # Ensure both username and email are unique
    __table_args__ = (
        UniqueConstraint("name", name="uq_user_name"),
        UniqueConstraint("email", name="uq_user_email"),
    )


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    subject = Column(String)
    category = Column(String, nullable=True)  # NEW: Category within subject (e.g., "Poland" within "Geography")
    level = Column(String, nullable=True)     # NEW: Level of advancement (e.g., "Beginner", "Class 5")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    description = Column(Text)

    user = relationship("User", back_populates="quizzes")
    flashcards = relationship("Flashcard", back_populates="quiz", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="quiz")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))

    # Question fields
    question_title = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    question_lang = Column(String)
    question_difficulty = Column(Integer, nullable=True)
    question_emoji = Column(String, nullable=True)
    question_image = Column(String, nullable=True)

    # Answer fields with new type support
    answer_text = Column(Text, nullable=False)
    answer_lang = Column(String)
    answer_type = Column(String, default="text", nullable=False)  # NEW: Answer type
    answer_options = Column(JSON, nullable=True)  # NEW: For choice/multiple_choice types
    answer_metadata = Column(JSON, nullable=True)  # NEW: Additional answer configuration

    quiz = relationship("Quiz", back_populates="flashcards")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    mode = Column(String(20), nullable=False)  # "learn" or "test"
    started_at = Column(DateTime(timezone=True), server_default=func.now())  # pylint: disable=not-callable
    completed_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    quiz = relationship("Quiz", back_populates="sessions")
