import { useState, useEffect } from 'react';
import { Quiz } from '../types';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

interface UseQuizReturn {
    quiz: Quiz | null;
    isLoading: boolean;
    error: Error | null;
    refetch: () => void;
}

/**
 * Custom hook to fetch a single quiz by ID
 */
export function useQuiz(quizId: number | null): UseQuizReturn {
    const { accessToken } = useAuth();
    const [quiz, setQuiz] = useState<Quiz | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<Error | null>(null);
    const [refetchTrigger, setRefetchTrigger] = useState<number>(0);

    useEffect(() => {
        const fetchQuiz = async () => {
            // Don't fetch if quizId is null or no access token
            if (quizId === null || !accessToken) {
                setQuiz(null);
                setIsLoading(false);
                return;
            }

            setIsLoading(true);
            setError(null);

            try {
                // Fetch quiz from API
                const data = await api.get<Quiz>(`/quizzes/${quizId}`, accessToken);
                setQuiz(data);
            } catch (err) {
                console.error(`Failed to fetch quiz ${quizId}:`, err);
                setError(err instanceof Error ? err : new Error('Failed to fetch quiz'));
                setQuiz(null);
            } finally {
                setIsLoading(false);
            }
        };

        fetchQuiz();
    }, [accessToken, quizId, refetchTrigger]);

    const refetch = () => {
        setRefetchTrigger((prev) => prev + 1);
    };

    return {
        quiz,
        isLoading,
        error,
        refetch,
    };
}
