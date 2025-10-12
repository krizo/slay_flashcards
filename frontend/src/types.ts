export type AnswerType = 'text' | 'integer' | 'float' | 'range' | 'boolean' | 'choice' | 'multiple_choice' | 'short_text';

export type FlashcardMode = 'learn' | 'test';

export interface QuestionData {
    title: string;
    text: string;
    lang?: string | null;
    difficulty: number;
    emoji: string;
    image: string | null;
}

export interface AnswerData {
    text: string;
    lang?: string | null;
    type: AnswerType;
    options: string[] | null;
    metadata: Record<string, any> | null;
}

export interface FlashcardData {
    id: number;
    quiz_id: number;
    question: QuestionData;
    answer: AnswerData;
}

// Based on 'User' schema
export interface User {
    id: number;
    name: string;
    email: string | null;
    created_at: string | null;
}

// Based on 'UserStats' schema
export interface UserStats {
    total_sessions: number;
    learn_sessions: number;
    test_sessions: number;
    average_score: number | null;
    best_score: number | null;  // Float value to match API
    study_streak: number;
    favorite_subjects: { [key: string]: number }[]; // Simplified type
    sessions_this_week: number;
    sessions_this_month: number;
    unique_quizzes: number;
}

// Based on 'Session' schema (for Recent Activity)
export type SessionMode = 'learn' | 'test';

export interface Session {
    id: number;
    user_id: number;
    quiz_id: number;
    mode: SessionMode;
    started_at: string;
    score: number | null;  // Float value to match API
    completed_at: string | null;
    completed: boolean;  // Session completion status
    // Quiz details for display in Dashboard
    quiz_name?: string;
    quiz_category?: string | null;
    quiz_level?: string | null;
}

// Interface for chart data (Progress)
export interface ProgressDataPoint {
    date: string; // e.g. YYYY-MM-DD
    score: number; // Average score for the given day
}

// Quiz interface for quiz management
export interface Quiz {
    id: number;
    name: string;
    subject: string;
    category?: string | null;
    level?: string | null;
    description: string | null;
    user_id: number;
    flashcard_count?: number;
    created_at?: string;
    updated_at?: string;
    favourite: boolean;
    image?: string | null;  // Base64 encoded image data
}

// Request/Response types for Quiz operations
export interface QuizCreateRequest {
    name: string;
    subject: string;
    description?: string | null;
    favourite?: boolean;
    image?: string | null;
}

export interface QuizUpdateRequest {
    name?: string;
    subject?: string;
    description?: string | null;
    favourite?: boolean;
    image?: string | null;
}

export interface QuizListResponse {
    quizzes: Quiz[];
    total: number;
    page: number;
    limit: number;
}

// Session-related types for learning/test sessions
export interface SessionProgress {
    flashcard_id: number;
    user_answer: string;
    is_correct?: boolean;
    feedback?: string;
}

export interface SessionFeedback {
    is_correct: boolean;
    correct_answer: string;
    feedback: string;
}

export interface SessionCreateRequest {
    quiz_id: number;
    mode: SessionMode;
}

export interface SessionCreateResponse {
    id: number;
    user_id: number;
    quiz_id: number;
    mode: SessionMode;
    started_at: string;
    score: number | null;
    completed_at: string | null;
    completed: boolean;
}

// Test mode result types
export interface TestAnswerBreakdown {
    flashcard_id: number;
    question: string;
    user_answer: string;
    correct_answer: string;
    evaluation: 'correct' | 'incorrect';
}

export interface TestResult {
    final_score: number;
    correct: number;
    total: number;
    breakdown: TestAnswerBreakdown[];
    duration?: number; // Total test duration in seconds
}

export interface TestSubmitRequest {
    session_id: number;
    answers: {
        flashcard_id: number;
        user_answer: string;
        time_taken?: number;
    }[];
    duration?: number; // Total test duration in seconds
}
