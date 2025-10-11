import { useState, useEffect } from 'react';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import { Session } from '../types';

interface UseRecentSessionsReturn {
    sessions: Session[];
    lastSessionDate: string | null;
    isLoading: boolean;
    error: Error | null;
}

export function useRecentSessions(limit: number = 5): UseRecentSessionsReturn {
    const { accessToken, user } = useAuth();
    const [sessions, setSessions] = useState<Session[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (!accessToken || !user) {
            setIsLoading(false);
            return;
        }

        const fetchSessions = async () => {
            try {
                setIsLoading(true);
                setError(null);
                // Fetch more sessions to ensure we get previous one
                const data = await api.get<Session[]>(
                    `/sessions/`,
                    accessToken,
                    { user_id: user.id, limit: 50 }
                );
                // Sort by started_at descending (most recent first)
                const sorted = [...data].sort((a, b) =>
                    new Date(b.started_at).getTime() - new Date(a.started_at).getTime()
                );
                setSessions(sorted);
            } catch (err) {
                setError(err as Error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchSessions();
    }, [accessToken, user, limit]);

    // Get second session (index 1) to skip the current one that just started
    const lastSessionDate = sessions.length > 1 && sessions[1].started_at
        ? sessions[1].started_at
        : (sessions.length === 1 ? null : null);

    console.log('useRecentSessions returning lastSessionDate:', lastSessionDate);

    return { sessions, lastSessionDate, isLoading, error };
}
