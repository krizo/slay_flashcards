from core.db.crud.repository import UserRepository, QuizRepository, FlashcardRepository, SessionRepository


def test_user_repository_create_user(test_db):
    """Test creating a user via repository."""
    repo = UserRepository(test_db)
    user = repo.create_user("john")

    assert user.id is not None
    assert user.name == "john"


def test_user_repository_get_by_name(test_db):
    """Test getting user by name."""
    repo = UserRepository(test_db)
    user = repo.create_user("alice")

    found_user = repo.get_by_name("alice")
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.name == "alice"


def test_user_repository_get_by_name_not_found(test_db):
    """Test getting non-existent user returns None."""
    repo = UserRepository(test_db)
    found_user = repo.get_by_name("nonexistent")
    assert found_user is None


def test_user_repository_ensure_exists_creates_new(test_db):
    """Test ensure_exists creates new user when needed."""
    repo = UserRepository(test_db)
    user = repo.ensure_exists("new_user")

    assert user.name == "new_user"
    assert user.id is not None


def test_user_repository_ensure_exists_returns_existing(test_db):
    """Test ensure_exists returns existing user."""
    repo = UserRepository(test_db)
    original_user = repo.create_user("existing")

    found_user = repo.ensure_exists("existing")
    assert found_user.id == original_user.id


def test_quiz_repository_create_quiz(test_db):
    """Test creating a quiz."""
    repo = QuizRepository(test_db)
    quiz = repo.create_quiz("Math Basics", "Mathematics", "Basic math concepts")

    assert quiz.id is not None
    assert quiz.name == "Math Basics"
    assert quiz.subject == "Mathematics"
    assert quiz.description == "Basic math concepts"
    assert quiz.created_at is not None


def test_quiz_repository_get_by_subject(test_db):
    """Test getting quizzes by subject."""
    repo = QuizRepository(test_db)
    repo.create_quiz("French 101", "French")
    repo.create_quiz("Spanish 101", "Spanish")
    repo.create_quiz("French 201", "French")

    french_quizzes = repo.get_by_subject("French")
    assert len(french_quizzes) == 2
    quiz_names = [q.name for q in french_quizzes]
    assert "French 101" in quiz_names
    assert "French 201" in quiz_names


def test_quiz_repository_search_by_name(test_db):
    """Test searching quizzes by name pattern."""
    repo = QuizRepository(test_db)
    repo.create_quiz("Advanced Math", "Mathematics")
    repo.create_quiz("Basic Math", "Mathematics")
    repo.create_quiz("Physics Basics", "Physics")

    math_quizzes = repo.search_by_name("Math")
    assert len(math_quizzes) == 2

    basic_quizzes = repo.search_by_name("Basic")
    assert len(basic_quizzes) == 2


def test_flashcard_repository_create_flashcard(test_db):
    """Test creating a flashcard."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz("Test Quiz")
    question = {"title": "hello", "text": "hello", "lang": "en", "difficulty": 1}
    answer = {"text": "bonjour", "lang": "fr"}

    card = flashcard_repo.create_flashcard(quiz.id, question, answer)

    assert card.id is not None
    assert card.quiz_id == quiz.id
    assert card.question_title == "hello"
    assert card.question_text == "hello"
    assert card.question_lang == "en"
    assert card.question_difficulty == 1
    assert card.answer_text == "bonjour"
    assert card.answer_lang == "fr"


def test_flashcard_repository_get_by_quiz_id(test_db, example_quiz_data):
    """Test getting flashcards by quiz ID."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz("Test Quiz")
    flashcard_repo.bulk_create_flashcards(quiz.id, example_quiz_data["flashcards"])

    cards = flashcard_repo.get_by_quiz_id(quiz.id)
    assert len(cards) == 3

    # Check first card
    dog_card = next(c for c in cards if c.question_title == "dog")
    assert dog_card.question_emoji == "🐶"
    assert dog_card.answer_text == "chien"


def test_flashcard_repository_get_by_difficulty(test_db, example_quiz_data):
    """Test getting flashcards by difficulty."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz("Test Quiz")
    flashcard_repo.bulk_create_flashcards(quiz.id, example_quiz_data["flashcards"])

    easy_cards = flashcard_repo.get_by_difficulty(quiz.id, 1)
    assert len(easy_cards) == 2  # dog and cat

    medium_cards = flashcard_repo.get_by_difficulty(quiz.id, 2)
    assert len(medium_cards) == 1  # house


def test_flashcard_repository_search_by_question_text(test_db, example_quiz_data):
    """Test searching flashcards by question text."""
    quiz_repo = QuizRepository(test_db)
    flashcard_repo = FlashcardRepository(test_db)

    quiz = quiz_repo.create_quiz("Test Quiz")
    flashcard_repo.bulk_create_flashcards(quiz.id, example_quiz_data["flashcards"])

    dog_cards = flashcard_repo.search_by_question_text(quiz.id, "dog")
    assert len(dog_cards) == 1
    assert dog_cards[0].question_title == "dog"

    # Case in-sensitive search
    cat_cards = flashcard_repo.search_by_question_text(quiz.id, "CAT")
    assert len(cat_cards) == 1


def test_session_repository_create_session(test_db):
    """Test creating a session."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user("test_user")
    quiz = quiz_repo.create_quiz("Test Quiz")

    session = session_repo.create_session(user.id, quiz.id, "learn")

    assert session.id is not None
    assert session.user_id == user.id
    assert session.quiz_id == quiz.id
    assert session.mode == "learn"
    assert session.score is None
    assert session.started_at is not None


def test_session_repository_get_by_user_id(test_db):
    """Test getting sessions by user ID."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user1 = user_repo.create_user("user1")
    user2 = user_repo.create_user("user2")
    quiz = quiz_repo.create_quiz("Test Quiz")

    session_repo.create_session(user1.id, quiz.id, "learn")
    session_repo.create_session(user1.id, quiz.id, "test", 85)
    session_repo.create_session(user2.id, quiz.id, "learn")

    user1_sessions = session_repo.get_by_user_id(user1.id)
    assert len(user1_sessions) == 2

    user2_sessions = session_repo.get_by_user_id(user2.id)
    assert len(user2_sessions) == 1


def test_session_repository_get_by_mode(test_db):
    """Test getting sessions by mode."""
    user_repo = UserRepository(test_db)
    quiz_repo = QuizRepository(test_db)
    session_repo = SessionRepository(test_db)

    user = user_repo.create_user("test_user")
    quiz = quiz_repo.create_quiz("Test Quiz")

    session_repo.create_session(user.id, quiz.id, "learn")
    session_repo.create_session(user.id, quiz.id, "learn")
    session_repo.create_session(user.id, quiz.id, "test", 90)

    learn_sessions = session_repo.get_by_mode(user.id, "learn")
    assert len(learn_sessions) == 2

    test_sessions = session_repo.get_by_mode(user.id, "test")
    assert len(test_sessions) == 1
    assert test_sessions[0].score == 90
