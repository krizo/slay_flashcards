# Core Tests

Comprehensive test suite for the core functionality of SlayFlashcards.

## Structure

```
tests/core/
├── unit/                    # Unit tests for repositories
│   ├── test_user_repository.py
│   ├── test_quiz_repository.py
│   ├── test_flashcard_repository.py
│   └── test_session_repository.py
└── integration/             # Integration tests (future)
```

## Unit Tests

### test_user_repository.py (~400 lines)
Tests for UserRepository covering:
- **User Creation**: Validation, normalization, duplicate detection
- **User Lookup**: By ID, name, email (case-insensitive)
- **User Search**: Pattern matching for names and emails
- **User Modification**: Rename, email updates, password updates
- **User Deletion**: With cascade to sessions
- **User Activity**: Active users, most active users, registration dates
- **User Statistics**: Summary statistics across all users

**Test Classes:**
- `TestUserCreation` - 10 tests
- `TestUserLookup` - 10 tests
- `TestUserSearch` - 3 tests
- `TestUserModification` - 6 tests
- `TestUserDeletion` - 4 tests
- `TestUserActivity` - 3 tests
- `TestUserStatistics` - 1 test

### test_quiz_repository.py (~370 lines)
Tests for QuizRepository covering:
- **Quiz Creation**: With various field combinations
- **Quiz Lookup**: By ID, name, with pagination
- **Quiz Subject Management**: Get by subject, list all subjects
- **Quiz Search**: Pattern matching with ordering
- **Quiz Modification**: Update fields
- **Quiz Deletion**: With cascade to flashcards
- **Base Repository**: Bulk operations, refresh

**Test Classes:**
- `TestQuizCreation` - 5 tests
- `TestQuizLookup` - 8 tests
- `TestQuizSubject` - 4 tests
- `TestQuizSearch` - 5 tests
- `TestQuizModification` - 2 tests
- `TestQuizDeletion` - 3 tests
- `TestBaseRepositoryFunctionality` - 3 tests

### test_flashcard_repository.py (~650 lines)
Tests for FlashcardRepository covering:
- **Flashcard Creation**: All answer types (text, integer, float, choice, etc.)
- **Bulk Creation**: Multiple flashcards with different types
- **Flashcard Retrieval**: By quiz, difficulty, answer type
- **Flashcard Search**: Question text search
- **Answer Type Management**: Update types, validate types
- **Answer Type Statistics**: Count by type
- **Flashcard Modification**: Update fields
- **Flashcard Deletion**: Delete operations

**Test Classes:**
- `TestFlashcardCreation` - 10 tests
- `TestBulkFlashcardCreation` - 2 tests
- `TestFlashcardRetrieval` - 4 tests
- `TestFlashcardSearch` - 2 tests
- `TestAnswerTypeManagement` - 4 tests
- `TestAnswerTypeStatistics` - 2 tests
- `TestFlashcardModification` - 1 test
- `TestFlashcardDeletion` - 2 tests

### test_session_repository.py (~560 lines)
Tests for SessionRepository covering:
- **Session Creation**: Learn and test modes with scores
- **Session Retrieval**: By user, quiz, mode with ordering
- **Advanced Queries**: User-quiz combinations, mode filtering
- **Date Range Queries**: Sessions within time periods
- **Score Tracking**: Best scores, statistics
- **Session Statistics**: Comprehensive user activity stats
- **Session Modification**: Update scores
- **Session Deletion**: Delete operations
- **Activity Tracking**: Weekly and monthly activity

**Test Classes:**
- `TestSessionCreation` - 4 tests
- `TestSessionRetrieval` - 5 tests
- `TestSessionQueries` - 3 tests
- `TestDateRangeQueries` - 2 tests
- `TestScoreAndStatistics` - 4 tests
- `TestSessionModification` - 1 test
- `TestSessionDeletion` - 2 tests
- `TestActivityTracking` - 2 tests

## Running Tests

### Run all core tests:
```bash
pytest tests/core/
```

### Run specific repository tests:
```bash
pytest tests/core/unit/test_user_repository.py
pytest tests/core/unit/test_quiz_repository.py
pytest tests/core/unit/test_flashcard_repository.py
pytest tests/core/unit/test_session_repository.py
```

### Run specific test class:
```bash
pytest tests/core/unit/test_user_repository.py::TestUserCreation
```

### Run specific test:
```bash
pytest tests/core/unit/test_user_repository.py::TestUserCreation::test_create_user_minimal
```

### Run with coverage:
```bash
pytest tests/core/ --cov=core/db/crud/repository --cov-report=html
```

### Run with verbose output:
```bash
pytest tests/core/ -v
```

## Test Coverage

Total: **~2000 lines** of test code covering:
- ✅ 37 UserRepository tests
- ✅ 30 QuizRepository tests
- ✅ 27 FlashcardRepository tests
- ✅ 23 SessionRepository tests

**Total: 117+ unit tests**

## Key Features Tested

### Repository Pattern
- Generic CRUD operations (create, read, update, delete)
- Bulk operations
- Transaction handling
- Query builders

### Business Logic
- Input validation and normalization
- Duplicate detection
- Cascade deletion
- Case-insensitive searches
- Date range filtering
- Statistical aggregations

### Data Integrity
- Referential integrity (foreign keys)
- Unique constraints
- Required field validation
- Type validation (especially answer types)

### Advanced Features
- Answer type system (8 types supported)
- Default value generation
- Metadata handling
- Session scoring and statistics
- Activity tracking

## Test Fixtures

Tests use the `test_db` fixture from `tests/conftest.py` which provides:
- Clean database session for each test
- Automatic rollback after tests
- Isolated test environment

## Best Practices

1. **Arrange-Act-Assert**: All tests follow AAA pattern
2. **Descriptive Names**: Test names clearly describe what they test
3. **Single Responsibility**: Each test tests one thing
4. **Grouped by Feature**: Tests organized into logical classes
5. **Comprehensive Coverage**: Edge cases, errors, and happy paths
6. **No External Dependencies**: All tests are self-contained
