import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import QuizDetailsPanel from './QuizDetailsPanel';
import * as useQuizHook from '../../hooks/useQuiz';
import * as useQuizPerformanceHook from '../../hooks/useQuizPerformance';
import * as useQuizSessionsHook from '../../hooks/useQuizSessions';
import { Quiz } from '../../types';

// Mock the hooks
vi.mock('../../hooks/useQuiz');
vi.mock('../../hooks/useQuizPerformance');
vi.mock('../../hooks/useQuizSessions');

// Mock the AuthContext
vi.mock('../../context/AuthContext', () => ({
    useAuth: () => ({
        accessToken: 'mock-access-token',
        user: { id: 1, name: 'TestUser', email: 'test@example.com', created_at: '2025-10-08T10:00:00Z' },
        isLoading: false,
        isAuthenticated: true,
        login: vi.fn(),
        register: vi.fn(),
        logout: vi.fn(),
    }),
}));

// Mock Recharts
vi.mock('recharts', () => ({
    LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
    Line: () => <div data-testid="line" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
}));

// Mock fetch for export functionality
global.fetch = vi.fn();

describe('QuizDetailsPanel', () => {
    const mockQuiz: Quiz = {
        id: 1,
        name: 'Test Quiz',
        subject: 'Mathematics',
        description: 'A comprehensive test quiz for algebra',
        category: 'Algebra',
        level: 'Intermediate',
        user_id: 1,
        flashcard_count: 25,
        created_at: '2025-10-01T10:00:00Z',
        updated_at: '2025-10-05T15:30:00Z',
    };

    const mockPerformance = {
        quiz_id: 1,
        quiz_name: 'Test Quiz',
        total_sessions: 15,
        test_sessions: 8,
        learn_sessions: 7,
        unique_users: 1,
        days_analyzed: 30,
        scores: {
            average: 85.5,
            highest: 95.0,
            lowest: 70.0,
            distribution: {
                '90-100': 3,
                '80-89': 4,
                '70-79': 1,
                '60-69': 0,
                '50-59': 0,
                '0-49': 0,
            },
        },
        activity_trend: {
            '2025-10-01': { sessions: 2, average_score: 80.0 },
            '2025-10-02': { sessions: 1, average_score: 85.0 },
            '2025-10-03': { sessions: 3, average_score: 90.0 },
            '2025-10-05': { sessions: 2, average_score: 88.0 },
            '2025-10-06': { sessions: 1, average_score: 92.0 },
        },
    };

    const mockSessions = [
        {
            id: 1,
            quiz_id: 1,
            user_id: 1,
            mode: 'test' as const,
            score: 92.0,
            started_at: '2025-10-10T14:00:00Z',
            completed_at: '2025-10-10T14:30:00Z',
        },
        {
            id: 2,
            quiz_id: 1,
            user_id: 1,
            mode: 'learn' as const,
            score: null,
            started_at: '2025-10-09T10:00:00Z',
            completed_at: '2025-10-09T10:45:00Z',
        },
    ];

    const mockHandlers = {
        onEditClick: vi.fn(),
        onDeleteClick: vi.fn(),
        onStartLearningSession: vi.fn(),
        onStartTestSession: vi.fn(),
    };

    beforeEach(() => {
        vi.clearAllMocks();

        // Default mock implementations
        vi.mocked(useQuizHook.useQuiz).mockReturnValue({
            quiz: mockQuiz,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        });

        vi.mocked(useQuizPerformanceHook.useQuizPerformance).mockReturnValue({
            performance: mockPerformance,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        });

        vi.mocked(useQuizSessionsHook.useQuizSessions).mockReturnValue({
            sessions: mockSessions,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        });

        // Mock window methods
        window.alert = vi.fn();
        global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
        global.URL.revokeObjectURL = vi.fn();
    });

    describe('Empty State', () => {
        it('shows empty state when no quiz is selected', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={null}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('No Quiz Selected')).toBeInTheDocument();
            expect(screen.getByText(/Select a quiz from the list to view details/i)).toBeInTheDocument();
        });

        it('displays empty state icon', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={null}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('📚')).toBeInTheDocument();
        });
    });

    describe('Loading State', () => {
        it('shows loading state when quiz is loading', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: null,
                isLoading: true,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('Loading quiz details...')).toBeInTheDocument();
        });

        it('shows loading spinner for statistics when performance is loading', () => {
            vi.mocked(useQuizPerformanceHook.useQuizPerformance).mockReturnValue({
                performance: null,
                isLoading: true,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('Loading statistics...')).toBeInTheDocument();
        });
    });

    describe('Error State', () => {
        it('shows error message when quiz fails to load', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: null,
                isLoading: false,
                error: new Error('Failed to fetch quiz'),
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('Failed to load quiz details: Failed to fetch quiz')).toBeInTheDocument();
        });
    });

    describe('Quiz Header Display', () => {
        it('displays quiz name and icon', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('Test Quiz')).toBeInTheDocument();
            expect(screen.getByText('📚')).toBeInTheDocument();
        });

        it('displays created date in correct format', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText(/Created Oct 1, 2025/)).toBeInTheDocument();
        });

        it('displays all badges (subject, category, level, cards)', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('Mathematics')).toBeInTheDocument();
            expect(screen.getByText('Algebra')).toBeInTheDocument();
            expect(screen.getByText('Intermediate')).toBeInTheDocument();
            expect(screen.getByText('25 cards')).toBeInTheDocument();
        });

        it('displays quiz description in italic', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            const description = screen.getByText('A comprehensive test quiz for algebra');
            expect(description).toBeInTheDocument();
            expect(description).toHaveClass('quiz-compact-description-inline');
        });

        it('does not show category badge when category is null', () => {
            const quizWithoutCategory = { ...mockQuiz, category: null };
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: quizWithoutCategory,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.queryByText('Algebra')).not.toBeInTheDocument();
        });
    });

    describe('Action Buttons', () => {
        it('renders all five action buttons', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByRole('button', { name: /learn/i })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: /test/i })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument();
        });

        it('calls onStartLearningSession when Learn button is clicked', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            fireEvent.click(screen.getByRole('button', { name: /learn/i }));
            expect(mockHandlers.onStartLearningSession).toHaveBeenCalledWith(1);
        });

        it('calls onStartTestSession when Test button is clicked', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            fireEvent.click(screen.getByRole('button', { name: /test/i }));
            expect(mockHandlers.onStartTestSession).toHaveBeenCalledWith(1);
        });

        it('calls onEditClick when Edit button is clicked', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            fireEvent.click(screen.getByRole('button', { name: /edit/i }));
            expect(mockHandlers.onEditClick).toHaveBeenCalledWith(1);
        });

        it('calls onDeleteClick when Delete button is clicked', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            fireEvent.click(screen.getByRole('button', { name: /delete/i }));
            expect(mockHandlers.onDeleteClick).toHaveBeenCalledWith(1);
        });
    });

    describe('Statistics Display', () => {
        it('displays all 8 statistics cards', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('Total Sessions')).toBeInTheDocument();
            expect(screen.getByText('Latest Score')).toBeInTheDocument();
            expect(screen.getByText('Max Score')).toBeInTheDocument();
            expect(screen.getByText('Min Score')).toBeInTheDocument();
            expect(screen.getByText('Avg Score')).toBeInTheDocument();
            expect(screen.getByText('Days Active')).toBeInTheDocument();
            expect(screen.getByText('Peak Score')).toBeInTheDocument();
            expect(screen.getByText('Best Streak')).toBeInTheDocument();
        });

        it('displays correct total sessions count', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('15')).toBeInTheDocument();
        });

        it('displays latest score from most recent test session', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            const latestScoreCard = screen.getByText('Latest Score').parentElement;
            expect(latestScoreCard).toHaveTextContent('92%');
        });

        it('displays average score rounded to integer', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('86%')).toBeInTheDocument(); // 85.5 rounded to 86
        });

        it('displays max and min scores', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('95%')).toBeInTheDocument();
            expect(screen.getByText('70%')).toBeInTheDocument();
        });

        it('displays days active count from activity trend', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('5')).toBeInTheDocument(); // 5 days in activity_trend
        });

        it('displays em dash when no latest score available', () => {
            vi.mocked(useQuizSessionsHook.useQuizSessions).mockReturnValue({
                sessions: [],
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            const statCards = screen.getAllByText('—');
            expect(statCards.length).toBeGreaterThan(0);
        });
    });

    describe('Best Streak Calculation', () => {
        it('calculates best streak correctly for consecutive days', () => {
            const performanceWithStreak = {
                ...mockPerformance,
                activity_trend: {
                    '2025-10-01': { sessions: 1, average_score: 80.0 },
                    '2025-10-02': { sessions: 1, average_score: 85.0 },
                    '2025-10-03': { sessions: 1, average_score: 90.0 },
                },
            };

            vi.mocked(useQuizPerformanceHook.useQuizPerformance).mockReturnValue({
                performance: performanceWithStreak,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            const bestStreakCard = screen.getByText('Best Streak').parentElement;
            expect(bestStreakCard).toHaveTextContent('3'); // 3-day streak
        });

        it('shows em dash when no streak data available', () => {
            vi.mocked(useQuizPerformanceHook.useQuizPerformance).mockReturnValue({
                performance: { ...mockPerformance, activity_trend: {} },
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            const bestStreakSection = screen.getByText('Best Streak').parentElement;
            expect(bestStreakSection).toHaveTextContent('—');
        });
    });

    describe('Peak Score Calculation', () => {
        it('displays peak score with rounded value', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            const peakScoreCard = screen.getByText('Peak Score').parentElement;
            expect(peakScoreCard).toHaveTextContent('92%'); // Peak from activity trend
        });

        it('shows em dash when no peak score available', () => {
            vi.mocked(useQuizPerformanceHook.useQuizPerformance).mockReturnValue({
                performance: { ...mockPerformance, activity_trend: {} },
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            const peakScoreSection = screen.getByText('Peak Score').parentElement;
            expect(peakScoreSection).toHaveTextContent('—');
        });
    });

    describe('Activity Trend Chart', () => {
        it('renders line chart when activity data is available', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('Activity Trend')).toBeInTheDocument();
            expect(screen.getByTestId('line-chart')).toBeInTheDocument();
        });

        it('shows placeholder when no activity data available', () => {
            vi.mocked(useQuizPerformanceHook.useQuizPerformance).mockReturnValue({
                performance: { ...mockPerformance, activity_trend: {} },
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('No session data available yet')).toBeInTheDocument();
            expect(screen.getByText(/Start a learning session to see your progress/i)).toBeInTheDocument();
        });
    });

    describe('Session Distribution Chart', () => {
        it('displays session distribution bar chart', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('Session Distribution')).toBeInTheDocument();
            expect(screen.getByText('Learn vs Test sessions')).toBeInTheDocument();
        });

        it('shows correct learn and test session counts in legend', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText(/Learn \(7\)/)).toBeInTheDocument();
            expect(screen.getByText(/Test \(8\)/)).toBeInTheDocument();
        });

        it('shows placeholder when no sessions available', () => {
            vi.mocked(useQuizPerformanceHook.useQuizPerformance).mockReturnValue({
                performance: { ...mockPerformance, total_sessions: 0 },
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(screen.getByText('No session data available yet')).toBeInTheDocument();
        });
    });

    describe('Export Functionality', () => {
        afterEach(() => {
            vi.restoreAllMocks();
        });

        it('calls fetch with correct parameters when export button is clicked', async () => {
            const mockBlob = new Blob(['test'], { type: 'application/json' });
            vi.mocked(fetch).mockResolvedValue({
                ok: true,
                blob: () => Promise.resolve(mockBlob),
            } as Response);

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            fireEvent.click(screen.getByRole('button', { name: /export/i }));

            await waitFor(() => {
                expect(fetch).toHaveBeenCalledWith('/api/v1/quizzes/1/export', {
                    headers: {
                        'Authorization': 'Bearer mock-access-token',
                    },
                });
            });
        });

        it('triggers download when export is successful', async () => {
            const mockBlob = new Blob(['test'], { type: 'application/json' });
            vi.mocked(fetch).mockResolvedValue({
                ok: true,
                blob: () => Promise.resolve(mockBlob),
            } as Response);

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            const mockClick = vi.fn();
            const mockAnchor = document.createElement('a');
            mockAnchor.click = mockClick;

            const mockAppendChild = vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockAnchor);
            const mockRemoveChild = vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockAnchor);

            const originalCreateElement = document.createElement;
            vi.spyOn(document, 'createElement').mockImplementation(function(this: Document, tagName: string) {
                if (tagName === 'a') {
                    return mockAnchor;
                }
                return originalCreateElement.call(this, tagName as any);
            });

            fireEvent.click(screen.getByRole('button', { name: /export/i }));

            await waitFor(() => {
                expect(mockClick).toHaveBeenCalled();
                expect(global.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
                expect(global.URL.revokeObjectURL).toHaveBeenCalled();
                expect(mockAppendChild).toHaveBeenCalled();
                expect(mockRemoveChild).toHaveBeenCalled();
            });
        });

        it('shows alert when export fails', async () => {
            vi.mocked(fetch).mockResolvedValue({
                ok: false,
            } as Response);

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            fireEvent.click(screen.getByRole('button', { name: /export/i }));

            await waitFor(() => {
                expect(window.alert).toHaveBeenCalledWith('Failed to export quiz. Please try again.');
            });
        });

        it('disables export button while exporting', async () => {
            const mockBlob = new Blob(['test'], { type: 'application/json' });
            vi.mocked(fetch).mockResolvedValue({
                ok: true,
                blob: () => Promise.resolve(mockBlob),
            } as Response);

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            const mockClick = vi.fn();
            const mockAnchor = document.createElement('a');
            mockAnchor.click = mockClick;

            vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockAnchor);
            vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockAnchor);

            const originalCreateElement = document.createElement;
            vi.spyOn(document, 'createElement').mockImplementation(function(this: Document, tagName: string) {
                if (tagName === 'a') {
                    return mockAnchor;
                }
                return originalCreateElement.call(this, tagName as any);
            });

            const exportButton = screen.getByRole('button', { name: /export/i });
            fireEvent.click(exportButton);

            // Button should be disabled during export
            expect(exportButton).toBeDisabled();

            await waitFor(() => {
                expect(exportButton).not.toBeDisabled();
            });
        });
    });

    describe('Hook Integration', () => {
        it('calls useQuiz with selected quiz ID', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(useQuizHook.useQuiz).toHaveBeenCalledWith(1);
        });

        it('calls useQuizPerformance with selected quiz ID and 30 days', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(useQuizPerformanceHook.useQuizPerformance).toHaveBeenCalledWith(1, 30);
        });

        it('calls useQuizSessions with selected quiz ID and limit 50', () => {
            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            expect(useQuizSessionsHook.useQuizSessions).toHaveBeenCalledWith(1, 50);
        });
    });

    describe('Responsive Date Formatting', () => {
        it('formats relative dates correctly', () => {
            const recentSession = {
                ...mockSessions[0],
                started_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
            };

            vi.mocked(useQuizSessionsHook.useQuizSessions).mockReturnValue({
                sessions: [recentSession],
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            render(
                <QuizDetailsPanel
                    selectedQuizId={1}
                    {...mockHandlers}
                />
            );

            // The relative date appears in the Latest Score stat card
            const latestScoreCard = screen.getByText('Latest Score').parentElement;
            expect(latestScoreCard).toHaveTextContent('2d ago');
        });
    });
});
