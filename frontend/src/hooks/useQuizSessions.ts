import { useState, useEffect } from 'react';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import { Session } from '../types';

interface UseQuizSessionsReturn {
    sessions: Session[] | null;
    isLoading: boolean;
    error: Error | null;
    refetch: () => void;
}

/**
 * Custom hook to fetch sessions for a specific quiz
 */
export function useQuizSessions(quizId: number | null, limit: number = 10): UseQuizSessionsReturn {
    const { accessToken } = useAuth();
    const [sessions, setSessions] = useState<Session[] | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<Error | null>(null);
    const [refetchTrigger, setRefetchTrigger] = useState<number>(0);

    const refetch = () => {
        setRefetchTrigger(prev => prev + 1);
    };

    useEffect(() => {
        const fetchSessions = async () => {
            if (!quizId || !accessToken) {
                setSessions(null);
                setIsLoading(false);
                return;
            }

            setIsLoading(true);
            setError(null);

            try {
                const data = await api.get<Session[]>(
                    `/sessions/`,
                    accessToken,
                    { quiz_id: quizId, limit }
                );
                setSessions(data);
            } catch (err) {
                console.error('Failed to fetch quiz sessions:', err);
                setError(err instanceof Error ? err : new Error('Failed to fetch quiz sessions'));
                setSessions(null);
            } finally {
                setIsLoading(false);
            }
        };

        fetchSessions();
    }, [quizId, limit, accessToken, refetchTrigger]);

    return {
        sessions,
        isLoading,
        error,
        refetch,
    };
}
