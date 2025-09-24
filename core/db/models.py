from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import datetime

from core.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    sessions = relationship("Session", back_populates="user")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    description = Column(Text)

    flashcards = relationship("Flashcard", back_populates="quiz")
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
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    mode = Column(String)  # "learn" or "test"
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    score = Column(Integer, nullable=True)

    user = relationship("User", back_populates="sessions")
    quiz = relationship("Quiz", back_populates="sessions")