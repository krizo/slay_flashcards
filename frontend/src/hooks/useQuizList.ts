import { useState, useEffect } from 'react';
import { Quiz } from '../types';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

interface UseQuizListParams {
    page?: number;
    limit?: number;
    subject?: string;
    nameContains?: string;
    category?: string;
    level?: string;
}

interface UseQuizListReturn {
    quizzes: Quiz[] | null;
    isLoading: boolean;
    error: Error | null;
    refetch: () => void;
}

/**
 * Custom hook to fetch list of quizzes with filtering and pagination
 */
export function useQuizList({
    page = 1,
    limit = 100,
    subject,
    nameContains,
    category,
    level,
}: UseQuizListParams = {}): UseQuizListReturn {
    const { accessToken } = useAuth();
    const [quizzes, setQuizzes] = useState<Quiz[] | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<Error | null>(null);
    const [refetchTrigger, setRefetchTrigger] = useState<number>(0);

    useEffect(() => {
        const fetchQuizzes = async () => {
            if (!accessToken) {
                setIsLoading(false);
                return;
            }

            setIsLoading(true);
            setError(null);

            try {
                // Build query params
                const queryParams: Record<string, string | number | undefined> = {
                    page,
                    limit,
                };

                if (subject) {
                    queryParams.subject = subject;
                }

                if (nameContains) {
                    queryParams.name_contains = nameContains;
                }

                if (category) {
                    queryParams.category = category;
                }

                if (level) {
                    queryParams.level = level;
                }

                // Fetch quizzes from API
                const data = await api.get<Quiz[]>('/quizzes/', accessToken, queryParams);

                // Deduplicate quizzes by ID (in case API returns duplicates)
                const uniqueQuizzes = data.reduce((acc: Quiz[], quiz: Quiz) => {
                    if (!acc.find(q => q.id === quiz.id)) {
                        acc.push(quiz);
                    }
                    return acc;
                }, []);

                setQuizzes(uniqueQuizzes);
            } catch (err) {
                console.error('Failed to fetch quizzes:', err);
                setError(err instanceof Error ? err : new Error('Failed to fetch quizzes'));
            } finally {
                setIsLoading(false);
            }
        };

        fetchQuizzes();
    }, [accessToken, page, limit, subject, nameContains, category, level, refetchTrigger]);

    const refetch = () => {
        setRefetchTrigger((prev) => prev + 1);
    };

    return {
        quizzes,
        isLoading,
        error,
        refetch,
    };
}
