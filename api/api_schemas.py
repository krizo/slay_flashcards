"""
Pydantic schemas for API request/response models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class SessionMode(str, Enum):
    LEARN = "learn"
    TEST = "test"


class AnswerType(str, Enum):
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    RANGE = "range"
    BOOLEAN = "boolean"
    CHOICE = "choice"
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_TEXT = "short_text"


class AnswerEvaluation(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[Any]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool


# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=100, description="User name")


class UserCreate(UserBase):
    """User creation schema."""
    pass


class UserUpdate(BaseModel):
    """User update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class User(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None


class UserStats(BaseModel):
    """User statistics schema."""
    total_sessions: int
    learn_sessions: int
    test_sessions: int
    average_score: Optional[float]
    best_score: Optional[int]
    study_streak: int
    favorite_subjects: List[Dict[str, Any]]
    sessions_this_week: int
    sessions_this_month: int
    unique_quizzes: int


class UserResponse(BaseResponse):
    """User response with data."""
    data: User


class UsersResponse(BaseResponse):
    """Multiple users response."""
    data: List[User]


class UserStatsResponse(BaseResponse):
    """User statistics response."""
    data: UserStats


# =============================================================================
# QUIZ SCHEMAS
# =============================================================================

class QuizBase(BaseModel):
    """Base quiz schema."""
    name: str = Field(..., min_length=1, max_length=200, description="Quiz name")
    subject: Optional[str] = Field(None, max_length=100, description="Quiz subject")
    description: Optional[str] = Field(None, max_length=1000, description="Quiz description")


class QuizCreate(QuizBase):
    """Quiz creation schema."""
    pass


class QuizUpdate(BaseModel):
    """Quiz update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    subject: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class Quiz(QuizBase):
    """Quiz response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    flashcard_count: Optional[int] = None


class QuizStats(BaseModel):
    """Quiz statistics schema."""
    total_cards: int
    difficulty_distribution: Dict[int, int]
    question_languages: Dict[str, int]
    answer_languages: Dict[str, int]
    answer_types: Dict[str, int]
    subject: Optional[str]
    created_at: datetime
    description: Optional[str]


class QuizImportData(BaseModel):
    """Quiz import data schema."""
    quiz: Dict[str, Any] = Field(..., description="Quiz metadata")
    flashcards: List[Dict[str, Any]] = Field(..., description="Flashcard data")


class QuizResponse(BaseResponse):
    """Quiz response with data."""
    data: Quiz


class QuizzesResponse(BaseResponse):
    """Multiple quizzes response."""
    data: List[Quiz]


class QuizStatsResponse(BaseResponse):
    """Quiz statistics response."""
    data: QuizStats


# =============================================================================
# FLASHCARD SCHEMAS
# =============================================================================

class FlashcardQuestionBase(BaseModel):
    """Base flashcard question schema."""
    title: str = Field(..., min_length=1, max_length=500)
    text: str = Field(..., min_length=1, max_length=2000)
    lang: Optional[str] = Field(None, max_length=10)
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    emoji: Optional[str] = Field(None, max_length=10)
    image: Optional[str] = Field(None, max_length=500)


class FlashcardAnswerBase(BaseModel):
    """Base flashcard answer schema."""
    text: str = Field(..., min_length=1, max_length=2000)
    lang: Optional[str] = Field(None, max_length=10)
    type: AnswerType = Field(default=AnswerType.TEXT)
    options: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class FlashcardBase(BaseModel):
    """Base flashcard schema."""
    quiz_id: int
    question: FlashcardQuestionBase
    answer: FlashcardAnswerBase


class FlashcardCreate(FlashcardBase):
    """Flashcard creation schema."""
    pass


class FlashcardUpdate(BaseModel):
    """Flashcard update schema."""
    question: Optional[FlashcardQuestionBase] = None
    answer: Optional[FlashcardAnswerBase] = None


class Flashcard(BaseModel):
    """Flashcard response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    question_title: str
    question_text: str
    question_lang: Optional[str]
    question_difficulty: Optional[int]
    question_emoji: Optional[str]
    question_image: Optional[str]
    answer_text: str
    answer_lang: Optional[str]
    answer_type: str
    answer_options: Optional[List[Dict[str, Any]]]
    answer_metadata: Optional[Dict[str, Any]]


class FlashcardResponse(BaseResponse):
    """Flashcard response with data."""
    data: Flashcard


class FlashcardsResponse(BaseResponse):
    """Multiple flashcards response."""
    data: List[Flashcard]


# =============================================================================
# SESSION SCHEMAS
# =============================================================================

class SessionBase(BaseModel):
    """Base session schema."""
    user_id: int
    quiz_id: int
    mode: SessionMode


class SessionCreate(SessionBase):
    """Session creation schema."""
    score: Optional[int] = Field(None, ge=0, le=100)


class SessionUpdate(BaseModel):
    """Session update schema."""
    score: Optional[int] = Field(None, ge=0, le=100)
    completed_at: Optional[datetime] = None


class Session(SessionBase):
    """Session response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    started_at: datetime
    score: Optional[int]
    completed_at: Optional[datetime] = None


class SessionStats(BaseModel):
    """Session statistics schema."""
    total_sessions: int
    learn_sessions: int
    test_sessions: int
    average_score: Optional[float]
    best_score: Optional[int]
    unique_quizzes: int
    sessions_this_week: int
    sessions_this_month: int


class SessionResponse(BaseResponse):
    """Session response with data."""
    data: Session


class SessionsResponse(BaseResponse):
    """Multiple sessions response."""
    data: List[Session]


class SessionStatsResponse(BaseResponse):
    """Session statistics response."""
    data: SessionStats


# =============================================================================
# TEST SESSION SCHEMAS
# =============================================================================

class TestAnswer(BaseModel):
    """Test answer schema."""
    flashcard_id: int
    user_answer: str
    time_taken: Optional[float] = None


class TestSubmission(BaseModel):
    """Test submission schema."""
    session_id: int
    answers: List[TestAnswer]


class CardResult(BaseModel):
    """Card result schema."""
    flashcard_id: int
    question: str
    user_answer: str
    correct_answer: str
    evaluation: AnswerEvaluation
    score: float
    time_taken: Optional[float] = None


class TestResults(BaseModel):
    """Test results schema."""
    session_id: int
    total_questions: int
    correct: int
    partial: int
    incorrect: int
    final_score: int
    time_taken: Optional[float] = None
    breakdown: List[CardResult]


class TestResultsResponse(BaseResponse):
    """Test results response."""
    data: TestResults


# =============================================================================
# LEARNING SESSION SCHEMAS
# =============================================================================

class LearningProgress(BaseModel):
    """Learning progress schema."""
    flashcard_id: int
    reviewed: bool
    confidence: Optional[int] = Field(None, ge=1, le=5)
    time_spent: Optional[float] = None


class LearningSessionUpdate(BaseModel):
    """Learning session update schema."""
    progress: List[LearningProgress]


# =============================================================================
# AUTHENTICATION SCHEMAS
# =============================================================================

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Token data schema."""
    user_id: Optional[int] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Registration request schema."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    email: Optional[str] = Field(None, max_length=255)


class AuthResponse(BaseResponse):
    """Authentication response."""
    data: Token


# =============================================================================
# SEARCH AND FILTER SCHEMAS
# =============================================================================

class QuizFilters(BaseModel):
    """Quiz filtering parameters."""
    subject: Optional[str] = None
    name_contains: Optional[str] = None
    difficulty_min: Optional[int] = Field(None, ge=1, le=5)
    difficulty_max: Optional[int] = Field(None, ge=1, le=5)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class FlashcardFilters(BaseModel):
    """Flashcard filtering parameters."""
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    question_lang: Optional[str] = None
    answer_lang: Optional[str] = None
    answer_type: Optional[AnswerType] = None
    search_text: Optional[str] = None


class SessionFilters(BaseModel):
    """Session filtering parameters."""
    user_id: Optional[int] = None
    quiz_id: Optional[int] = None
    mode: Optional[SessionMode] = None
    score_min: Optional[int] = Field(None, ge=0, le=100)
    score_max: Optional[int] = Field(None, ge=0, le=100)
    started_after: Optional[datetime] = None
    started_before: Optional[datetime] = None


# =============================================================================
# ERROR SCHEMAS
# =============================================================================

class ErrorDetail(BaseModel):
    """Error detail schema."""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# BULK OPERATION SCHEMAS
# =============================================================================

class BulkFlashcardCreate(BaseModel):
    """Bulk flashcard creation schema."""
    quiz_id: int
    flashcards: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)


class BulkOperationResult(BaseModel):
    """Bulk operation result schema."""
    total: int
    successful: int
    failed: int
    errors: List[str] = []


class BulkOperationResponse(BaseResponse):
    """Bulk operation response."""
    data: BulkOperationResult


# =============================================================================
# ADVANCED FEATURE SCHEMAS
# =============================================================================

class ProgressData(BaseModel):
    """User progress data schema."""
    date: str
    learn_sessions: int
    test_sessions: int
    average_score: Optional[float]
    total_time_minutes: Optional[float]


class UserProgressResponse(BaseResponse):
    """User progress response."""
    data: Dict[str, Any]


class LeaderboardEntry(BaseModel):
    """Leaderboard entry schema."""
    user_id: int
    username: str
    score: float
    rank: int
    sessions_count: int


class LeaderboardResponse(BaseResponse):
    """Leaderboard response."""
    data: List[LeaderboardEntry]


class QuizPerformanceStats(BaseModel):
    """Quiz performance statistics."""
    quiz_id: int
    quiz_name: str
    total_attempts: int
    average_score: Optional[float]
    highest_score: Optional[int]
    lowest_score: Optional[int]
    completion_rate: float
    difficulty_breakdown: Dict[str, int]


class PerformanceStatsResponse(BaseResponse):
    """Performance statistics response."""
    data: QuizPerformanceStats


class StudyStreakData(BaseModel):
    """Study streak information."""
    current_streak: int
    longest_streak: int
    streak_start_date: Optional[datetime]
    last_study_date: Optional[datetime]


class StudyStreakResponse(BaseResponse):
    """Study streak response."""
    data: StudyStreakData


class DashboardSummary(BaseModel):
    """Dashboard summary data."""
    total_quizzes: int
    total_flashcards: int
    total_users: int
    total_sessions_today: int
    total_sessions_week: int
    popular_subjects: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    top_performers: List[Dict[str, Any]]


class DashboardResponse(BaseResponse):
    """Dashboard summary response."""
    data: DashboardSummary


# =============================================================================
# NOTIFICATION SCHEMAS
# =============================================================================

class NotificationCreate(BaseModel):
    """Notification creation schema."""
    user_id: int
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    type: str = Field(default="info")  # info, success, warning, error
    action_url: Optional[str] = None


class Notification(BaseModel):
    """Notification schema."""
    id: int
    user_id: int
    title: str
    message: str
    type: str
    action_url: Optional[str]
    read: bool = False
    created_at: datetime


class NotificationResponse(BaseResponse):
    """Single notification response."""
    data: Notification


class NotificationsResponse(BaseResponse):
    """Multiple notifications response."""
    data: List[Notification]


# =============================================================================
# ADVANCED QUIZ SCHEMAS
# =============================================================================

class QuizTemplate(BaseModel):
    """Quiz template schema."""
    name: str
    description: str
    category: str
    difficulty_level: int = Field(ge=1, le=5)
    estimated_time_minutes: int
    flashcard_templates: List[Dict[str, Any]]


class QuizTemplateResponse(BaseResponse):
    """Quiz template response."""
    data: QuizTemplate


class QuizAnalytics(BaseModel):
    """Comprehensive quiz analytics."""
    quiz_id: int
    total_attempts: int
    unique_users: int
    average_completion_time: Optional[float]
    score_distribution: Dict[str, int]
    difficulty_analysis: Dict[str, Any]
    common_mistakes: List[Dict[str, Any]]
    improvement_suggestions: List[str]


class QuizAnalyticsResponse(BaseResponse):
    """Quiz analytics response."""
    data: QuizAnalytics


# =============================================================================
# ADVANCED FLASHCARD SCHEMAS
# =============================================================================

class FlashcardReviewData(BaseModel):
    """Flashcard review data for spaced repetition."""
    flashcard_id: int
    user_id: int
    easiness_factor: float = Field(default=2.5, ge=1.3)
    interval_days: int = Field(default=1, ge=1)
    repetitions: int = Field(default=0, ge=0)
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None


class SpacedRepetitionUpdate(BaseModel):
    """Update for spaced repetition algorithm."""
    flashcard_id: int
    quality_response: int = Field(ge=0, le=5)  # 0=complete blackout, 5=perfect response


class FlashcardDifficulty(BaseModel):
    """Flashcard difficulty analysis."""
    flashcard_id: int
    success_rate: float
    average_response_time: Optional[float]
    common_wrong_answers: List[str]
    suggested_difficulty: int


# =============================================================================
# ACHIEVEMENT & GAMIFICATION SCHEMAS
# =============================================================================

class Achievement(BaseModel):
    """Achievement schema."""
    id: int
    name: str
    description: str
    icon: str
    category: str
    points: int
    requirement_type: str  # streak, score, sessions, etc.
    requirement_value: int
    is_hidden: bool = False


class UserAchievement(BaseModel):
    """User achievement schema."""
    id: int
    user_id: int
    achievement_id: int
    earned_at: datetime
    achievement: Achievement


class AchievementProgress(BaseModel):
    """Achievement progress schema."""
    achievement: Achievement
    current_progress: int
    required_progress: int
    percentage: float
    is_completed: bool


class UserLevel(BaseModel):
    """User level and experience schema."""
    user_id: int
    level: int
    experience_points: int
    experience_to_next_level: int
    total_experience: int


class GamificationData(BaseModel):
    """Complete gamification data for user."""
    level: UserLevel
    achievements: List[UserAchievement]
    progress: List[AchievementProgress]
    recent_rewards: List[Dict[str, Any]]
    leaderboard_rank: Optional[int]


class GamificationResponse(BaseResponse):
    """Gamification data response."""
    data: GamificationData


# =============================================================================
# COLLABORATION SCHEMAS
# =============================================================================

class QuizShare(BaseModel):
    """Quiz sharing schema."""
    quiz_id: int
    shared_by_user_id: int
    shared_with_user_id: Optional[int] = None  # None for public share
    permission_level: str = Field(default="view")  # view, edit, admin
    expires_at: Optional[datetime] = None


class QuizCollaborator(BaseModel):
    """Quiz collaborator schema."""
    user_id: int
    username: str
    permission_level: str
    added_at: datetime


class CollaborativeQuiz(BaseModel):
    """Collaborative quiz schema."""
    quiz: Quiz
    owner: User
    collaborators: List[QuizCollaborator]
    is_public: bool
    share_code: Optional[str]


# =============================================================================
# IMPORT/EXPORT ADVANCED SCHEMAS
# =============================================================================

class ImportOptions(BaseModel):
    """Import options schema."""
    merge_duplicates: bool = False
    update_existing: bool = False
    preserve_ids: bool = False
    validate_only: bool = False


class ImportResult(BaseModel):
    """Import operation result."""
    success: bool
    imported_quizzes: int
    imported_flashcards: int
    skipped_items: int
    errors: List[str]
    warnings: List[str]


class ExportOptions(BaseModel):
    """Export options schema."""
    include_statistics: bool = False
    include_user_data: bool = False
    format_version: str = "2.0"
    compression: bool = True


class BatchImportData(BaseModel):
    """Batch import data schema."""
    quizzes: List[QuizImportData]
    options: ImportOptions = ImportOptions()


# =============================================================================
# API VERSIONING SCHEMAS
# =============================================================================

class ApiVersion(BaseModel):
    """API version information."""
    version: str
    release_date: str
    status: str  # stable, beta, deprecated
    changes: List[str]
    breaking_changes: List[str] = []


class ApiVersionResponse(BaseResponse):
    """API version response."""
    data: ApiVersion


class VersionCompatibility(BaseModel):
    """Version compatibility check."""
    client_version: str
    server_version: str
    compatible: bool
    warnings: List[str] = []
    upgrade_required: bool = False


# =============================================================================
# WEBHOOK SCHEMAS
# =============================================================================

class WebhookEvent(BaseModel):
    """Webhook event schema."""
    id: str
    event_type: str  # quiz.created, test.completed, user.registered, etc.
    timestamp: datetime
    user_id: Optional[int]
    data: Dict[str, Any]


class WebhookEndpoint(BaseModel):
    """Webhook endpoint schema."""
    id: int
    url: str
    events: List[str]
    secret: str
    active: bool = True
    created_at: datetime


class WebhookDelivery(BaseModel):
    """Webhook delivery attempt."""
    id: int
    endpoint_id: int
    event_id: str
    status: str  # pending, delivered, failed
    attempts: int
    last_attempt: Optional[datetime]
    response_code: Optional[int]
    error_message: Optional[str]