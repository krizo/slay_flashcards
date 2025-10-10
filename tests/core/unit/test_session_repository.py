"""
Unit tests for SessionRepository.

Tests all session-related database operations including:
- Session creation
- Session retrieval (by user, quiz, mode, date ranges)
- Session scoring and statistics
- Recent sessions queries
- Best score tracking
"""
from datetime import datetime, timedelta

from core.db.crud.repository.user_repository import UserRepository
from core.db.crud.repository.quiz_repository import QuizRepository
from core.db.crud.repository.session_repository import SessionRepository


# =============================================================================
# SESSION CREATION TESTS
# =============================================================================

def test_create_session_minimal(test_db):
    """Test creating session with minimal required fields."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session = session_repo.create_session(
        user_id=user.id,
        quiz_id=quiz.id,
        mode="learn"
    )

    assert session.id is not None
    assert session.user_id == user.id
    assert session.quiz_id == quiz.id
    assert session.mode == "learn"
    assert session.score is None
    assert session.started_at is not None


def test_create_session_with_score(test_db):
    """Test creating session with score."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session = session_repo.create_session(
        user_id=user.id,
        quiz_id=quiz.id,
        mode="test",
        score=85
    )

    assert session.score == 85


def test_create_learn_session(test_db):
    """Test creating a learn mode session."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session = session_repo.create_session(user.id, quiz.id, "learn")

    assert session.mode == "learn"


def test_create_test_session(test_db):
    """Test creating a test mode session."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session = session_repo.create_session(user.id, quiz.id, "test", score=90)

    assert session.mode == "test"
    assert session.score == 90


# =============================================================================
# SESSION RETRIEVAL TESTS
# =============================================================================

