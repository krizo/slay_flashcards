# SlayFlashcards - Complete Documentation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Core Services](#core-services)
- [REST API](#rest-api)
- [Installation](#installation)
- [CLI Usage](#cli-usage)
- [API Usage](#api-usage)
- [Development](#development)
- [Testing](#testing)

## Overview

SlayFlashcards is a modern flashcard learning platform with both CLI and REST API interfaces. It features a clean architecture with repository pattern, service layer, and comprehensive testing.

### Key Features
- 🎓 Interactive learning sessions with audio support
- 📊 Comprehensive progress tracking and statistics
- 🗣️ Text-to-Speech (TTS) for questions and answers
- 🌍 Multi-language support
- 🔐 JWT-based authentication (API)
- 📱 Both CLI and REST API interfaces
- 💾 SQLite database with PostgreSQL migration path
- 🧪 117+ unit tests with 100% repository coverage

## Architecture

SlayFlashcards follows a layered architecture pattern:

```
┌─────────────────────────────────────────────┐
│          Presentation Layer                  │
│  ┌──────────────┐      ┌──────────────┐    │
│  │  CLI (Typer) │      │ REST API     │    │
│  │              │      │ (FastAPI)    │    │
│  └──────────────┘      └──────────────┘    │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│           Service Layer                      │
│  ┌─────────────┐  ┌──────────────┐         │
│  │ QuizService │  │ UserService  │         │
│  │             │  │              │         │
│  └─────────────┘  └──────────────┘         │
│  ┌─────────────┐                           │
│  │AudioService │                           │
│  └─────────────┘                           │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│         Repository Layer                     │
│  ┌────────────────┐  ┌───────────────┐     │
│  │ BaseRepository │  │QuizRepository │     │
│  │   (Generic)    │  │               │     │
│  └────────────────┘  └───────────────┘     │
│  ┌─────────────────┐ ┌────────────────┐    │
│  │UserRepository   │ │SessionRepo     │    │
│  └─────────────────┘ └────────────────┘    │
│  ┌──────────────────┐                      │
│  │FlashcardRepo     │                      │
│  └──────────────────┘                      │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│         Data Layer (SQLAlchemy ORM)         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐   │
│  │ User │ │ Quiz │ │Flash-│ │ Session │   │
│  │      │ │      │ │ card │ │         │   │
│  └──────┘ └──────┘ └──────┘ └─────────┘   │
└─────────────────────────────────────────────┘
                    │
          ┌──────────────────┐
          │  SQLite Database │
          └──────────────────┘
```

## Core Services

### Repository Layer

The repository layer provides a clean abstraction over database operations using the Repository Pattern with generic types.

#### BaseRepository

Generic repository providing CRUD operations for all entities:

**Location**: `core/db/crud/repository/base_repository.py`

**Methods**:
- `get_by_id(id)` - Retrieve entity by ID
- `get_all(limit, offset)` - Get all entities with pagination
- `create(**kwargs)` - Create new entity
- `update(instance, **kwargs)` - Update existing entity
- `delete(instance)` - Delete entity
- `delete_by_id(id)` - Delete by ID
- `count()` - Count total entities
- `exists(id)` - Check if entity exists
- `bulk_create(items)` - Create multiple entities
- `bulk_delete(items)` - Delete multiple entities
- `refresh(instance)` - Refresh entity from database

#### UserRepository

**Location**: `core/db/crud/repository/user_repository.py`

**Features**:
- User creation with validation (duplicate detection, input normalization)
- Case-insensitive lookups by name and email
- User search by name/email patterns
- User modification (rename, email update, password update)
- Cascade deletion with sessions
- Activity tracking (users with sessions, most active users)
- Registration date queries
- Comprehensive user statistics

**Key Methods**:
```python
create_user(name: str, email: str, password_hash: str = None) -> User
get_by_name(name: str) -> Optional[User]
get_by_email(email: str) -> Optional[User]
exists_by_name(name: str) -> bool
exists_by_email(email: str) -> bool
rename_user(user_id: int, new_name: str) -> Optional[User]
update_email(user_id: int, new_email: str) -> Optional[User]
update_password(user_id: int, password_hash: str) -> Optional[User]
search_by_name_pattern(pattern: str) -> List[User]
search_by_email_pattern(pattern: str) -> List[User]
get_users_with_sessions() -> List[User]
get_most_active_users(limit: int = 10) -> List[Tuple[User, int]]
get_users_by_registration_date(start_date, end_date) -> List[User]
get_user_statistics_summary() -> Dict
delete_user_and_sessions(user_id: int) -> bool
ensure_user_exists(name: str) -> User  # Creates with auto-generated email
```

#### QuizRepository

**Location**: `core/db/crud/repository/quiz_repository.py`

**Features**:
- Quiz creation with metadata
- Quiz lookup by ID and name (case-sensitive)
- Subject management (get quizzes by subject, list all subjects)
- Case-insensitive search by name pattern
- Cascade deletion with flashcards
- Bulk operations

**Key Methods**:
```python
create_quiz(name: str, subject: str = None, description: str = None) -> Quiz
get_by_name(name: str) -> Optional[Quiz]
get_by_subject(subject: str) -> List[Quiz]
get_all_subjects() -> List[str]
search_by_name(pattern: str) -> List[Quiz]
```

#### FlashcardRepository

**Location**: `core/db/crud/repository/flashcard_repository.py`

**Features**:
- Flashcard creation with 8 answer types:
  - `text` - Free-form text answer
  - `short_text` - Short text answer
  - `integer` - Numeric integer (with tolerance)
  - `float` - Floating-point number (with tolerance)
  - `range` - Numeric range (min-max)
  - `boolean` - True/false answer
  - `choice` - Single choice from options
  - `multiple_choice` - Multiple selections from options
- Bulk flashcard creation
- Answer type validation with default fallback
- Retrieval by quiz, difficulty, answer type
- Case-insensitive question text search
- Answer type statistics

**Key Methods**:
```python
create_flashcard(
    quiz_id: int,
    question: Dict[str, Any],
    answer: Dict[str, Any]
) -> Flashcard

bulk_create_flashcards(
    quiz_id: int,
    flashcards_data: List[Dict]
) -> List[Flashcard]

get_by_quiz_id(quiz_id: int) -> List[Flashcard]
get_by_difficulty(quiz_id: int, difficulty: int) -> List[Flashcard]
get_by_answer_type(quiz_id: int, answer_type: str) -> List[Flashcard]
search_by_question_text(quiz_id: int, text: str) -> List[Flashcard]

update_answer_type(
    flashcard_id: int,
    answer_type: str,
    answer_options: List = None,
    answer_metadata: Dict = None
) -> Optional[Flashcard]

get_answer_type_statistics(quiz_id: int) -> Dict[str, int]
```

**Answer Type Details**:
- `integer`: Automatically sets tolerance to 0 if not specified
- `float`: Automatically sets tolerance to 0.01 if not specified
- `range`: Requires min/max in metadata
- `choice`/`multiple_choice`: Requires options list
- Invalid types default to `text` (unless `raise_on_invalid=True`)

#### SessionRepository

**Location**: `core/db/crud/repository/session_repository.py`

**Features**:
- Session creation (learn and test modes)
- Session retrieval by user, quiz, mode
- Date range queries
- Best score tracking
- Session statistics (total, average, counts)
- Recent sessions with ordering

**Key Methods**:
```python
create_session(
    user_id: int,
    quiz_id: int,
    mode: str,
    score: int = None
) -> Session

get_by_user_id(user_id: int) -> List[Session]
get_by_quiz_id(quiz_id: int) -> List[Session]
get_by_mode(user_id: int, mode: str) -> List[Session]
get_recent_sessions(user_id: int, limit: int = 10) -> List[Session]

get_sessions_by_date_range(
    user_id: int,
    start_date: datetime,
    end_date: datetime = None
) -> List[Session]

get_sessions_by_quiz_and_mode(
    quiz_id: int,
    mode: str
) -> List[Session]

get_user_quiz_sessions(user_id: int, quiz_id: int) -> List[Session]
get_sessions_since_date(user_id: int, since_date: datetime) -> List[Session]
get_best_test_scores(user_id: int, quiz_id: int = None) -> List[Session]

get_session_statistics(user_id: int) -> Dict
# Returns:
# {
#   "total_sessions": int,
#   "learn_sessions": int,
#   "test_sessions": int,
#   "average_score": float,
#   "best_score": int,
#   "unique_quizzes": int,
#   "sessions_this_week": int,
#   "sessions_this_month": int
# }
```

### Service Layer

Services implement business logic and coordinate between repositories.

#### QuizService

**Location**: `core/services/quiz_service.py`

**Responsibilities**:
- Quiz and flashcard management
- JSON import/export
- Quiz statistics
- Coordinates QuizRepository and FlashcardRepository

**Key Methods**:
```python
def __init__(self, db: Session):
    self.quiz_repo = QuizRepository(db)
    self.flashcard_repo = FlashcardRepository(db)

get_all_quizzes() -> List[Quiz]
get_quiz_by_id(quiz_id: int) -> Quiz
get_quiz_with_flashcards(quiz_id: int) -> Quiz
create_quiz(name: str, subject: str = None, description: str = None) -> Quiz
delete_quiz(quiz_id: int) -> bool
get_flashcards_for_quiz(quiz_id: int) -> List[Flashcard]
import_quiz_from_json(file_path: str) -> Quiz
export_quiz_to_json(quiz_id: int, output_path: str) -> None
get_quiz_statistics(quiz_id: int) -> Dict
```

#### UserService

**Location**: `core/services/user_service.py`

**Responsibilities**:
- User and session management
- User statistics and progress tracking
- Coordinates UserRepository and SessionRepository

**Key Methods**:
```python
def __init__(self, db: Session):
    self.user_repo = UserRepository(db)
    self.session_repo = SessionRepository(db)

get_or_create_user(name: str) -> User
get_user_by_id(user_id: int) -> User
get_user_by_name(name: str) -> User
create_session(user_id: int, quiz_id: int, mode: str) -> Session
get_user_sessions(user_id: int) -> List[Session]
get_user_progress(user_id: int) -> Dict
get_recent_activity(user_id: int, limit: int = 10) -> List[Session]
```

#### AudioService

**Location**: `core/services/audio_service.py`

**Responsibilities**:
- Text-to-speech using Google TTS
- Audio playback using pygame
- Language support for any gTTS-supported language

**Key Methods**:
```python
is_available() -> bool
play_text(text: str, lang: str = "en") -> None
cleanup() -> None
```

## REST API

The REST API is built with FastAPI and provides comprehensive endpoints for all operations.

### API Documentation

- **OpenAPI Spec**: `api/openapi.yaml`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Base URL

```
Development: http://localhost:8000/api/v1
Production:  https://api.slayflashcards.com/api/v1
```

### Authentication

The API uses JWT (JSON Web Tokens) for authentication:

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'

# Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "john_doe",
    "email": "john@example.com"
  }
}

# Use token in subsequent requests
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGc..."
```

### API Endpoints

#### Health Check
- `GET /health` - Health check (no auth required)

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/refresh` - Refresh JWT token
- `GET /auth/me` - Get current authenticated user

#### Users
- `GET /users` - List all users (admin)
- `GET /users/{user_id}` - Get user by ID
- `GET /users/me` - Get current user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `GET /users/{user_id}/sessions` - Get user's sessions
- `GET /users/{user_id}/statistics` - Get user statistics
- `GET /users/leaderboard` - Get leaderboard

#### Quizzes
- `GET /quizzes` - List all quizzes (with pagination, filtering)
- `POST /quizzes` - Create new quiz
- `GET /quizzes/{quiz_id}` - Get quiz by ID
- `PUT /quizzes/{quiz_id}` - Update quiz
- `DELETE /quizzes/{quiz_id}` - Delete quiz
- `POST /quizzes/import` - Import quiz from JSON
- `GET /quizzes/{quiz_id}/export` - Export quiz to JSON
- `GET /quizzes/{quiz_id}/statistics` - Get quiz statistics
- `GET /quizzes/subjects` - List all subjects

#### Flashcards
- `GET /quizzes/{quiz_id}/flashcards` - List flashcards for quiz
- `POST /quizzes/{quiz_id}/flashcards` - Create flashcard
- `POST /quizzes/{quiz_id}/flashcards/bulk` - Bulk create flashcards
- `GET /flashcards/{flashcard_id}` - Get flashcard by ID
- `PUT /flashcards/{flashcard_id}` - Update flashcard
- `DELETE /flashcards/{flashcard_id}` - Delete flashcard
- `GET /flashcards/{flashcard_id}/validate-answer` - Validate answer

#### Sessions
- `GET /sessions` - List sessions (with filters)
- `POST /sessions` - Create new session
- `GET /sessions/{session_id}` - Get session by ID
- `PUT /sessions/{session_id}` - Update session
- `DELETE /sessions/{session_id}` - Delete session
- `GET /sessions/recent` - Get recent sessions
- `GET /sessions/best-scores` - Get best scores

### Request/Response Examples

#### Create Quiz with Flashcards

```bash
curl -X POST http://localhost:8000/api/v1/quizzes \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "French Basics",
    "subject": "French",
    "description": "Basic French vocabulary",
    "flashcards": [
      {
        "question": {
          "title": "dog",
          "text": "What is dog in French?",
          "lang": "en",
          "difficulty": 1,
          "emoji": "🐶"
        },
        "answer": {
          "text": "chien",
          "lang": "fr",
          "type": "text"
        }
      },
      {
        "question": {
          "title": "How many?",
          "text": "How many days in a week?",
          "difficulty": 1
        },
        "answer": {
          "text": "7",
          "type": "integer",
          "metadata": {"tolerance": 0}
        }
      }
    ]
  }'
```

#### Start Learning Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_id": 1,
    "mode": "learn"
  }'
```

#### Get User Statistics

```bash
curl http://localhost:8000/api/v1/users/me/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response:
{
  "user_id": 1,
  "total_sessions": 25,
  "learn_sessions": 18,
  "test_sessions": 7,
  "average_score": 85.5,
  "best_score": 100,
  "unique_quizzes": 5,
  "sessions_this_week": 8,
  "sessions_this_month": 25,
  "favorite_subject": "French",
  "total_flashcards_studied": 150
}
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Step 1: Clone Repository
```bash
git clone https://github.com/krizo/slayflashcards.git
cd slayflashcards
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python -c "from core.db.database import init_db; init_db()"
```

## CLI Usage

### Basic Commands

```bash
# Import quiz
python cli/main.py import-quiz examples/example.json

# List quizzes
python cli/main.py list-quizzes

# Start learning session
python cli/main.py learn 1

# Learning with options
python cli/main.py learn 1 --user "alice" --audio

# View progress
python cli/main.py progress --user "alice"

# Reset database
python cli/main.py reset-db
```

### CLI Features
- Interactive learning sessions
- Audio playback (TTS)
- Multi-user support
- Progress tracking
- Quiz import/export

## API Usage

### Start API Server

```bash
# Development
uvicorn api.main_api:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn api.main_api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Environment Variables

Create `.env` file:
```bash
# Database
DATABASE_URL=sqlite:///./slayflashcards.db
# DATABASE_URL=postgresql://user:pass@localhost/slayflashcards

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Development

### Project Structure

```
slayflashcards/
├── api/                          # REST API
│   ├── dependencies/             # FastAPI dependencies
│   ├── middleware/               # Custom middleware
│   ├── routes/                   # API route handlers
│   │   ├── users_route.py
│   │   ├── quizzes_route.py
│   │   ├── flashcards_route.py
│   │   └── sessions_route.py
│   ├── utils/                    # API utilities
│   ├── api_schemas.py            # Pydantic schemas
│   ├── api_config.py             # API configuration
│   ├── main_api.py               # FastAPI app
│   └── openapi.yaml              # OpenAPI specification
├── cli/                          # CLI interface
│   ├── commands/                 # CLI commands
│   └── main.py                   # CLI entry point
├── core/                         # Core business logic
│   ├── db/                       # Database layer
│   │   ├── crud/
│   │   │   └── repository/       # Repository pattern
│   │   │       ├── base_repository.py
│   │   │       ├── user_repository.py
│   │   │       ├── quiz_repository.py
│   │   │       ├── flashcard_repository.py
│   │   │       └── session_repository.py
│   │   ├── models.py             # SQLAlchemy models
│   │   └── database.py           # Database config
│   ├── services/                 # Service layer
│   │   ├── quiz_service.py
│   │   ├── user_service.py
│   │   └── audio_service.py
│   └── learning/                 # Learning session logic
├── tests/                        # Test suite
│   └── core/
│       ├── unit/                 # Unit tests (119 tests)
│       │   ├── test_user_repository.py
│       │   ├── test_quiz_repository.py
│       │   ├── test_flashcard_repository.py
│       │   └── test_session_repository.py
│       └── integration/          # Integration tests
├── examples/                     # Example quiz files
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/core/unit/test_user_repository.py

# With coverage
pytest --cov=core --cov-report=html

# Verbose output
pytest -v

# Unit tests only
pytest tests/core/unit/ -v
```

### Test Coverage

Current test coverage:
- **119 unit tests** for repositories
- **100% coverage** of repository layer
- Tests for all CRUD operations
- Tests for business logic
- Tests for edge cases and error handling

### Code Quality

The project includes comprehensive linting and code quality tools:

#### Quick Linting

Run all linters at once:
```bash
./lint.sh
```

This script runs:
- **Flake8** - PEP 8 style checker
- **Black** - Code formatter (check mode)
- **isort** - Import sorter (check mode)
- **MyPy** - Static type checker

#### Individual Linting Tools

```bash
# Format code with Black (120 char line length)
black core/ api/ --line-length=120

# Check formatting without changing files
black --check core/ api/

# Lint with Flake8
flake8 core/ api/ --max-line-length=120

# Sort imports with isort
isort core/ api/ --profile=black

# Check import sorting
isort --check-only core/ api/

# Type checking with MyPy
mypy core/ api/ --ignore-missing-imports
```

#### Configuration Files

All linting tools are configured via:
- `.flake8` - Flake8 configuration
- `.pylintrc` - Pylint configuration
- `pyproject.toml` - Black, isort, MyPy, and pytest configuration

#### Current Code Quality

- ✅ 0 Flake8 violations (down from 203)
- ✅ 100% Black formatted
- ✅ All imports properly sorted
- ✅ 119/119 tests passing

## Database Schema

### Users Table
- `id` - Primary key
- `name` - Username (unique, indexed)
- `email` - Email address (unique, indexed)
- `password_hash` - Hashed password
- `created_at` - Registration timestamp

### Quizzes Table
- `id` - Primary key
- `name` - Quiz name (indexed)
- `subject` - Subject category (indexed)
- `description` - Quiz description
- `created_at` - Creation timestamp

### Flashcards Table
- `id` - Primary key
- `quiz_id` - Foreign key to quizzes
- `question_title` - Short question
- `question_text` - Full question
- `question_lang` - Question language
- `question_difficulty` - Difficulty (1-5)
- `question_emoji` - Optional emoji
- `question_image` - Optional image path
- `answer_text` - Answer text
- `answer_lang` - Answer language
- `answer_type` - Answer type (text, integer, float, etc.)
- `answer_options` - JSON array for choice types
- `answer_metadata` - JSON object for additional data

### Sessions Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `quiz_id` - Foreign key to quizzes
- `mode` - Session mode (learn/test)
- `score` - Test score (if applicable)
- `started_at` - Session start time

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new features
4. Ensure all tests pass (`pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

- Documentation: This README
- API Docs: http://localhost:8000/docs
- Issues: https://github.com/krizo/slayflashcards/issues
- Tests: Run `pytest` to verify installation
