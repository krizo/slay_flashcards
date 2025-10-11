import { useState, useEffect } from 'react';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import { UserStats } from '../types';

interface UseUserStatsReturn {
    stats: UserStats | null;
    isLoading: boolean;
    error: Error | null;
}

export function useUserStats(): UseUserStatsReturn {
    const { accessToken, user } = useAuth();
    const [stats, setStats] = useState<UserStats | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (!accessToken || !user) {
            setIsLoading(false);
            return;
        }

        const fetchStats = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const data = await api.get<UserStats>(
                    `/users/${user.id}/statistics`,
                    accessToken
                );
                setStats(data);
            } catch (err) {
                setError(err as Error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchStats();
    }, [accessToken, user]);

    return { stats, isLoading, error };
}
