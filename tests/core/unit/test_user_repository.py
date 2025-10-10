"""
Unit tests for UserRepository.

Tests all user-related database operations including:
- User creation and validation
- User lookup (by name, email, ID)
- User search operations
- User modification (rename, email update, password update)
- User deletion with cascade
- User activity queries
- User statistics
"""
from datetime import datetime, timedelta
import pytest

from core.db.crud.repository.user_repository import UserRepository
from core.db.crud.repository.session_repository import SessionRepository
from core.db.crud.repository.quiz_repository import QuizRepository


# =============================================================================
# USER CREATION TESTS
# =============================================================================

def test_create_user_minimal(test_db):
    """Test creating user with minimal required fields."""
    user_repo = UserRepository(test_db)
    user = user_repo.create_user(
        name="testuser",
        email="test@example.com"
    )

    assert user.id is not None
    assert user.name == "testuser"
    assert user.email == "test@example.com"
    assert user.created_at is not None


def test_create_user_with_password(test_db):
    """Test creating user with password hash."""
    user_repo = UserRepository(test_db)
    user = user_repo.create_user(
        name="secureuser",
        email="secure@example.com",
        password_hash="hashed_password_123"
    )

    assert user.password_hash == "hashed_password_123"


def test_create_user_normalizes_input(test_db):
    """Test that user creation normalizes inputs."""
    user_repo = UserRepository(test_db)
    user = user_repo.create_user(
        name="  SpacedUser  ",
        email="  UPPER@EXAMPLE.COM  "
    )

    assert user.name == "SpacedUser"
    assert user.email == "upper@example.com"


def test_create_user_duplicate_name_fails(test_db):
    """Test that creating user with duplicate name fails."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="duplicate", email="first@example.com")

    with pytest.raises(ValueError, match="already exists"):
        user_repo.create_user(name="duplicate", email="second@example.com")


def test_create_user_duplicate_email_fails(test_db):
    """Test that creating user with duplicate email fails."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="user1", email="same@example.com")

    with pytest.raises(ValueError, match="already exists"):
        user_repo.create_user(name="user2", email="same@example.com")


def test_create_user_empty_name_fails(test_db):
    """Test that empty username fails validation."""
    user_repo = UserRepository(test_db)

    with pytest.raises(ValueError, match="cannot be empty"):
        user_repo.create_user(name="", email="test@example.com")


def test_create_user_empty_email_fails(test_db):
    """Test that empty email fails validation."""
    user_repo = UserRepository(test_db)

    with pytest.raises(ValueError, match="cannot be empty"):
        user_repo.create_user(name="testuser", email="")


def test_ensure_user_exists_creates_new(test_db):
    """Test ensure_user_exists creates new user when not found."""
    user_repo = UserRepository(test_db)
    user = user_repo.ensure_user_exists("newuser")

    assert user.id is not None
    assert user.name == "newuser"
    assert "@generated.local" in user.email


def test_ensure_user_exists_returns_existing(test_db):
    """Test ensure_user_exists returns existing user."""
    user_repo = UserRepository(test_db)
    first = user_repo.create_user(name="existing", email="existing@example.com")
    second = user_repo.ensure_user_exists("existing")

    assert first.id == second.id
    assert first.email == second.email


# =============================================================================
# USER LOOKUP TESTS
# =============================================================================

def test_get_by_id(test_db):
    """Test getting user by ID."""
    user_repo = UserRepository(test_db)
    created = user_repo.create_user(name="testuser", email="test@example.com")
    found = user_repo.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.name == "testuser"


def test_get_by_id_not_found(test_db):
    """Test getting non-existent user by ID returns None."""
    user_repo = UserRepository(test_db)
    found = user_repo.get_by_id(99999)

    assert found is None


def test_get_by_name(test_db):
    """Test getting user by name."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="findme", email="find@example.com")
    found = user_repo.get_by_name("findme")

    assert found is not None
    assert found.name == "findme"


def test_get_by_name_case_insensitive(test_db):
    """Test that get_by_name is case-insensitive."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="CaseSensitive", email="case@example.com")

    found = user_repo.get_by_name("casesensitive")
    assert found is not None
    assert found.name == "CaseSensitive"


def test_get_by_name_not_found(test_db):
    """Test getting non-existent user by name returns None."""
    user_repo = UserRepository(test_db)
    found = user_repo.get_by_name("nonexistent")

    assert found is None


