import { useState, useEffect } from 'react';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

interface UseQuizSubjectsReturn {
    subjects: string[] | null;
    isLoading: boolean;
    error: Error | null;
}

/**
 * Custom hook to fetch available quiz subjects
 */
export function useQuizSubjects(): UseQuizSubjectsReturn {
    const { accessToken } = useAuth();
    const [subjects, setSubjects] = useState<string[] | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchSubjects = async () => {
            if (!accessToken) {
                setIsLoading(false);
                return;
            }

            setIsLoading(true);
            setError(null);

            try {
                // Fetch subjects from API
                const data = await api.get<string[]>('/quizzes/subjects', accessToken);
                setSubjects(data);
            } catch (err) {
                console.error('Failed to fetch quiz subjects:', err);
                setError(err instanceof Error ? err : new Error('Failed to fetch quiz subjects'));
            } finally {
                setIsLoading(false);
            }
        };

        fetchSubjects();
    }, [accessToken]);

    return {
        subjects,
        isLoading,
        error,
    };
}
