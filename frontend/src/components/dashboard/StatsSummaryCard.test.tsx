import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import StatsSummaryCard from './StatsSummaryCard';
import { UserStats, Session } from '../../types';

// Helper function to render with user event
const renderWithUser = (component: React.ReactElement) => {
    return {
        user: userEvent.setup(),
        ...render(component),
    };
};

describe('StatsSummaryCard', () => {
    const mockOnTimePeriodChange = vi.fn();
    const mockStats: UserStats = {
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

    const mockSessions: Session[] = [
        {
            id: 1,
            user_id: 1,
            quiz_id: 7,
            mode: 'test',
            started_at: '2025-10-08T08:38:52Z',
            score: 75,
            completed_at: '2025-10-08T09:00:52Z',
            completed: true,
            quiz_name: 'JavaScript Basics',
        },
        {
            id: 2,
            user_id: 1,
            quiz_id: 5,
            mode: 'learn',
            started_at: '2025-10-07T10:20:00Z',
            score: null,
            completed_at: '2025-10-07T10:45:00Z',
            completed: true,
            quiz_name: 'Python Fundamentals',
        },
    ];

    const mockSessionsData = [
        { date: '2025-10-04', learn: 2, test: 1 },
        { date: '2025-10-05', learn: 1, test: 0 },
        { date: '2025-10-06', learn: 3, test: 2 },
        { date: '2025-10-07', learn: 0, test: 1 },
        { date: '2025-10-08', learn: 2, test: 0 },
        { date: '2025-10-09', learn: 1, test: 1 },
        { date: '2025-10-10', learn: 2, test: 3 },
    ];

    const mockProgressData = [
        { date: '2025-10-02', score: 75 },
        { date: '2025-10-03', score: 78 },
        { date: '2025-10-04', score: 80 },
        { date: '2025-10-05', score: 82 },
        { date: '2025-10-06', score: 79 },
        { date: '2025-10-07', score: 85 },
        { date: '2025-10-08', score: 88 },
    ];

    it('renders loading state', () => {
        render(<StatsSummaryCard stats={null} isLoading={true} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        expect(screen.getByText('Loading statistics...')).toBeInTheDocument();
    });

    it('renders error state', () => {
        const error = new Error('API connection failed');
        render(<StatsSummaryCard stats={null} error={error} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        expect(screen.getByText('Failed to load statistics')).toBeInTheDocument();
        expect(screen.getByText('API connection failed')).toBeInTheDocument();
    });

    it('renders empty state when no stats provided', () => {
        render(<StatsSummaryCard stats={null} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        expect(screen.getByText('No statistics available')).toBeInTheDocument();
    });

    it('renders user statistics correctly', () => {
        render(<StatsSummaryCard stats={mockStats} userName="Emila" recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        // Check welcome message
        expect(screen.getByText('Welcome back, Emila! 👋')).toBeInTheDocument();

        // Check stats values (using getAllByText for duplicates)
        const totalSessionsElements = screen.getAllByText('58');
        expect(totalSessionsElements.length).toBeGreaterThanOrEqual(1); // Total sessions (and recent activity)

        expect(screen.getByText('83%')).toBeInTheDocument(); // Average score (rounded)

        // "15" appears twice: for Study Streak and Days Active (both same in 'all' mode)
        const fifteenElements = screen.getAllByText('15');
        expect(fifteenElements.length).toBe(2);

        expect(screen.getByText('97%')).toBeInTheDocument(); // Best score
        expect(screen.getByText('41')).toBeInTheDocument(); // Learn sessions
        expect(screen.getByText('17')).toBeInTheDocument(); // Test sessions
        expect(screen.getByText('12')).toBeInTheDocument(); // Unique quizzes

        // Check calculated stats
        expect(screen.getByText('75%')).toBeInTheDocument(); // Latest score
        expect(screen.getByText('69%')).toBeInTheDocument(); // Min score (estimated: 97 - (97-83)*2 = 69)
        expect(screen.getByText('1.9')).toBeInTheDocument(); // Daily average (58/30)
    });

    it('renders with default user name when not provided', () => {
        render(<StatsSummaryCard stats={mockStats} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        expect(screen.getByText('Welcome back, User! 👋')).toBeInTheDocument();
    });

    it('displays — for null average score', () => {
        const statsWithNullAverage = { ...mockStats, average_score: null };
        render(<StatsSummaryCard stats={statsWithNullAverage} recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        // Now displays just "—" without "%" when value is null
        const dashElements = screen.getAllByText('—');
        expect(dashElements.length).toBeGreaterThan(0);
    });

    it('displays — for null best score', () => {
        const statsWithNullBest = { ...mockStats, best_score: null };
        render(<StatsSummaryCard stats={statsWithNullBest} recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        // Should have "—%" for best score and min score (which depends on best score)
        const dashElements = screen.getAllByText('—');
        expect(dashElements.length).toBeGreaterThan(0);
    });

    it('renders all stat labels correctly', () => {
        render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        // Row 1: Session Overview
        expect(screen.getByText('Total Sessions')).toBeInTheDocument();
        expect(screen.getByText('Learn Sessions')).toBeInTheDocument();
        expect(screen.getByText('Test Sessions')).toBeInTheDocument();
        expect(screen.getByText('Unique Quizzes')).toBeInTheDocument();

        // Row 2: Performance Metrics (Latest Score swapped with Study Streak)
        expect(screen.getByText('Average Score')).toBeInTheDocument();
        expect(screen.getByText('Best Score')).toBeInTheDocument();
        expect(screen.getByText('Latest Score')).toBeInTheDocument();
        expect(screen.getByText('Study Streak')).toBeInTheDocument();

        // Row 3: Recent Activity
        expect(screen.getByText('Days Active')).toBeInTheDocument();
        expect(screen.getByText('Min Score')).toBeInTheDocument();
        expect(screen.getByText('Recent Activity')).toBeInTheDocument();
        expect(screen.getByText('Daily Average')).toBeInTheDocument();
    });

    it('renders quick actions section', () => {
        render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        expect(screen.getByText('Quick Actions')).toBeInTheDocument();
        expect(screen.getByText('Start Learning')).toBeInTheDocument();
        expect(screen.getByText('Take a Test')).toBeInTheDocument();
        expect(screen.getByText('Create Quiz')).toBeInTheDocument();
    });

    it('rounds decimal scores to integers', () => {
        const statsWithDecimals = {
            ...mockStats,
            average_score: 85.67,
            best_score: 92.34,
        };
        render(<StatsSummaryCard stats={statsWithDecimals} recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        // Should round 85.67 to 86
        expect(screen.getByText('86%')).toBeInTheDocument();
        // Should round 92.34 to 92
        expect(screen.getByText('92%')).toBeInTheDocument();
    });

    it('displays — for latest score when no recent sessions', () => {
        render(<StatsSummaryCard stats={mockStats} recentSessions={null} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        // Should show — for latest score
        const latestScoreValue = screen.getAllByText('—');
        expect(latestScoreValue.length).toBeGreaterThan(0);
    });

    it('displays — for latest score when no test sessions available', () => {
        const learnOnlySessions: Session[] = [
            {
                id: 2,
                user_id: 1,
                quiz_id: 5,
                mode: 'learn',
                started_at: '2025-10-07T10:20:00Z',
                score: null,
                completed_at: '2025-10-07T10:45:00Z',
                completed: true,
                quiz_name: 'Python Fundamentals',
            },
        ];
        render(<StatsSummaryCard stats={mockStats} recentSessions={learnOnlySessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

        // Should show — for latest score since there are no test sessions
        const latestScoreValue = screen.getAllByText('—');
        expect(latestScoreValue.length).toBeGreaterThan(0);
    });

    describe('Time Period Filter', () => {
        it('renders all time period filter buttons', () => {
            render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

            expect(screen.getByText('Week')).toBeInTheDocument();
            expect(screen.getByText('Month')).toBeInTheDocument();
            expect(screen.getByText('Year')).toBeInTheDocument();
            expect(screen.getByText('All Time')).toBeInTheDocument();
        });

        it('defaults to "All Time" period', () => {
            render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);

            const allTimeButton = screen.getByText('All Time');
            expect(allTimeButton).toHaveClass('active');
        });

        it('calls onTimePeriodChange when button is clicked', async () => {
            const mockCallback = vi.fn();
            const { user } = renderWithUser(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockCallback} />);

            const weekButton = screen.getByText('Week');

            // Click Week button
            await user.click(weekButton);

            // Should call callback with 'week'
            expect(mockCallback).toHaveBeenCalledWith('week');
        });

        it('displays correct subtitle for each period', () => {
            // Test 'all' period - shows "all time"
            const { rerender } = render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} sessionsData={mockSessionsData} progressData={mockProgressData} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);
            const allTimeElements = screen.getAllByText('all time');
            expect(allTimeElements.length).toBeGreaterThanOrEqual(1);

            // Test 'week' period
            rerender(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} sessionsData={mockSessionsData} progressData={mockProgressData} timePeriod="week" onTimePeriodChange={mockOnTimePeriodChange} />);
            const lastWeekElements = screen.getAllByText('last week');
            expect(lastWeekElements.length).toBeGreaterThanOrEqual(1);

            // Test 'month' period
            rerender(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} sessionsData={mockSessionsData} progressData={mockProgressData} timePeriod="month" onTimePeriodChange={mockOnTimePeriodChange} />);
            const lastMonthElements = screen.getAllByText('last month');
            expect(lastMonthElements.length).toBeGreaterThanOrEqual(1);

            // Test 'year' period
            rerender(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} sessionsData={mockSessionsData} progressData={mockProgressData} timePeriod="year" onTimePeriodChange={mockOnTimePeriodChange} />);
            const yearElements = screen.getAllByText('last year');
            expect(yearElements.length).toBeGreaterThanOrEqual(1);
        });

        it('calculates Days Active correctly for week period', () => {
            render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="week" onTimePeriodChange={mockOnTimePeriodChange} />);

            // Should show min(sessions_this_week, 7) = min(29, 7) = 7
            const daysActiveElements = screen.getAllByText('7');
            expect(daysActiveElements.length).toBeGreaterThanOrEqual(1);
        });

        it('calculates Days Active correctly for month period', () => {
            render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="month" onTimePeriodChange={mockOnTimePeriodChange} />);

            // Should show min(sessions_this_month, 30) = min(58, 30) = 30
            expect(screen.getByText('30')).toBeInTheDocument();
        });

        it('calculates Days Active correctly for year and all time periods', () => {
            // Year should show study_streak
            render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="year" onTimePeriodChange={mockOnTimePeriodChange} />);
            const yearElements = screen.getAllByText('15');
            expect(yearElements.length).toBe(2); // Study Streak and Days Active both show 15
        });

        it('handles week period with fewer sessions than days', () => {
            const statsWithFewSessions = {
                ...mockStats,
                sessions_this_week: 3,
            };
            render(
                <StatsSummaryCard stats={statsWithFewSessions} recentSessions={mockSessions} timePeriod="week" onTimePeriodChange={mockOnTimePeriodChange} />
            );

            // Should show min(3, 7) = 3 (may appear multiple times)
            const threeElements = screen.getAllByText('3');
            expect(threeElements.length).toBeGreaterThanOrEqual(1);
        });

        it('handles month period with fewer sessions than days', () => {
            const statsWithFewSessions = {
                ...mockStats,
                sessions_this_month: 15,
            };
            render(
                <StatsSummaryCard stats={statsWithFewSessions} recentSessions={mockSessions} timePeriod="month" onTimePeriodChange={mockOnTimePeriodChange} />
            );

            // Should show min(15, 30) = 15
            const fifteenElements = screen.getAllByText('15');
            expect(fifteenElements.length).toBeGreaterThanOrEqual(1);
        });

        it('renders correct active button based on timePeriod prop', () => {
            // Test with 'week'
            const { rerender } = render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="week" onTimePeriodChange={mockOnTimePeriodChange} />);
            expect(screen.getByText('Week')).toHaveClass('active');

            // Test with 'month'
            rerender(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="month" onTimePeriodChange={mockOnTimePeriodChange} />);
            expect(screen.getByText('Month')).toHaveClass('active');
            expect(screen.getByText('Week')).not.toHaveClass('active');

            // Test with 'year'
            rerender(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="year" onTimePeriodChange={mockOnTimePeriodChange} />);
            expect(screen.getByText('Year')).toHaveClass('active');
            expect(screen.getByText('Month')).not.toHaveClass('active');

            // Test with 'all'
            rerender(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} timePeriod="all" onTimePeriodChange={mockOnTimePeriodChange} />);
            expect(screen.getByText('All Time')).toHaveClass('active');
            expect(screen.getByText('Year')).not.toHaveClass('active');
        });
    });
});
