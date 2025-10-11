import { useState, useEffect } from 'react';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

interface QuizStats {
    total_sessions: number;
    test_sessions: number;
    best_score: number | null;
    average_score: number | null;
}

interface UseQuizStatsReturn {
    quizStats: QuizStats | null;
    isLoading: boolean;
    error: Error | null;
}

export function useQuizStats(quizId: number | null): UseQuizStatsReturn {
    const { accessToken, user } = useAuth();
    const [quizStats, setQuizStats] = useState<QuizStats | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (!accessToken || !user || !quizId) {
            setIsLoading(false);
            return;
        }

        const fetchQuizStats = async () => {
            try {
                setIsLoading(true);
                setError(null);

                // Fetch all sessions for this user and quiz
                const sessions = await api.get<any[]>(
                    `/sessions/`,
                    accessToken,
                    { user_id: user.id, quiz_id: quizId }
                );

                // Sort by started_at descending (most recent first)
                const sortedSessions = [...sessions].sort((a, b) =>
                    new Date(b.started_at).getTime() - new Date(a.started_at).getTime()
                );

                // Calculate stats from sessions
                const testSessions = sessions.filter(s => s.mode === 'test');
                const completedSessions = sessions.filter(s => s.completed_at && s.score !== null);

                const bestScore = completedSessions.length > 0
                    ? Math.max(...completedSessions.map(s => s.score))
                    : null;

                const averageScore = completedSessions.length > 0
                    ? completedSessions.reduce((sum, s) => sum + s.score, 0) / completedSessions.length
                    : null;

                setQuizStats({
                    total_sessions: sessions.length,
                    test_sessions: testSessions.length,
                    best_score: bestScore,
                    average_score: averageScore,
                });
            } catch (err) {
                setError(err as Error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchQuizStats();
    }, [accessToken, user, quizId]);

    return { quizStats, isLoading, error };
}
