import { useState, useEffect } from 'react';
import { apiClient } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import { UserStats, Session, ProgressDataPoint, User } from '../types';

// Generic hook return type
interface UseApiResult<T> {
    data: T | null;
    isLoading: boolean;
    error: Error | null;
}

/**
 * Hook to fetch current user information
 * Fetches from GET /api/v1/auth/me
 */
export function useCurrentUser(): UseApiResult<User> {
    const { accessToken } = useAuth();
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const data = await apiClient<User>('/auth/me', undefined, accessToken);
                setUser(data);
            } catch (err) {
                setError(err instanceof Error ? err : new Error('Failed to fetch user information'));
            } finally {
                setIsLoading(false);
            }
        };

        if (accessToken) {
            fetchUser();
        } else {
            setIsLoading(false);
        }
    }, [accessToken]);

    return { data: user, isLoading, error };
}

/**
 * Hook to fetch user statistics
 * Fetches from GET /api/v1/users/{userId}/statistics
 */
export function useUserStats(userId: number): UseApiResult<UserStats> {
    const { accessToken } = useAuth();
    const [stats, setStats] = useState<UserStats | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const data = await apiClient<UserStats>(`/users/${userId}/statistics`, undefined, accessToken);
                setStats(data);
            } catch (err) {
                setError(err instanceof Error ? err : new Error('Failed to fetch user statistics'));
            } finally {
                setIsLoading(false);
            }
        };

        if (accessToken) {
            fetchStats();
        } else {
            setIsLoading(false);
        }
    }, [userId, accessToken]);

    return { data: stats, isLoading, error };
}

/**
 * Hook to fetch recent sessions for a user
 * Fetches from GET /api/v1/sessions/user/{userId}/recent?limit=4
 */
export function useRecentSessions(userId: number, limit: number = 5): UseApiResult<Session[]> {
    const { accessToken } = useAuth();
    const [sessions, setSessions] = useState<Session[] | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const data = await apiClient<Session[]>(`/sessions/user/${userId}/recent?limit=${limit}`, undefined, accessToken);
                setSessions(data);
            } catch (err) {
                setError(err instanceof Error ? err : new Error('Failed to fetch recent sessions'));
            } finally {
                setIsLoading(false);
            }
        };

        if (accessToken) {
            fetchSessions();
        } else {
            setIsLoading(false);
        }
    }, [userId, limit, accessToken]);

    return { data: sessions, isLoading, error };
}

// API response format for progress endpoint
interface ProgressApiResponse {
    total_sessions: number;
    learn_sessions: number;
    test_sessions: number;
    days_analyzed: number;
    quiz_filter: number | null;
    daily_activity: {
        [date: string]: {
            learn_sessions: number;
            test_sessions: number;
            scores: number[];
            average_score: number;
        };
    };
}

/**
 * Hook to fetch user progress data for charts
 * Fetches from GET /api/v1/users/{userId}/progress?days=30
 * Transforms the API response into chart-ready data
 */
export function useProgressData(userId: number, days: number = 7): UseApiResult<ProgressDataPoint[]> {
    const { accessToken } = useAuth();
    const [progress, setProgress] = useState<ProgressDataPoint[] | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchProgress = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const data = await apiClient<ProgressApiResponse>(`/users/${userId}/progress?days=${days}`, undefined, accessToken);

                // Transform the API response into chart data format
                const chartData: ProgressDataPoint[] = Object.entries(data.daily_activity)
                    .map(([date, activity]) => ({
                        date,
                        score: activity.average_score || 0
                    }))
                    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

                setProgress(chartData);
            } catch (err) {
                setError(err instanceof Error ? err : new Error('Failed to fetch progress data'));
            } finally {
                setIsLoading(false);
            }
        };

        if (accessToken) {
            fetchProgress();
        } else {
            setIsLoading(false);
        }
    }, [userId, days, accessToken]);

    return { data: progress, isLoading, error };
}
