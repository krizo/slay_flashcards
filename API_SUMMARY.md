# SlayFlashcards API - OpenAPI Schema Summary

**Generated:** 1.0.0
**Title:** SlayFlashcards API
**Description:** REST API for SlayFlashcards - An interactive flashcard learning platform

## Statistics

- **Total Endpoints:** 48
- **Total Schemas:** 49
- **OpenAPI Version:** 3.1.0

## Endpoint Categories

### Authentication (6 endpoints)
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/login - User login
- POST /api/v1/auth/refresh - Refresh access token
- POST /api/v1/auth/logout - User logout
- GET /api/v1/auth/me - Get current user info
- GET /api/v1/auth/verify - Verify authentication

### Users (10 endpoints)
- GET /api/v1/users/ - List all users
- POST /api/v1/users/ - Create new user
- GET /api/v1/users/{user_id} - Get user by ID
- PUT /api/v1/users/{user_id} - Update user
- DELETE /api/v1/users/{user_id} - Delete user
- GET /api/v1/users/name/{username} - Get user by username
- POST /api/v1/users/ensure - Ensure user exists
- GET /api/v1/users/search - Search users
- GET /api/v1/users/{user_id}/statistics - Get user stats
- GET /api/v1/users/{user_id}/progress - Get user progress
- GET /api/v1/users/leaderboard - Get leaderboard

### Quizzes (12 endpoints)
- GET /api/v1/quizzes/ - List all quizzes
- POST /api/v1/quizzes/ - Create quiz
- GET /api/v1/quizzes/{quiz_id} - Get quiz by ID
- PUT /api/v1/quizzes/{quiz_id} - Update quiz
- DELETE /api/v1/quizzes/{quiz_id} - Delete quiz
- POST /api/v1/quizzes/import - Import quiz from JSON
- POST /api/v1/quizzes/import-file - Import quiz from file upload
- GET /api/v1/quizzes/{quiz_id}/export - Export quiz to JSON
- GET /api/v1/quizzes/search - Search quizzes
- GET /api/v1/quizzes/subjects - Get all subjects
- GET /api/v1/quizzes/{quiz_id}/statistics - Get quiz statistics
- POST /api/v1/quizzes/{quiz_id}/duplicate - Duplicate quiz

### Flashcards (9 endpoints)
- GET /api/v1/flashcards/ - List flashcards (with quiz_id filter)
- POST /api/v1/flashcards/ - Create flashcard
- GET /api/v1/flashcards/{flashcard_id} - Get flashcard
- PUT /api/v1/flashcards/{flashcard_id} - Update flashcard
- DELETE /api/v1/flashcards/{flashcard_id} - Delete flashcard
- POST /api/v1/flashcards/bulk - Bulk create flashcards
- GET /api/v1/flashcards/quiz/{quiz_id}/random - Get random flashcards
- GET /api/v1/flashcards/quiz/{quiz_id}/types - Get answer type statistics

### Sessions (10 endpoints)
- GET /api/v1/sessions/ - List sessions
- POST /api/v1/sessions/ - Create session
- GET /api/v1/sessions/{session_id} - Get session
- PUT /api/v1/sessions/{session_id} - Update session
- DELETE /api/v1/sessions/{session_id} - Delete session
- POST /api/v1/sessions/test/submit - Submit test answers
- PUT /api/v1/sessions/learning/{session_id}/progress - Update learning progress
- GET /api/v1/sessions/user/{user_id}/recent - Get recent sessions
- GET /api/v1/sessions/statistics - Get session statistics
- GET /api/v1/sessions/quiz/{quiz_id}/performance - Get quiz performance

### Health (1 endpoint)
- GET /health - Health check

## Key Features

✅ **Complete Request/Response Schemas** - All endpoints have properly defined request and response schemas
✅ **Type Safety** - Enhanced answer types (text, integer, float, range, boolean, choice, multiple_choice, short_text)
✅ **Authentication** - JWT-based authentication with refresh tokens
✅ **Validation** - Pydantic validation with 422 error responses
✅ **Pagination** - Support for paginated responses
✅ **Search & Filter** - Search and filter capabilities for quizzes and users
✅ **Statistics** - Comprehensive statistics and progress tracking
✅ **Import/Export** - JSON import/export for quizzes

## Usage

View the OpenAPI documentation:
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## File Location

`openapi.json` - Complete OpenAPI 3.1.0 specification
