import { useState, useEffect } from 'react';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

interface QuizPerformanceData {
    quiz_id: number;
    quiz_name: string;
    total_sessions: number;
    test_sessions: number;
    learn_sessions: number;
    unique_users: number;
    days_analyzed: number;
    scores: {
        average: number | null;
        highest: number | null;
        lowest: number | null;
        distribution: {
            '90-100': number;
            '80-89': number;
            '70-79': number;
            '60-69': number;
            '50-59': number;
            '0-49': number;
        };
    };
    activity_trend: {
        [date: string]: {
            sessions: number;
            average_score: number | null;
        };
    };
}

interface UseQuizPerformanceReturn {
    performance: QuizPerformanceData | null;
    isLoading: boolean;
    error: Error | null;
    refetch: () => void;
}

/**
 * Custom hook to fetch quiz performance statistics
 */
export function useQuizPerformance(quizId: number | null, days: number = 30): UseQuizPerformanceReturn {
    const { accessToken } = useAuth();
    const [performance, setPerformance] = useState<QuizPerformanceData | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<Error | null>(null);
    const [refetchTrigger, setRefetchTrigger] = useState<number>(0);

    const refetch = () => {
        setRefetchTrigger(prev => prev + 1);
    };

    useEffect(() => {
        const fetchPerformance = async () => {
            if (!quizId || !accessToken) {
                setPerformance(null);
                setIsLoading(false);
                return;
            }

            setIsLoading(true);
            setError(null);

            try {
                const data = await api.get<QuizPerformanceData>(
                    `/sessions/quiz/${quizId}/performance`,
                    accessToken,
                    { days }
                );
                setPerformance(data);
            } catch (err) {
                console.error('Failed to fetch quiz performance:', err);
                setError(err instanceof Error ? err : new Error('Failed to fetch quiz performance'));
                setPerformance(null);
            } finally {
                setIsLoading(false);
            }
        };

        fetchPerformance();
    }, [quizId, days, accessToken, refetchTrigger]);

    return {
        performance,
        isLoading,
        error,
        refetch,
    };
}