def test_get_by_email(test_db):
    """Test getting user by email."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="emailuser", email="email@example.com")
    found = user_repo.get_by_email("email@example.com")

    assert found is not None
    assert found.email == "email@example.com"


def test_get_by_email_case_insensitive(test_db):
    """Test that get_by_email is case-insensitive."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="emailuser", email="Email@Example.COM")

    found = user_repo.get_by_email("email@example.com")
    assert found is not None


def test_exists_by_name(test_db):
    """Test checking if username exists."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="exists", email="exists@example.com")

    assert user_repo.exists_by_name("exists") is True
    assert user_repo.exists_by_name("notexists") is False


def test_exists_by_email(test_db):
    """Test checking if email exists."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="user", email="exists@example.com")

    assert user_repo.exists_by_email("exists@example.com") is True
    assert user_repo.exists_by_email("notexists@example.com") is False


def test_get_all(test_db):
    """Test getting all users."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="user1", email="user1@example.com")
    user_repo.create_user(name="user2", email="user2@example.com")
    user_repo.create_user(name="user3", email="user3@example.com")

    users = user_repo.get_all()
    assert len(users) >= 3


def test_count(test_db):
    """Test counting total users."""
    user_repo = UserRepository(test_db)
    initial_count = user_repo.count()

    user_repo.create_user(name="user1", email="user1@example.com")
    user_repo.create_user(name="user2", email="user2@example.com")

    assert user_repo.count() == initial_count + 2


# =============================================================================
# USER SEARCH TESTS
# =============================================================================

def test_search_by_name_pattern(test_db):
    """Test searching users by name pattern."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="john_doe", email="john@example.com")
    user_repo.create_user(name="jane_doe", email="jane@example.com")
    user_repo.create_user(name="bob_smith", email="bob@example.com")

    results = user_repo.search_by_name_pattern("doe")
    assert len(results) >= 2
    assert all("doe" in user.name.lower() for user in results)