def test_get_by_id(test_db):
    """Test getting session by ID."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    created = session_repo.create_session(user.id, quiz.id, "learn")
    found = session_repo.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id


def test_get_by_user_id(test_db):
    """Test getting sessions by user ID."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user1 = user_repo.create_user(name="user1", email="user1@example.com")
    user2 = user_repo.create_user(name="user2", email="user2@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user1.id)

    session_repo.create_session(user1.id, quiz.id, "learn")
    session_repo.create_session(user1.id, quiz.id, "test")
    session_repo.create_session(user2.id, quiz.id, "learn")

    user1_sessions = session_repo.get_by_user_id(user1.id)

    assert len(user1_sessions) == 2
    assert all(s.user_id == user1.id for s in user1_sessions)


def test_get_by_quiz_id(test_db):
    """Test getting sessions by quiz ID."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz1 = quiz_repo.create_quiz(name="Quiz 1", user_id=user.id)
    quiz2 = quiz_repo.create_quiz(name="Quiz 2", user_id=user.id)

    session_repo.create_session(user.id, quiz1.id, "learn")
    session_repo.create_session(user.id, quiz1.id, "test")
    session_repo.create_session(user.id, quiz2.id, "learn")

    quiz1_sessions = session_repo.get_by_quiz_id(quiz1.id)

    assert len(quiz1_sessions) == 2
    assert all(s.quiz_id == quiz1.id for s in quiz1_sessions)


def test_get_by_mode(test_db):
    """Test getting sessions by user and mode."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session_repo.create_session(user.id, quiz.id, "learn")
    session_repo.create_session(user.id, quiz.id, "learn")
    session_repo.create_session(user.id, quiz.id, "test")

    learn_sessions = session_repo.get_by_mode(user.id, "learn")

    assert len(learn_sessions) == 2
    assert all(s.mode == "learn" for s in learn_sessions)


def test_get_recent_sessions(test_db):
    """Test getting recent sessions for a user ordered by date."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    for i in range(5):
        session_repo.create_session(user.id, quiz.id, "learn")

    recent = session_repo.get_recent_sessions(user.id, limit=3)

    assert len(recent) == 3
    # Should be ordered by most recent first
    for i in range(len(recent) - 1):
        assert recent[i].started_at >= recent[i + 1].started_at


# =============================================================================
# SESSION ADVANCED QUERIES TESTS
# =============================================================================

def test_get_user_quiz_sessions(test_db):
    """Test getting sessions for specific user-quiz combination."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz1 = quiz_repo.create_quiz(name="Quiz 1", user_id=user.id)
    quiz2 = quiz_repo.create_quiz(name="Quiz 2", user_id=user.id)

    session_repo.create_session(user.id, quiz1.id, "learn")
    session_repo.create_session(user.id, quiz1.id, "test")
    session_repo.create_session(user.id, quiz2.id, "learn")

    user_quiz1_sessions = session_repo.get_user_quiz_sessions(user.id, quiz1.id)

    assert len(user_quiz1_sessions) == 2
    assert all(s.user_id == user.id and s.quiz_id == quiz1.id for s in user_quiz1_sessions)


def test_get_by_user_and_mode(test_db):
    """Test getting sessions filtered by user and mode using get_by_mode."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user1 = user_repo.create_user(name="user1", email="user1@example.com")
    user2 = user_repo.create_user(name="user2", email="user2@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user1.id)

    session_repo.create_session(user1.id, quiz.id, "learn")
    session_repo.create_session(user1.id, quiz.id, "test")
    session_repo.create_session(user2.id, quiz.id, "learn")

    user1_learn = session_repo.get_by_mode(user1.id, "learn")

    assert len(user1_learn) == 1
    assert user1_learn[0].user_id == user1.id
    assert user1_learn[0].mode == "learn"


def test_get_by_quiz_and_mode(test_db):
    """Test getting sessions filtered by quiz and mode."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz1 = quiz_repo.create_quiz(name="Quiz 1", user_id=user.id)
    quiz2 = quiz_repo.create_quiz(name="Quiz 2", user_id=user.id)

    session_repo.create_session(user.id, quiz1.id, "learn")
    session_repo.create_session(user.id, quiz1.id, "test")
    session_repo.create_session(user.id, quiz2.id, "learn")

    quiz1_test = session_repo.get_sessions_by_quiz_and_mode(quiz1.id, "test")

    assert len(quiz1_test) == 1
    assert quiz1_test[0].quiz_id == quiz1.id
    assert quiz1_test[0].mode == "test"


# =============================================================================
# DATE RANGE QUERIES TESTS
# =============================================================================

def test_get_sessions_in_date_range(test_db):
    """Test getting sessions within a date range."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    # Create sessions at different times
    now = datetime.now()
    old_date = now - timedelta(days=10)

    # Create old session with explicit date
    old_session = session_repo.create(
        user_id=user.id,
        quiz_id=quiz.id,
        mode="learn",
        started_at=old_date
    )

    recent_session = session_repo.create_session(user.id, quiz.id, "learn")

    # Get sessions from last 7 days using get_sessions_since_date
    start_date = now - timedelta(days=7)
    recent_sessions = session_repo.get_sessions_since_date(user.id, start_date)

    # Should include recent but not old
    session_ids = [s.id for s in recent_sessions]
    assert recent_session.id in session_ids
    assert old_session.id not in session_ids


def test_get_sessions_by_date_range(test_db):
    """Test getting sessions using date range method."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session_repo.create_session(user.id, quiz.id, "learn")
    today = datetime.now()

    # Use date range method
    sessions_today = session_repo.get_sessions_by_date_range(
        user_id=user.id,
        start_date=today.replace(hour=0, minute=0, second=0),
        end_date=today
    )

    assert len(sessions_today) >= 1


# =============================================================================
# SCORE AND STATISTICS TESTS
# =============================================================================

def test_update_score(test_db):
    """Test updating session score using base update method."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session = session_repo.create_session(user.id, quiz.id, "test")
    updated = session_repo.update(session, score=95)

    assert updated.score == 95


def test_get_best_score(test_db):
    """Test getting best test scores."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session_repo.create_session(user.id, quiz.id, "test", score=70)
    session_repo.create_session(user.id, quiz.id, "test", score=95)
    session_repo.create_session(user.id, quiz.id, "test", score=80)

    best_scores = session_repo.get_best_test_scores(user.id, quiz_id=quiz.id)

    assert len(best_scores) >= 1
    # Should be ordered by score descending, so first is best
    assert best_scores[0].score == 95


def test_get_average_score_from_statistics(test_db):
    """Test calculating average score using session statistics."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session_repo.create_session(user.id, quiz.id, "test", score=70)
    session_repo.create_session(user.id, quiz.id, "test", score=80)
    session_repo.create_session(user.id, quiz.id, "test", score=90)

    stats = session_repo.get_session_statistics(user.id)

    # Statistics should show average score (for test sessions)
    assert "average_score" in stats
    assert stats["average_score"] == 80.0


def test_get_user_statistics(test_db):
    """Test getting comprehensive user statistics."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session_repo.create_session(user.id, quiz.id, "learn")
    session_repo.create_session(user.id, quiz.id, "test", score=85)
    session_repo.create_session(user.id, quiz.id, "test", score=95)

    stats = session_repo.get_session_statistics(user.id)

    assert stats["total_sessions"] == 3
    assert stats["learn_sessions"] == 1
    assert stats["test_sessions"] == 2
    assert stats["average_score"] == 90.0


# =============================================================================
# SESSION MODIFICATION TESTS
# =============================================================================

def test_update_session(test_db):
    """Test updating session fields."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session = session_repo.create_session(user.id, quiz.id, "learn")

    updated = session_repo.update(session, mode="test", score=88)

    assert updated.mode == "test"
    assert updated.score == 88


# =============================================================================
# SESSION DELETION TESTS
# =============================================================================

def test_delete_session(test_db):
    """Test deleting a session."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session = session_repo.create_session(user.id, quiz.id, "learn")
    session_id = session.id

    session_repo.delete(session)

    assert session_repo.get_by_id(session_id) is None


def test_delete_by_id(test_db):
    """Test deleting session by ID."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    session = session_repo.create_session(user.id, quiz.id, "learn")

    result = session_repo.delete_by_id(session.id)

    assert result is True
    assert session_repo.get_by_id(session.id) is None


# =============================================================================
# ACTIVITY TRACKING TESTS
# =============================================================================

def test_get_session_activity(test_db):
    """Test tracking session activity using statistics."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)

    # Create multiple sessions
    for _ in range(5):
        session_repo.create_session(user.id, quiz.id, "learn")

    stats = session_repo.get_session_statistics(user.id)

    assert stats["total_sessions"] >= 5
    assert stats["learn_sessions"] >= 5
