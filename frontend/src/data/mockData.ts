import { UserStats, Session, ProgressDataPoint } from '../types';

// Mock user statistics for Dashboard
export const mockUserStats: UserStats = {
    total_sessions: 350,
    learn_sessions: 280,
    test_sessions: 70,
    average_score: 82,
    best_score: 95,
    study_streak: 12,
    favorite_subjects: [{ French: 50 }, { React: 30 }],
    sessions_this_week: 15,
    sessions_this_month: 60,
    unique_quizzes: 15,
};

// Mock recent sessions for Recent Activity
export const mockRecentSessions: Session[] = [
    {
        id: 1,
        user_id: 1,
        quiz_id: 8,
        mode: 'learn',
        started_at: '2025-10-08T10:30:00Z',
        score: 85,
        completed_at: '2025-10-08T10:45:00Z',
        quiz_name: 'French Vocabulary',
    },
    {
        id: 2,
        user_id: 1,
        quiz_id: 12,
        mode: 'test',
        started_at: '2025-10-08T09:00:00Z',
        score: 92,
        completed_at: '2025-10-08T09:20:00Z',
        quiz_name: 'React Fundamentals',
    },
    {
        id: 3,
        user_id: 1,
        quiz_id: 5,
        mode: 'learn',
        started_at: '2025-10-07T15:00:00Z',
        score: 78,
        completed_at: '2025-10-07T15:30:00Z',
        quiz_name: 'JavaScript Basics',
    },
    {
        id: 4,
        user_id: 1,
        quiz_id: 3,
        mode: 'test',
        started_at: '2025-10-07T11:00:00Z',
        score: 88,
        completed_at: '2025-10-07T11:25:00Z',
        quiz_name: 'TypeScript Advanced',
    },
    {
        id: 5,
        user_id: 1,
        quiz_id: 9,
        mode: 'learn',
        started_at: '2025-10-06T14:00:00Z',
        score: 75,
        completed_at: '2025-10-06T14:20:00Z',
        quiz_name: 'Python Basics',
    },
];

// Mock progress data for chart (last 7 days)
export const mockProgressData: ProgressDataPoint[] = [
    { date: '2025-10-02', score: 75 },
    { date: '2025-10-03', score: 78 },
    { date: '2025-10-04', score: 80 },
    { date: '2025-10-05', score: 82 },
    { date: '2025-10-06', score: 79 },
    { date: '2025-10-07', score: 85 },
    { date: '2025-10-08', score: 88 },
];

// Mock trending quizzes data
export interface TrendingQuiz {
    id: number;
    name: string;
    emoji: string;
    popularity: number;
}

export const mockTrendingQuizzes: TrendingQuiz[] = [
    { id: 1, name: 'French Vocabulary', emoji: '🇫🇷', popularity: 95 },
    { id: 2, name: 'React Fundamentals', emoji: '⚛️', popularity: 88 },
    { id: 3, name: 'JavaScript Basics', emoji: '💻', popularity: 82 },
    { id: 4, name: 'TypeScript Advanced', emoji: '📘', popularity: 75 },
];
