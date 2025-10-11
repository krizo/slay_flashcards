import { useState, useEffect } from 'react';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import { Quiz } from '../types';

interface UseQuizFiltersReturn {
    subjects: string[] | null;
    categories: string[] | null;
    levels: string[] | null;
    isLoading: boolean;
    error: Error | null;
}

/**
 * Custom hook to fetch all available quiz filter options
 */
export function useQuizFilters(): UseQuizFiltersReturn {
    const { accessToken } = useAuth();
    const [subjects, setSubjects] = useState<string[] | null>(null);
    const [categories, setCategories] = useState<string[] | null>(null);
    const [levels, setLevels] = useState<string[] | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchFilters = async () => {
            if (!accessToken) {
                setIsLoading(false);
                return;
            }

            setIsLoading(true);
            setError(null);

            try {
                // Fetch subjects from dedicated endpoint
                const subjectsResponse = await api.get<{ [key: string]: number }>('/quizzes/subjects', accessToken);

                // Extract subject names (keys from the dictionary)
                const subjectNames = Object.keys(subjectsResponse).sort();

                // Fetch all quizzes to extract unique categories and levels
                const quizzesData = await api.get<Quiz[]>('/quizzes/', accessToken, { limit: 100 });

                // Extract unique categories (excluding null/undefined)
                const uniqueCategories = [...new Set(
                    quizzesData
                        .map(quiz => quiz.category)
                        .filter((cat): cat is string => cat !== null && cat !== undefined)
                )].sort();

                // Extract unique levels (excluding null/undefined)
                const uniqueLevels = [...new Set(
                    quizzesData
                        .map(quiz => quiz.level)
                        .filter((level): level is string => level !== null && level !== undefined)
                )].sort();

                setSubjects(subjectNames);
                setCategories(uniqueCategories);
                setLevels(uniqueLevels);
            } catch (err) {
                console.error('Failed to fetch quiz filters:', err);
                setError(err instanceof Error ? err : new Error('Failed to fetch quiz filters'));
            } finally {
                setIsLoading(false);
            }
        };

        fetchFilters();
    }, [accessToken]);

    return {
        subjects,
        categories,
        levels,
        isLoading,
        error,
    };
}