def test_search_by_name_pattern_case_insensitive(test_db):
    """Test that name search is case-insensitive."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="JohnDoe", email="john@example.com")

    results = user_repo.search_by_name_pattern("john")
    assert len(results) >= 1


def test_search_by_email_pattern(test_db):
    """Test searching users by email pattern."""
    user_repo = UserRepository(test_db)
    user_repo.create_user(name="user1", email="john@company.com")
    user_repo.create_user(name="user2", email="jane@company.com")
    user_repo.create_user(name="user3", email="bob@other.com")

    results = user_repo.search_by_email_pattern("company")
    assert len(results) >= 2
    assert all("company" in user.email.lower() for user in results)


# =============================================================================
# USER MODIFICATION TESTS
# =============================================================================

def test_rename_user(test_db):
    """Test renaming a user."""
    user_repo = UserRepository(test_db)
    user = user_repo.create_user(name="oldname", email="test@example.com")

    updated = user_repo.rename_user(user.id, "newname")

    assert updated is not None
    assert updated.name == "newname"
    assert updated.id == user.id


def test_rename_user_validates_uniqueness(test_db):
    """Test that rename validates name uniqueness."""
    user_repo = UserRepository(test_db)
    user1 = user_repo.create_user(name="user1", email="user1@example.com")
    user_repo.create_user(name="taken", email="user2@example.com")

    with pytest.raises(ValueError, match="already exists"):
        user_repo.rename_user(user1.id, "taken")


def test_rename_user_not_found(test_db):
    """Test renaming non-existent user returns None."""
    user_repo = UserRepository(test_db)
    result = user_repo.rename_user(99999, "newname")

    assert result is None


def test_update_email(test_db):
    """Test updating user email."""
    user_repo = UserRepository(test_db)
    user = user_repo.create_user(name="user", email="old@example.com")

    updated = user_repo.update_email(user.id, "new@example.com")

    assert updated is not None
    assert updated.email == "new@example.com"


def test_update_email_validates_uniqueness(test_db):
    """Test that email update validates uniqueness."""
    user_repo = UserRepository(test_db)
    user1 = user_repo.create_user(name="user1", email="user1@example.com")
    user_repo.create_user(name="user2", email="taken@example.com")

    with pytest.raises(ValueError, match="already exists"):
        user_repo.update_email(user1.id, "taken@example.com")


def test_update_password(test_db):
    """Test updating user password hash."""
    user_repo = UserRepository(test_db)
    user = user_repo.create_user(name="user", email="user@example.com")

    updated = user_repo.update_password(user.id, "new_hashed_password")

    assert updated is not None
    assert updated.password_hash == "new_hashed_password"


# =============================================================================
# USER DELETION TESTS
# =============================================================================

def test_delete_user(test_db):
    """Test deleting a user."""
    user_repo = UserRepository(test_db)
    user = user_repo.create_user(name="todelete", email="delete@example.com")
    user_id = user.id

    user_repo.delete(user)

    assert user_repo.get_by_id(user_id) is None


def test_delete_by_id(test_db):
    """Test deleting user by ID."""
    user_repo = UserRepository(test_db)
    user = user_repo.create_user(name="todelete", email="delete@example.com")

    result = user_repo.delete_by_id(user.id)

    assert result is True
    assert user_repo.get_by_id(user.id) is None


def test_delete_by_id_not_found(test_db):
    """Test deleting non-existent user returns False."""
    user_repo = UserRepository(test_db)
    result = user_repo.delete_by_id(99999)

    assert result is False


def test_delete_user_and_sessions_cascade(test_db):
    """Test that deleting user also deletes their sessions."""
    user_repo = UserRepository(test_db)
    session_repo = SessionRepository(test_db)
    quiz_repo = QuizRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)
    session_repo.create_session(user.id, quiz.id, "learn")

    result = user_repo.delete_user_and_sessions(user.id)

    assert result is True
    assert user_repo.get_by_id(user.id) is None
    assert len(session_repo.get_by_user_id(user.id)) == 0


# =============================================================================
# USER ACTIVITY TESTS
# =============================================================================

def test_get_users_with_sessions(test_db):
    """Test getting users who have sessions."""
    user_repo = UserRepository(test_db)
    session_repo = SessionRepository(test_db)
    quiz_repo = QuizRepository(test_db)

    active_user = user_repo.create_user(name="active", email="active@example.com")
    user_repo.create_user(name="inactive", email="inactive@example.com")

    quiz = quiz_repo.create_quiz(name="Quiz", user_id=active_user.id)
    session_repo.create_session(active_user.id, quiz.id, "learn")

    users_with_sessions = user_repo.get_users_with_sessions()
    user_names = [u.name for u in users_with_sessions]

    assert "active" in user_names


def test_get_most_active_users(test_db):
    """Test getting most active users by session count."""
    user_repo = UserRepository(test_db)
    session_repo = SessionRepository(test_db)
    quiz_repo = QuizRepository(test_db)

    user1 = user_repo.create_user(name="user1", email="user1@example.com")
    user2 = user_repo.create_user(name="user2", email="user2@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user1.id)

    # User1 has 3 sessions, User2 has 1
    for _ in range(3):
        session_repo.create_session(user1.id, quiz.id, "learn")
    session_repo.create_session(user2.id, quiz.id, "learn")

    most_active = user_repo.get_most_active_users(limit=5)

    assert len(most_active) >= 2
    # First user should have most sessions
    _, count = most_active[0]
    assert count >= 3


def test_get_users_by_registration_date(test_db):
    """Test getting users by registration date range."""
    user_repo = UserRepository(test_db)

    user_repo.create_user(name="recent", email="recent@example.com")

    # Get users from last week
    start_date = datetime.now() - timedelta(days=7)
    users = user_repo.get_users_by_registration_date(start_date=start_date)

    assert len(users) >= 1
    assert any(u.name == "recent" for u in users)


# =============================================================================
# USER STATISTICS TESTS
# =============================================================================

def test_get_user_statistics_summary(test_db):
    """Test getting user statistics summary."""
    user_repo = UserRepository(test_db)
    session_repo = SessionRepository(test_db)
    quiz_repo = QuizRepository(test_db)

    user = user_repo.create_user(name="user", email="user@example.com")
    quiz = quiz_repo.create_quiz(name="Quiz", user_id=user.id)
    session_repo.create_session(user.id, quiz.id, "learn")

    stats = user_repo.get_user_statistics_summary()

    assert "total_users" in stats
    assert "users_with_activity" in stats
    assert "inactive_users" in stats
    assert stats["total_users"] >= 1
    assert stats["users_with_activity"] >= 1
