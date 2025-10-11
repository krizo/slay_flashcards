import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useQuizSessions } from './useQuizSessions';
import { api } from '../services/apiClient';

// Mock the apiClient module
vi.mock('../services/apiClient', () => ({
    api: {
        get: vi.fn(),
    },
}));

// Mock the AuthContext module
vi.mock('../context/AuthContext', () => ({
    useAuth: () => ({
        accessToken: 'mock-access-token',
        user: { id: 1, email: 'test@example.com', name: 'Test User' },
        isLoading: false,
        isAuthenticated: true,
        login: vi.fn(),
        register: vi.fn(),
        logout: vi.fn(),
    }),
}));

describe('useQuizSessions', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.resetAllMocks();
    });

    it('should fetch and return quiz sessions successfully', async () => {
        const mockSessions = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'test' as const,
                started_at: '2025-10-11T10:00:00.000Z',
                completed_at: '2025-10-11T10:30:00.000Z',
                score: 95.5,
            },
            {
                id: 2,
                user_id: 1,
                quiz_id: 5,
                mode: 'learn' as const,
                started_at: '2025-10-10T14:00:00.000Z',
                completed_at: '2025-10-10T14:45:00.000Z',
                score: null,
            },
        ];

        vi.mocked(api.get).mockResolvedValueOnce(mockSessions);

        const { result } = renderHook(() => useQuizSessions(5, 10));

        expect(result.current.isLoading).toBe(true);
        expect(result.current.sessions).toBe(null);

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.sessions).toEqual(mockSessions);
        expect(result.current.error).toBe(null);
        expect(api.get).toHaveBeenCalledWith(
            '/sessions/',
            'mock-access-token',
            { quiz_id: 5, limit: 10 }
        );
    });

    it('should handle error when fetching sessions fails', async () => {
        const mockError = new Error('Failed to fetch quiz sessions');
        vi.mocked(api.get).mockRejectedValueOnce(mockError);

        const { result } = renderHook(() => useQuizSessions(5, 10));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.sessions).toBe(null);
        expect(result.current.error).toEqual(mockError);
    });

    it('should not fetch when quizId is null', async () => {
        const { result } = renderHook(() => useQuizSessions(null, 10));

        expect(result.current.isLoading).toBe(false);
        expect(result.current.sessions).toBe(null);
        expect(result.current.error).toBe(null);
        expect(api.get).not.toHaveBeenCalled();
    });

    it('should use default limit of 10 when not provided', async () => {
        const mockSessions = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'test' as const,
                started_at: '2025-10-11T10:00:00.000Z',
                completed_at: '2025-10-11T10:30:00.000Z',
                score: 85.0,
            },
        ];

        vi.mocked(api.get).mockResolvedValueOnce(mockSessions);

        const { result } = renderHook(() => useQuizSessions(5));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(api.get).toHaveBeenCalledWith(
            '/sessions/',
            'mock-access-token',
            { quiz_id: 5, limit: 10 }
        );
    });

    it('should handle empty sessions array', async () => {
        vi.mocked(api.get).mockResolvedValueOnce([]);

        const { result } = renderHook(() => useQuizSessions(5, 10));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.sessions).toEqual([]);
        expect(result.current.error).toBe(null);
    });

    it('should support refetch functionality', async () => {
        const mockSessions = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'test' as const,
                started_at: '2025-10-11T10:00:00.000Z',
                completed_at: '2025-10-11T10:30:00.000Z',
                score: 90.0,
            },
        ];

        vi.mocked(api.get).mockResolvedValue(mockSessions);

        const { result } = renderHook(() => useQuizSessions(5, 10));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(api.get).toHaveBeenCalledTimes(1);

        // Call refetch
        result.current.refetch();

        await waitFor(() => {
            expect(api.get).toHaveBeenCalledTimes(2);
        });
    });

    it('should handle different limit parameter values', async () => {
        const mockSessions = Array.from({ length: 50 }, (_, i) => ({
            id: i + 1,
            user_id: 1,
            quiz_id: 5,
            mode: (i % 2 === 0 ? 'test' : 'learn') as 'test' | 'learn',
            started_at: `2025-10-${String(11 - Math.floor(i / 2)).padStart(2, '0')}T10:00:00.000Z`,
            completed_at: `2025-10-${String(11 - Math.floor(i / 2)).padStart(2, '0')}T10:30:00.000Z`,
            score: i % 2 === 0 ? 80 + i : null,
        }));

        vi.mocked(api.get).mockResolvedValueOnce(mockSessions);

        const { result } = renderHook(() => useQuizSessions(5, 50));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(api.get).toHaveBeenCalledWith(
            '/sessions/',
            'mock-access-token',
            { quiz_id: 5, limit: 50 }
        );
        expect(result.current.sessions).toHaveLength(50);
    });

    it('should handle sessions with null scores (learn mode)', async () => {
        const mockSessions = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'learn' as const,
                started_at: '2025-10-11T10:00:00.000Z',
                completed_at: '2025-10-11T10:30:00.000Z',
                score: null,
            },
            {
                id: 2,
                user_id: 1,
                quiz_id: 5,
                mode: 'learn' as const,
                started_at: '2025-10-10T14:00:00.000Z',
                completed_at: '2025-10-10T14:45:00.000Z',
                score: null,
            },
        ];

        vi.mocked(api.get).mockResolvedValueOnce(mockSessions);

        const { result } = renderHook(() => useQuizSessions(5, 10));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.sessions).toEqual(mockSessions);
        expect(result.current.sessions?.every(s => s.score === null)).toBe(true);
    });

    it('should handle incomplete sessions (no completed_at)', async () => {
        const mockSessions = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'test' as const,
                started_at: '2025-10-11T10:00:00.000Z',
                completed_at: null,
                score: null,
            },
        ];

        vi.mocked(api.get).mockResolvedValueOnce(mockSessions);

        const { result } = renderHook(() => useQuizSessions(5, 10));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.sessions).toEqual(mockSessions);
        expect(result.current.sessions?.[0].completed_at).toBe(null);
    });

    it('should handle mixed test and learn sessions', async () => {
        const mockSessions = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'test' as const,
                started_at: '2025-10-11T10:00:00.000Z',
                completed_at: '2025-10-11T10:30:00.000Z',
                score: 92.5,
            },
            {
                id: 2,
                user_id: 1,
                quiz_id: 5,
                mode: 'learn' as const,
                started_at: '2025-10-10T14:00:00.000Z',
                completed_at: '2025-10-10T14:45:00.000Z',
                score: null,
            },
            {
                id: 3,
                user_id: 1,
                quiz_id: 5,
                mode: 'test' as const,
                started_at: '2025-10-09T09:00:00.000Z',
                completed_at: '2025-10-09T09:25:00.000Z',
                score: 88.0,
            },
        ];

        vi.mocked(api.get).mockResolvedValueOnce(mockSessions);

        const { result } = renderHook(() => useQuizSessions(5, 10));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.sessions).toEqual(mockSessions);
        const testSessions = result.current.sessions?.filter(s => s.mode === 'test');
        const learnSessions = result.current.sessions?.filter(s => s.mode === 'learn');
        expect(testSessions).toHaveLength(2);
        expect(learnSessions).toHaveLength(1);
    });
});
