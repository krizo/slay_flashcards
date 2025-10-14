import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useCurrentUser, useUserStats, useRecentSessions, useProgressData } from './useDashboardData';
import * as apiClient from '../services/apiClient';

// Mock the apiClient module
vi.mock('../services/apiClient', () => ({
    apiClient: vi.fn(),
}));

// Mock the AuthContext module
vi.mock('../context/AuthContext', () => ({
    useAuth: () => ({
        accessToken: 'mock-access-token',
        user: null,
        isLoading: false,
        isAuthenticated: true,
        login: vi.fn(),
        register: vi.fn(),
        logout: vi.fn(),
    }),
}));

describe('useDashboardData hooks', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.resetAllMocks();
    });

    describe('useCurrentUser', () => {
        it('should fetch and return user data successfully', async () => {
            const mockUser = {
                id: 1,
                name: 'Emila',
                email: 'emila@test.com',
                created_at: '2025-10-08T10:00:00Z',
            };

            vi.mocked(apiClient.apiClient).mockResolvedValueOnce(mockUser);

            const { result } = renderHook(() => useCurrentUser());

            expect(result.current.isLoading).toBe(true);
            expect(result.current.data).toBe(null);

            await waitFor(() => {
                expect(result.current.isLoading).toBe(false);
            });

            expect(result.current.data).toEqual(mockUser);
            expect(result.current.error).toBe(null);
            expect(apiClient.apiClient).toHaveBeenCalledWith('/auth/me', undefined, 'mock-access-token');
        });

        it('should handle error when fetching user fails', async () => {
            const mockError = new Error('Failed to fetch user');
            vi.mocked(apiClient.apiClient).mockRejectedValueOnce(mockError);

            const { result } = renderHook(() => useCurrentUser());

            await waitFor(() => {
                expect(result.current.isLoading).toBe(false);
            });

            expect(result.current.data).toBe(null);
            expect(result.current.error).toEqual(mockError);
        });
    });

    describe('useUserStats', () => {
        it('should fetch and return user statistics', async () => {
            const mockStats = {
                total_sessions: 58,
                learn_sessions: 41,
                test_sessions: 17,
                average_score: 82.88,
                best_score: 97,
                study_streak: 15,
                favorite_subjects: [],
                sessions_this_week: 29,
                sessions_this_month: 58,
                unique_quizzes: 12,
            };

            vi.mocked(apiClient.apiClient).mockResolvedValueOnce(mockStats);

            const { result } = renderHook(() => useUserStats(1));

            expect(result.current.isLoading).toBe(true);

            await waitFor(() => {
                expect(result.current.isLoading).toBe(false);
            });

            expect(result.current.data).toEqual(mockStats);
            expect(result.current.error).toBe(null);
            expect(apiClient.apiClient).toHaveBeenCalledWith('/users/1/statistics', undefined, 'mock-access-token');
        });

        it('should handle error when fetching stats fails', async () => {
            const mockError = new Error('Failed to fetch statistics');
            vi.mocked(apiClient.apiClient).mockRejectedValueOnce(mockError);

            const { result } = renderHook(() => useUserStats(1));

            await waitFor(() => {
                expect(result.current.isLoading).toBe(false);
            });

            expect(result.current.data).toBe(null);
            expect(result.current.error).toEqual(mockError);
        });
    });

    describe('useRecentSessions', () => {
        it('should fetch and return recent sessions', async () => {
            // Mock sessions with quiz details included (backend now returns these fields)
            const mockSessions = [
                {
                    id: 1,
                    user_id: 1,
                    quiz_id: 7,
                    mode: 'test' as const,
                    started_at: '2025-10-08T08:38:52Z',
                    score: 75,
                    completed_at: '2025-10-08T09:00:52Z',
                    quiz_name: 'Test Quiz',
                    quiz_category: 'Algebra',
                    quiz_level: 'Intermediate',
                },
            ];

            // Mock single API call: sessions endpoint now includes quiz details
            vi.mocked(apiClient.apiClient).mockResolvedValueOnce(mockSessions);

            const { result } = renderHook(() => useRecentSessions(1, 5));

            expect(result.current.isLoading).toBe(true);

            await waitFor(() => {
                expect(result.current.isLoading).toBe(false);
            });

            expect(result.current.data).toEqual(mockSessions);
            expect(result.current.error).toBe(null);
            expect(apiClient.apiClient).toHaveBeenCalledWith('/sessions/user/1/recent?limit=5', undefined, 'mock-access-token');
            // No longer fetching quizzes separately
            expect(apiClient.apiClient).toHaveBeenCalledTimes(1);
        });
    });

    describe('useProgressData', () => {
        it('should fetch and transform progress data correctly', async () => {
            const mockApiResponse = {
                total_sessions: 29,
                learn_sessions: 22,
                test_sessions: 7,
                days_analyzed: 7,
                quiz_filter: null,
                daily_activity: {
                    '2025-10-08': {
                        learn_sessions: 1,
                        test_sessions: 1,
                        scores: [75],
                        average_score: 75.0,
                    },
                    '2025-10-07': {
                        learn_sessions: 2,
                        test_sessions: 1,
                        scores: [92],
                        average_score: 92.0,
                    },
                },
            };

            vi.mocked(apiClient.apiClient).mockResolvedValueOnce(mockApiResponse);

            const { result } = renderHook(() => useProgressData(1, 7));

            await waitFor(() => {
                expect(result.current.isLoading).toBe(false);
            });

            expect(result.current.data).toHaveLength(2);
            expect(result.current.data).toEqual([
                { date: '2025-10-07', score: 92.0 },
                { date: '2025-10-08', score: 75.0 },
            ]);
            expect(result.current.error).toBe(null);
        });

        it('should filter out days with null or empty scores', async () => {
            const mockApiResponse = {
                total_sessions: 2,
                learn_sessions: 2,
                test_sessions: 0,
                days_analyzed: 7,
                quiz_filter: null,
                daily_activity: {
                    '2025-10-08': {
                        learn_sessions: 2,
                        test_sessions: 0,
                        scores: [],
                        average_score: null,
                    },
                },
            };

            vi.mocked(apiClient.apiClient).mockResolvedValueOnce(mockApiResponse);

            const { result } = renderHook(() => useProgressData(1, 7));

            await waitFor(() => {
                expect(result.current.isLoading).toBe(false);
            });

            // Days with no test scores should be filtered out
            expect(result.current.data).toEqual([]);
        });
    });
});
