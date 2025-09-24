"""
Solution: Move E2E fixtures to main conftest.py to avoid plugin conflicts

Replace or update your main tests/conftest.py with this content.
This avoids the plugin registration conflict by putting all fixtures in one place.
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.db import models
from core.db.database import Base
from core.learning.sessions.quiz_session import TestSession, TestSessionConfig
from core.services.audio_service import SilentAudioService
from core.services.quiz_service import QuizService
from core.services.user_service import UserService


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    yield db

    db.close()


@pytest.fixture(scope="function")
def quiz_service(test_db):
    """Create QuizService with test database."""
    return QuizService(test_db)


@pytest.fixture(scope="function")
def user_service(test_db):
    """Create UserService with test database."""
    return UserService(test_db)


@pytest.fixture(scope="session")
def example_quiz_data():
    """Load the example quiz data."""
    return {
        "quiz": {
            "name": "French Basics",
            "subject": "French",
            "created_at": "2025-09-17",
            "description": "Basic French vocabulary for beginners"
        },
        "flashcards": [
            {
                "question": {
                    "title": "dog",
                    "text": "dog",
                    "lang": "en",
                    "difficulty": 1,
                    "emoji": "🐶",
                    "image": "dog.png"
                },
                "answer": {
                    "text": "chien",
                    "lang": "fr"
                }
            },
            {
                "question": {
                    "title": "cat",
                    "text": "cat",
                    "lang": "en",
                    "difficulty": 1,
                    "emoji": "🐱",
                    "image": "cat.png"
                },
                "answer": {
                    "text": "chat",
                    "lang": "fr"
                }
            },
            {
                "question": {
                    "title": "house",
                    "text": "house",
                    "lang": "en",
                    "difficulty": 2,
                    "emoji": "🏠"
                },
                "answer": {
                    "text": "maison",
                    "lang": "fr"
                }
            }
        ]
    }


@pytest.fixture(scope="function")
def temp_quiz_file(example_quiz_data):
    """Create a temporary quiz file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(example_quiz_data, f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    os.unlink(temp_file)


@pytest.fixture(scope="function")
def sample_user(user_service):
    """Create a sample user for testing."""
    return user_service.create_user("testuser")


@pytest.fixture(scope="function")
def sample_quiz_with_cards(quiz_service, example_quiz_data):
    """Create a sample quiz with flashcards."""
    return quiz_service.import_quiz_from_dict(example_quiz_data)


# =============================================================================
# E2E SPECIFIC FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def e2e_test_config():
    """Configuration for E2E tests."""
    return {
        "test_timeout": 30,  # seconds
        "performance_threshold": 5.0,  # seconds for large operations
        "audio_enabled": False,  # Disable audio for faster tests
        "strict_mode": False,  # Use flexible matching by default
        "similarity_threshold": 0.8,
        "temp_file_cleanup": True,
    }


@pytest.fixture(scope="function")
def e2e_database():
    """Create isolated database for each E2E test."""
    # Use in-memory SQLite for E2E tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db
    
    db.close()


@pytest.fixture(scope="function")
def e2e_services(e2e_database):
    """Create service instances for E2E tests."""
    return {
        "quiz_service": QuizService(e2e_database),
        "user_service": UserService(e2e_database),
        "audio_service": SilentAudioService(),
        "database": e2e_database
    }


@pytest.fixture(scope="function")
def temp_directory():
    """Create temporary directory for file operations."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


# =============================================================================
# E2E QUIZ CONTENT FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def basic_french_quiz():
    """Basic French vocabulary quiz for E2E tests."""
    return {
        "quiz": {
            "name": "French Basics",
            "subject": "French",
            "description": "Essential French vocabulary for beginners"
        },
        "flashcards": [
            {
                "question": {"title": "hello", "text": "hello", "lang": "en", "difficulty": 1, "emoji": "👋"},
                "answer": {"text": "bonjour", "lang": "fr"}
            },
            {
                "question": {"title": "goodbye", "text": "goodbye", "lang": "en", "difficulty": 1, "emoji": "👋"},
                "answer": {"text": "au revoir", "lang": "fr"}
            },
            {
                "question": {"title": "thank you", "text": "thank you", "lang": "en", "difficulty": 2, "emoji": "🙏"},
                "answer": {"text": "merci", "lang": "fr"}
            },
            {
                "question": {"title": "please", "text": "please", "lang": "en", "difficulty": 2, "emoji": "🙏"},
                "answer": {"text": "s'il vous plaît", "lang": "fr"}
            }
        ]
    }


@pytest.fixture(scope="session")
def advanced_vocabulary_quiz():
    """Advanced vocabulary quiz for challenging scenarios."""
    return {
        "quiz": {
            "name": "Advanced English Vocabulary",
            "subject": "English",
            "description": "Challenging vocabulary for advanced learners"
        },
        "flashcards": [
            {
                "question": {"title": "perspicacious", "text": "Define: perspicacious", "lang": "en", "difficulty": 5},
                "answer": {"text": "having keen insight and understanding", "lang": "en"}
            },
            {
                "question": {"title": "ubiquitous", "text": "Define: ubiquitous", "lang": "en", "difficulty": 4},
                "answer": {"text": "present everywhere at the same time", "lang": "en"}
            },
            {
                "question": {"title": "ephemeral", "text": "Define: ephemeral", "lang": "en", "difficulty": 4},
                "answer": {"text": "lasting for a very short time", "lang": "en"}
            }
        ]
    }


@pytest.fixture(scope="session")
def programming_quiz():
    """Programming concepts quiz for technical scenarios."""
    return {
        "quiz": {
            "name": "Python Programming Basics",
            "subject": "Programming",
            "description": "Fundamental Python programming concepts"
        },
        "flashcards": [
            {"question": {"title": "list comprehension", "text": "Syntax for list comprehension"}, "answer": {"text": "[expression for item in iterable]"}},
            {"question": {"title": "lambda function", "text": "Syntax for lambda function"}, "answer": {"text": "lambda arguments: expression"}},
            {"question": {"title": "exception handling", "text": "Keywords for exception handling"}, "answer": {"text": "try, except, finally"}},
            {"question": {"title": "dictionary comprehension", "text": "Syntax for dictionary comprehension"}, "answer": {"text": "{key: value for item in iterable}"}}
        ]
    }


# =============================================================================
# E2E USER PERSONA FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def user_personas():
    """Different user personas for testing various scenarios."""
    return {
        "beginner_student": {
            "name": "beginner_student",
            "skill_level": "novice",
            "learning_style": "visual",
            "patience_level": "high",
            "typical_answers": {
                "french_hello": "hello",  # English answer to French question
                "accuracy": 0.3  # 30% accuracy initially
            }
        },
        "intermediate_student": {
            "name": "intermediate_student", 
            "skill_level": "intermediate",
            "learning_style": "mixed",
            "patience_level": "medium",
            "typical_answers": {
                "french_hello": "bonjor",  # Close but with typos
                "accuracy": 0.7  # 70% accuracy
            }
        },
        "advanced_student": {
            "name": "advanced_student",
            "skill_level": "advanced",
            "learning_style": "auditory",
            "patience_level": "low",
            "typical_answers": {
                "french_hello": "bonjour",  # Correct answers
                "accuracy": 0.95  # 95% accuracy
            }
        },
        "struggling_student": {
            "name": "struggling_student",
            "skill_level": "novice",
            "learning_style": "kinesthetic",
            "patience_level": "low",
            "typical_answers": {
                "french_hello": "hi",  # Wrong answers
                "accuracy": 0.2  # 20% accuracy
            }
        },
        "teacher": {
            "name": "teacher",
            "skill_level": "expert", 
            "learning_style": "analytical",
            "patience_level": "high",
            "role": "educator",
            "creates_content": True
        }
    }


@pytest.fixture
def create_user_with_persona(e2e_services, user_personas):
    """Factory function to create users based on personas."""
    def _create_user(persona_name: str, custom_name: str = None):
        persona = user_personas[persona_name]
        user_name = custom_name or persona["name"]
        
        user_service = e2e_services["user_service"]
        user = user_service.ensure_user_exists(user_name)
        
        # Attach persona data to user for test reference
        user._test_persona = persona
        return user
    
    return _create_user


# =============================================================================
# E2E MOCK PRESENTER FIXTURES
# =============================================================================

@pytest.fixture
def mock_presenter_factory():
    """Factory for creating mock presenters with different behaviors."""
    def _create_presenter(answers: List[str] = None, behavior: str = "normal"):
        presenter = Mock()
        presenter.show_test_header = Mock()
        presenter.show_question = Mock()
        presenter.show_answer_result = Mock()
        presenter.wait_for_next = Mock()
        presenter.show_final_results = Mock()
        
        if answers:
            if behavior == "quit_early":
                # Quit after some answers
                quit_index = len(answers) // 2
                modified_answers = answers[:quit_index] + ["quit"]
                presenter.get_user_answer = Mock(side_effect=modified_answers)
            elif behavior == "interrupted":
                # Simulate keyboard interrupt
                presenter.get_user_answer = Mock(side_effect=KeyboardInterrupt())
            else:  # normal behavior
                presenter.get_user_answer = Mock(side_effect=answers)
        else:
            presenter.get_user_answer = Mock(return_value="default_answer")
        
        return presenter
    
    return _create_presenter


@pytest.fixture
def adaptive_presenter_factory(user_personas):
    """Factory for creating presenters that adapt based on user personas."""
    def _create_adaptive_presenter(persona_name: str, quiz_cards: List):
        persona = user_personas[persona_name]
        accuracy = persona["typical_answers"]["accuracy"]
        
        # Generate answers based on persona accuracy
        answers = []
        correct_count = int(len(quiz_cards) * accuracy)
        
        for i, card in enumerate(quiz_cards):
            if i < correct_count:
                # Give correct answer
                answers.append(card.answer_text)
            else:
                # Give incorrect answer based on persona
                if persona["skill_level"] == "novice":
                    answers.append("wrong_answer")
                else:
                    # Give close but not perfect answer
                    correct = card.answer_text
                    if len(correct) > 3:
                        # Add typo
                        answers.append(correct[:-1] + "x")
                    else:
                        answers.append("wrong")
        
        presenter = Mock()
        presenter.show_test_header = Mock()
        presenter.show_question = Mock()
        presenter.get_user_answer = Mock(side_effect=answers)
        presenter.show_answer_result = Mock()
        presenter.wait_for_next = Mock()
        presenter.show_final_results = Mock()
        
        return presenter
    
    return _create_adaptive_presenter


# =============================================================================
# E2E WORKFLOW HELPER FIXTURES
# =============================================================================

@pytest.fixture
def quiz_workflow(e2e_services):
    """Helper for common quiz workflow operations."""
    class QuizWorkflow:
        def __init__(self, services):
            self.services = services
            
        def create_and_import_quiz(self, quiz_data: Dict[str, Any]):
            """Create and import a quiz, return quiz object and cards."""
            quiz_service = self.services["quiz_service"]
            quiz = quiz_service.import_quiz_from_dict(quiz_data)
            cards = quiz_service.get_quiz_flashcards(quiz.id)
            return quiz, cards
            
        def run_learning_session(self, user, quiz_id: int):
            """Run a learning session for a user."""
            user_service = self.services["user_service"]
            return user_service.create_session(user.id, quiz_id, "learn")
            
        def run_test_session(self, user, quiz, cards, presenter, config):
            """Run a complete test session and save results."""

            user_service = self.services["user_service"]
            audio_service = self.services["audio_service"]
            
            session = TestSession(cards, presenter, audio_service, config)
            result = session.start()
            score = session.get_final_score()
            
            # Save session
            db_session = user_service.create_session(user.id, quiz.id, "test", score)
            
            return {
                "result": result,
                "score": score,
                "session": session,
                "db_session": db_session,
                "detailed_results": session.get_detailed_results()
            }
    
    return QuizWorkflow(e2e_services)


@pytest.fixture
def progress_analyzer(e2e_services):
    """Helper for analyzing user progress and generating reports."""
    class ProgressAnalyzer:
        def __init__(self, services):
            self.services = services
            
        def get_user_progress(self, user):
            """Get comprehensive progress data for a user."""
            user_service = self.services["user_service"]
            sessions = user_service.get_user_sessions(user.id)
            
            learn_sessions = [s for s in sessions if s.mode == "learn"]
            test_sessions = [s for s in sessions if s.mode == "test"]
            
            return {
                "total_sessions": len(sessions),
                "learn_sessions": len(learn_sessions),
                "test_sessions": len(test_sessions),
                "test_scores": [s.score for s in test_sessions],
                "improvement": self._calculate_improvement(test_sessions),
                "recent_activity": sessions[:5]  # Most recent 5
            }
            
        @staticmethod
        def _calculate_improvement(test_sessions):
            """Calculate improvement between first and last test."""
            if len(test_sessions) < 2:
                return 0
            
            # Sessions are ordered newest first
            latest_score = test_sessions[0].score
            earliest_score = test_sessions[-1].score
            return latest_score - earliest_score
            
        def generate_class_report(self, users, quiz_id):
            """Generate class-wide performance report."""
            all_scores = []
            user_reports = []
            
            for user in users:
                progress = self.get_user_progress(user)
                user_test_scores = [
                    s.score for s in progress["recent_activity"] 
                    if s.mode == "test" and s.quiz_id == quiz_id
                ]
                
                if user_test_scores:
                    best_score = max(user_test_scores)
                    all_scores.append(best_score)
                    user_reports.append({
                        "user": user.name,
                        "best_score": best_score,
                        "attempts": len(user_test_scores)
                    })
            
            return {
                "class_average": sum(all_scores) / len(all_scores) if all_scores else 0,
                "highest_score": max(all_scores) if all_scores else 0,
                "lowest_score": min(all_scores) if all_scores else 0,
                "total_students": len(users),
                "students_tested": len(user_reports),
                "user_reports": user_reports
            }

        def analyze_progress(self, user_sessions: List) -> dict:
            """Analyze user progress over time."""
            if len(user_sessions) < 2:
                return {
                    "improvement": 0,
                    "trend": "insufficient_data",
                    "sessions_analyzed": len(user_sessions)
                }

            # Get test sessions with scores
            test_sessions = [s for s in user_sessions if s.mode == "test" and s.score is not None]

            if len(test_sessions) < 2:
                return {
                    "improvement": 0,
                    "trend": "insufficient_data",
                    "sessions_analyzed": len(test_sessions)
                }

            # Sort by time (oldest first)
            sorted_sessions = sorted(test_sessions, key=lambda x: x.started_at)

            # Calculate improvement: latest score - first score
            first_score = sorted_sessions[0].score
            latest_score = sorted_sessions[-1].score
            improvement = latest_score - first_score

            # Determine trend
            if improvement > 10:
                trend = "improving"
            elif improvement < -10:
                trend = "declining"
            else:
                trend = "stable"

            return {
                "improvement": improvement,
                "trend": trend,
                "sessions_analyzed": len(sorted_sessions),
                "first_score": first_score,
                "latest_score": latest_score
            }
    return ProgressAnalyzer(e2e_services)


# =============================================================================
# E2E VALIDATION FIXTURES
# =============================================================================

@pytest.fixture
def test_validators():
    """Validators for common test assertions."""
    class TestValidators:
        @staticmethod
        def validate_quiz_structure(quiz):
            """Validate quiz has correct structure."""
            assert hasattr(quiz, 'id')
            assert hasattr(quiz, 'name')
            assert hasattr(quiz, 'subject')
            assert quiz.name is not None
            
        @staticmethod
        def validate_user_session(session):
            """Validate session has correct structure."""
            assert hasattr(session, 'id')
            assert hasattr(session, 'user_id')
            assert hasattr(session, 'quiz_id')
            assert hasattr(session, 'mode')
            assert session.mode in ["learn", "test"]
            
        @staticmethod
        def validate_test_results(results):
            """Validate test results structure."""
            required_keys = ["total_questions", "correct", "incorrect", "final_score"]
            for key in required_keys:
                assert key in results
            
            assert 0 <= results["final_score"] <= 100
            assert results["total_questions"] > 0
            
        @staticmethod
        def validate_score_progression(scores, should_improve=True):
            """Validate that scores show expected progression."""
            assert len(scores) >= 2
            if should_improve:
                assert scores[-1] > scores[0], f"Expected improvement: {scores[0]} -> {scores[-1]}"
    
    return TestValidators()


# =============================================================================
# CONFIGURATION FIXTURES  
# =============================================================================

@pytest.fixture
def default_test_config():
    """Create a default test session configuration."""
    return TestSessionConfig(
        audio_enabled=False,
        question_lang="en",
        answer_lang="fr",
        strict_matching=False,
        case_sensitive=False,
        similarity_threshold=0.8,
        allow_partial_credit=True
    )


@pytest.fixture
def strict_test_config():
    """Create a strict test session configuration."""
    return TestSessionConfig(
        audio_enabled=False,
        strict_matching=True,
        case_sensitive=True,
        allow_partial_credit=False
    )


@pytest.fixture
def silent_audio_service():
    """Create a silent audio service for testing."""
    return SilentAudioService()


# =============================================================================
# EXISTING MOCK FIXTURES (keep any existing ones you have)
# =============================================================================

@pytest.fixture
def mock_flashcard():
    """Create a mock flashcard for testing."""
    from unittest.mock import Mock

    card = Mock(spec=models.Flashcard)
    card.id = 1
    card.quiz_id = 1
    card.question_title = "dog"
    card.question_text = "What is 'dog' in French?"
    card.question_lang = "en"
    card.question_emoji = "🐶"
    card.answer_text = "chien"
    card.answer_lang = "fr"
    return card


@pytest.fixture
def mock_flashcards():
    """Create multiple mock flashcards for testing."""
    from unittest.mock import Mock
    from core.db import models
    
    cards = []
    
    # Card 1: dog -> chien
    card1 = Mock(spec=models.Flashcard)
    card1.id = 1
    card1.question_title = "dog"
    card1.question_text = "dog"
    card1.question_lang = "en"
    card1.question_emoji = "🐶"
    card1.answer_text = "chien"
    card1.answer_lang = "fr"
    cards.append(card1)
    
    # Card 2: cat -> chat
    card2 = Mock(spec=models.Flashcard)
    card2.id = 2
    card2.question_title = "cat"
    card2.question_text = "cat"
    card2.question_lang = "en"
    card2.question_emoji = "🐱"
    card2.answer_text = "chat"
    card2.answer_lang = "fr"
    cards.append(card2)
    
    # Card 3: house -> maison
    card3 = Mock(spec=models.Flashcard)
    card3.id = 3
    card3.question_title = "house"
    card3.question_text = "house"
    card3.question_lang = "en"
    card3.question_emoji = "🏠"
    card3.answer_text = "maison"
    card3.answer_lang = "fr"
    cards.append(card3)
    
    return cards


@pytest.fixture
def mock_test_presenter():
    """Create a mock test presenter."""
    presenter = Mock()
    presenter.show_test_header = Mock()
    presenter.show_question = Mock()
    presenter.get_user_answer = Mock()
    presenter.show_answer_result = Mock()
    pytest.fixture
    presenter.wait_for_next = Mock()
    presenter.show_final_results = Mock()
    return presenter