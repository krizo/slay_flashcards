import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useQuizPerformance } from './useQuizPerformance';
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

describe('useQuizPerformance', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.resetAllMocks();
    });

    it('should fetch and return quiz performance data successfully', async () => {
        const mockPerformanceData = {
            quiz_id: 5,
            quiz_name: 'Spanish Vocabulary',
            total_sessions: 25,
            test_sessions: 10,
            learn_sessions: 15,
            unique_users: 1,
            days_analyzed: 30,
            scores: {
                average: 85.5,
                highest: 98.0,
                lowest: 72.0,
                distribution: {
                    '90-100': 5,
                    '80-89': 3,
                    '70-79': 2,
                    '60-69': 0,
                    '50-59': 0,
                    '0-49': 0,
                },
            },
            activity_trend: {
                '2025-10-01': {
                    sessions: 2,
                    average_score: 85.0,
                },
                '2025-10-05': {
                    sessions: 3,
                    average_score: 90.0,
                },
            },
        };

        vi.mocked(api.get).mockResolvedValueOnce(mockPerformanceData);

        const { result } = renderHook(() => useQuizPerformance(5, 30));

        expect(result.current.isLoading).toBe(true);
        expect(result.current.performance).toBe(null);

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.performance).toEqual(mockPerformanceData);
        expect(result.current.error).toBe(null);
        expect(api.get).toHaveBeenCalledWith(
            '/sessions/quiz/5/performance',
            'mock-access-token',
            { days: 30 }
        );
    });

    it('should handle error when fetching performance data fails', async () => {
        const mockError = new Error('Failed to fetch quiz performance');
        vi.mocked(api.get).mockRejectedValueOnce(mockError);

        const { result } = renderHook(() => useQuizPerformance(5, 30));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.performance).toBe(null);
        expect(result.current.error).toEqual(mockError);
    });

    it('should not fetch when quizId is null', async () => {
        const { result } = renderHook(() => useQuizPerformance(null, 30));

        expect(result.current.isLoading).toBe(false);
        expect(result.current.performance).toBe(null);
        expect(result.current.error).toBe(null);
        expect(api.get).not.toHaveBeenCalled();
    });

    it('should use default days parameter of 30 when not provided', async () => {
        const mockPerformanceData = {
            quiz_id: 5,
            quiz_name: 'Test Quiz',
            total_sessions: 10,
            test_sessions: 5,
            learn_sessions: 5,
            unique_users: 1,
            days_analyzed: 30,
            scores: {
                average: 80.0,
                highest: 90.0,
                lowest: 70.0,
                distribution: {
                    '90-100': 1,
                    '80-89': 2,
                    '70-79': 2,
                    '60-69': 0,
                    '50-59': 0,
                    '0-49': 0,
                },
            },
            activity_trend: {},
        };

        vi.mocked(api.get).mockResolvedValueOnce(mockPerformanceData);

        const { result } = renderHook(() => useQuizPerformance(5));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(api.get).toHaveBeenCalledWith(
            '/sessions/quiz/5/performance',
            'mock-access-token',
            { days: 30 }
        );
    });

    it('should handle performance data with null scores', async () => {
        const mockPerformanceData = {
            quiz_id: 5,
            quiz_name: 'New Quiz',
            total_sessions: 5,
            test_sessions: 0,
            learn_sessions: 5,
            unique_users: 1,
            days_analyzed: 30,
            scores: {
                average: null,
                highest: null,
                lowest: null,
                distribution: {
                    '90-100': 0,
                    '80-89': 0,
                    '70-79': 0,
                    '60-69': 0,
                    '50-59': 0,
                    '0-49': 0,
                },
            },
            activity_trend: {},
        };

        vi.mocked(api.get).mockResolvedValueOnce(mockPerformanceData);

        const { result } = renderHook(() => useQuizPerformance(5, 30));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.performance?.scores.average).toBe(null);
        expect(result.current.performance?.scores.highest).toBe(null);
        expect(result.current.performance?.scores.lowest).toBe(null);
    });

    it('should support refetch functionality', async () => {
        const mockPerformanceData = {
            quiz_id: 5,
            quiz_name: 'Test Quiz',
            total_sessions: 10,
            test_sessions: 5,
            learn_sessions: 5,
            unique_users: 1,
            days_analyzed: 30,
            scores: {
                average: 80.0,
                highest: 90.0,
                lowest: 70.0,
                distribution: {
                    '90-100': 1,
                    '80-89': 2,
                    '70-79': 2,
                    '60-69': 0,
                    '50-59': 0,
                    '0-49': 0,
                },
            },
            activity_trend: {},
        };

        vi.mocked(api.get).mockResolvedValue(mockPerformanceData);

        const { result } = renderHook(() => useQuizPerformance(5, 30));

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

    it('should handle different days parameter values', async () => {
        const mockPerformanceData = {
            quiz_id: 5,
            quiz_name: 'Test Quiz',
            total_sessions: 50,
            test_sessions: 25,
            learn_sessions: 25,
            unique_users: 1,
            days_analyzed: 365,
            scores: {
                average: 85.0,
                highest: 95.0,
                lowest: 75.0,
                distribution: {
                    '90-100': 10,
                    '80-89': 10,
                    '70-79': 5,
                    '60-69': 0,
                    '50-59': 0,
                    '0-49': 0,
                },
            },
            activity_trend: {},
        };

        vi.mocked(api.get).mockResolvedValueOnce(mockPerformanceData);

        const { result } = renderHook(() => useQuizPerformance(5, 365));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(api.get).toHaveBeenCalledWith(
            '/sessions/quiz/5/performance',
            'mock-access-token',
            { days: 365 }
        );
        expect(result.current.performance?.days_analyzed).toBe(365);
    });

    it('should handle empty activity trend', async () => {
        const mockPerformanceData = {
            quiz_id: 5,
            quiz_name: 'Test Quiz',
            total_sessions: 5,
            test_sessions: 2,
            learn_sessions: 3,
            unique_users: 1,
            days_analyzed: 30,
            scores: {
                average: 80.0,
                highest: 85.0,
                lowest: 75.0,
                distribution: {
                    '90-100': 0,
                    '80-89': 2,
                    '70-79': 0,
                    '60-69': 0,
                    '50-59': 0,
                    '0-49': 0,
                },
            },
            activity_trend: {},
        };

        vi.mocked(api.get).mockResolvedValueOnce(mockPerformanceData);

        const { result } = renderHook(() => useQuizPerformance(5, 30));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.performance?.activity_trend).toEqual({});
    });
});
