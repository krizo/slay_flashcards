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
    best_score: number | null;
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
    score: number | null;
    completed_at: string | null;
    // Add field for quiz name for readability in Dashboard (Quiz Name)
    quiz_name?: string;
}

// Interface for chart data (Progress)
export interface ProgressDataPoint {
    date: string; // e.g. YYYY-MM-DD
    score: number; // Average score for the given day
}
